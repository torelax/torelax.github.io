"""Local-only, explicit opt-in export through the configured EvoMyn MCP client."""
import argparse
import asyncio
import json
import os
from pathlib import Path
import re
import tempfile
import tomllib

ROOT = Path(__file__).resolve().parents[1]


def project_record(record, selected):
    allowed = {'title', 'body', 'occurrence_date'}
    include = selected.get('include', [])
    if not isinstance(include, list) or not {'title', 'body'}.issubset(include) or not set(include).issubset(allowed):
        raise ValueError('Select title and body explicitly; only occurrence_date is additionally allowed.')
    slug = selected.get('slug', '')
    if not isinstance(slug, str) or not re.fullmatch(r'[a-z0-9]+(?:-[a-z0-9]+)*', slug):
        raise ValueError('Invalid publication slug.')
    if not all(isinstance(record.get(key), str) and record[key].strip() for key in ('title', 'body')):
        raise ValueError('Selected record has no text title/body; export aborted.')
    article = {'slug': slug, 'title': record['title'], 'category': selected.get('category', '文章'),
               'summary': selected.get('summary', ''), 'blocks': [{'type': 'p', 'text': record['body']}]}
    value = record.get('date', record.get('occurrence_date'))
    if 'occurrence_date' in include and value:
        if not isinstance(value, str) or not re.fullmatch(r'\d{4}(?:-\d{2})?(?:-\d{2})?', value):
            raise ValueError('Unsupported occurrence date; export aborted.')
        article['date'] = value
    return article


async def fetch_selected(items, config):
    from mcp import ClientSession, StdioServerParameters
    from mcp.client.stdio import stdio_client
    settings = tomllib.loads(config.read_text('utf-8'))['mcp_servers']['evomyn']
    if not settings.get('enabled', True):
        raise ValueError('EvoMyn is disabled in the Codex configuration.')
    if not settings.get('command') or 'url' in settings:
        raise ValueError('This exporter requires the configured local stdio EvoMyn client.')
    params = StdioServerParameters(command=settings['command'], args=settings.get('args', []), env={**os.environ, **settings.get('env', {})})
    articles = []
    async with asyncio.timeout(90):
        async with stdio_client(params) as (reader, writer):
            async with ClientSession(reader, writer) as session:
                await session.initialize()
                for item in items:
                    result = await session.call_tool('archive_get', {'record_id': item['record_id']})
                    dumped = result.model_dump(by_alias=True)
                    if dumped.get('isError', False):
                        raise ValueError('EvoMyn rejected a selected record; no export was written.')
                    record = dumped.get('structuredContent')
                    if record is None:
                        chunks = [part['text'] for part in dumped.get('content', []) if part.get('type') == 'text']
                        if len(chunks) != 1:
                            raise ValueError('Unexpected MCP response; no export was written.')
                        record = json.loads(chunks[0])
                    if isinstance(record, dict) and isinstance(record.get('record'), dict):
                        record = record['record']
                    if not isinstance(record, dict):
                        raise ValueError('Unexpected record shape; no export was written.')
                    articles.append(project_record(record, item))
    return articles


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--selection', type=Path, default=ROOT / '.local' / 'publications.json')
    parser.add_argument('--codex-config', type=Path, default=Path(os.environ.get('CODEX_HOME', Path.home() / '.codex')) / 'config.toml')
    args = parser.parse_args()
    if not args.selection.exists():
        raise SystemExit('Create .local/publications.json with {"articles": []}; add only approved records.')
    selection = json.loads(args.selection.read_text('utf-8'))
    items = selection['articles']
    if not isinstance(items, list):
        raise ValueError('articles must be an explicit list of selected records.')
    for item in items:
        if not isinstance(item.get('record_id'), str) or not item['record_id'].strip():
            raise ValueError('Every selection needs a stable record_id.')
    articles = asyncio.run(fetch_selected(items, args.codex_config)) if items else []
    slugs = [item['slug'] for item in articles]
    if len(slugs) != len(set(slugs)):
        raise ValueError('Duplicate publication slug; no export was written.')
    target = ROOT / 'content' / 'evomyn.json'
    with tempfile.NamedTemporaryFile(mode='w', dir=target.parent, encoding='utf-8', delete=False) as stream:
        temporary = Path(stream.name)
        json.dump({'articles': articles}, stream, ensure_ascii=False, indent=2)
        stream.write('\n')
    try:
        os.replace(temporary, target)
    finally:
        temporary.unlink(missing_ok=True)
    print(f'Exported {len(articles)} explicitly selected article(s). Review the diff before publishing.')


if __name__ == '__main__':
    main()
