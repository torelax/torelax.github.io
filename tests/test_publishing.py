import importlib.util
import json
from pathlib import Path
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]


def module(name):
    spec = importlib.util.spec_from_file_location(name, ROOT / 'scripts' / (name + '.py'))
    result = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(result)
    return result


class PublishingTests(unittest.TestCase):
    def test_projection_does_not_publish_private_fields_or_unapproved_date(self):
        sync = module('sync_evomyn')
        selected = {'record_id': 'example', 'slug': 'hello', 'include': ['title', 'body']}
        record = {'id': 'example', 'title': '公开标题', 'body': '公开正文',
                  'fields': {'phone': 'PRIVATE'}, 'links': ['PRIVATE'],
                  'file_path': 'PRIVATE', 'occurrence_date': '2026-10'}
        article = sync.project_record(record, selected)
        self.assertEqual(article['title'], '公开标题')
        self.assertEqual(article['blocks'], [{'type': 'p', 'text': '公开正文'}])
        self.assertNotIn('PRIVATE', json.dumps(article))
        self.assertNotIn('date', article)
        self.assertNotIn('example', json.dumps(article))

    def test_projection_preserves_selected_month_precision(self):
        sync = module('sync_evomyn')
        item = {'slug': 'hello', 'include': ['title', 'body', 'occurrence_date']}
        article = sync.project_record({'title': 'a', 'body': 'b', 'occurrence_date': '2026-10'}, item)
        self.assertEqual(article['date'], '2026-10')

    def test_real_evomyn_get_date_field_is_preserved_when_selected(self):
        sync = module('sync_evomyn')
        item = {'slug': 'hello', 'include': ['title', 'body', 'occurrence_date']}
        article = sync.project_record({'title': 'a', 'body': 'b', 'date': '2026'}, item)
        self.assertEqual(article.get('date'), '2026')

    def test_private_field_selection_and_missing_body_are_rejected(self):
        sync = module('sync_evomyn')
        with self.assertRaises(ValueError):
            sync.project_record({'title': 'a', 'body': 'b'}, {'slug': 'safe', 'include': ['title', 'body', 'fields']})
        with self.assertRaises(ValueError):
            sync.project_record({'title': 'a'}, {'slug': 'safe', 'include': ['title', 'body']})

    def test_body_is_text_and_cannot_execute_html(self):
        build = module('build')
        html = build.render_blocks([{'type': 'p', 'text': '<script>alert(1)</script>'}])
        self.assertNotIn('<script>', html)
        self.assertIn('&lt;script&gt;', html)

    def test_unsafe_links_and_traversal_slugs_are_rejected(self):
        build = module('build')
        for link in ['javascript:alert(1)', 'data:text/html,hello', '//example.com', '/private']:
            with self.assertRaises(ValueError):
                build.safe_url(link)
        for slug in ['../private', 'a/b', '', 'A']:
            with self.assertRaises(ValueError):
                build.validate_slug(slug)
        self.assertEqual(build.safe_url('https://github.com/torelax'), 'https://github.com/torelax')

    def test_fresh_build_removes_withdrawn_articles_and_does_not_copy_sources(self):
        build = module('build')
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / 'src').mkdir()
            (root / 'content').mkdir()
            for source in (ROOT / 'src').iterdir():
                (root / 'src' / source.name).write_bytes(source.read_bytes())
            site = {'name': 'Example', 'github': 'https://github.com/torelax', 'about': '',
                    'projects': [], 'articles': [{'slug': 'old', 'title': 'Old', 'category': 'Note',
                    'summary': '', 'blocks': [{'type': 'p', 'text': 'TEXT'}]}]}
            (root / 'content' / 'site.json').write_text(json.dumps(site), encoding='utf-8')
            (root / 'PRIVATE.db').write_text('SECRET')
            build.build_site(root)
            self.assertTrue((root / 'dist' / 'posts' / 'old' / 'index.html').is_file())
            self.assertFalse((root / 'dist' / 'PRIVATE.db').exists())
            site['articles'] = []
            (root / 'content' / 'site.json').write_text(json.dumps(site), encoding='utf-8')
            build.build_site(root)
            self.assertFalse((root / 'dist' / 'posts' / 'old').exists())
            self.assertTrue((root / 'dist' / 'index.html').is_file())


if __name__ == '__main__':
    unittest.main()
