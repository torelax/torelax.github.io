"""Build only approved public content. No database access or third-party packages."""
from datetime import date
from html import escape
import json
from pathlib import Path
import re
import shutil
from string import Template
import tempfile
from urllib.parse import urlsplit

ROOT = Path(__file__).resolve().parents[1]


def validate_slug(value):
    if not isinstance(value, str) or not re.fullmatch(r'[a-z0-9]+(?:-[a-z0-9]+)*', value):
        raise ValueError('Article slugs must contain lowercase letters, numbers and hyphens.')
    return value


def safe_url(value):
    if not isinstance(value, str) or any(ord(c) < 33 for c in value):
        raise ValueError('Invalid URL.')
    parsed = urlsplit(value)
    if parsed.scheme != 'https' or not parsed.hostname or parsed.username or parsed.password:
        raise ValueError('Public links must be absolute HTTPS URLs.')
    return value


def text(value):
    if not isinstance(value, str):
        raise ValueError('Public text must be a string.')
    return escape(value, quote=True)


def render_blocks(blocks):
    rendered = []
    for block in blocks:
        kind = block['type']
        if kind == 'p':
            rendered.append('<p>' + text(block['text']).replace('\n', '<br>') + '</p>')
        elif kind == 'h2':
            rendered.append('<h2>' + text(block['text']) + '</h2>')
        elif kind == 'code':
            rendered.append('<pre><code>' + text(block['text']) + '</code></pre>')
        elif kind == 'list':
            rendered.append('<ul>' + ''.join('<li>' + text(item) + '</li>' for item in block['items']) + '</ul>')
        elif kind == 'table':
            head = ''.join('<th scope="col">' + text(cell) + '</th>' for cell in block['headers'])
            rows = ''.join('<tr>' + ''.join('<td>' + text(str(cell)) + '</td>' for cell in row) + '</tr>' for row in block['rows'])
            rendered.append('<div class="table-wrap" tabindex="0" role="region" aria-label="数据表格"><table><thead><tr>' + head + '</tr></thead><tbody>' + rows + '</tbody></table></div>')
        else:
            raise ValueError('Unsupported content block: ' + str(kind))
    return '\n'.join(rendered)


def article_rows(articles):
    if not articles:
        return '<p class="empty">文章正在整理中。新的文字，会在这里慢慢展开。</p>'
    result = []
    for index, article in enumerate(articles, 1):
        slug = validate_slug(article['slug'])
        search = text(' '.join([article['title'], article.get('summary', ''), article.get('category', '')]))
        result.append(f'''<a class="article-row" href="posts/{slug}/" data-article data-search="{search}">
<span class="row-index">{index:02d}</span><div class="article-copy"><div class="article-meta">{text(article.get('category', '文章'))}</div>
<h3>{text(article['title'])}</h3><p>{text(article.get('summary', ''))}</p></div><span class="row-arrow" aria-hidden="true">↗</span></a>''')
    return '\n'.join(result)


def project_rows(projects):
    if not projects:
        return '<div class="empty-project"><span class="empty-symbol" aria-hidden="true">＋</span><div><h3>暂无公开项目</h3><p>这里留给之后分享的作品与实践。</p></div></div>'
    return ''.join(f'''<a class="project" href="{text(safe_url(item['url']))}"><span class="article-meta">{text(item.get('label', '项目'))}</span>
<h3>{text(item['title'])} <span aria-hidden="true">↗</span></h3><p>{text(item.get('summary', ''))}</p></a>''' for item in projects)


def build_site(root=ROOT):
    root = Path(root).resolve()
    source = root / 'src'
    site = json.loads((root / 'content' / 'site.json').read_text('utf-8'))
    imported = root / 'content' / 'evomyn.json'
    articles = site.get('articles', []) + (json.loads(imported.read_text('utf-8'))['articles'] if imported.exists() else [])
    slugs = [validate_slug(article['slug']) for article in articles]
    if len(slugs) != len(set(slugs)):
        raise ValueError('Duplicate article slug; no files have been published.')
    template = Template((source / 'page.html').read_text('utf-8'))
    common = {'name': text(site['name']), 'github': text(safe_url(site['github'])), 'year': str(date.today().year)}

    def page(title, description, body, prefix='./', page_kind='home'):
        return template.substitute(common, title=text(title), description=text(description),
                                   body=body, prefix=prefix, page_kind=page_kind)

    about = text(site.get('about') or '这里收录公开的项目、技术笔记与文章。')
    home = f'''<main id="main">
<section class="hero" aria-labelledby="hero-title"><div class="hero-top"><span class="eyebrow"><span class="tiny-line"></span> A PERSONAL SPACE</span><span class="hero-edition">项目 / 文字 / 思考</span></div>
<h1 id="hero-title">你好，我是<br><span>{text(site['name'])}</span><span class="hero-period">.</span></h1>
<div class="hero-bottom"><p>{about}</p><a class="text-link" href="#writing">阅读文章 <span aria-hidden="true">↗</span></a></div>
<span class="hero-mark" aria-hidden="true">*</span></section>
<section id="about" class="section about-section" aria-labelledby="about-title"><div class="section-label"><span>01 / ABOUT</span><h2 id="about-title">关于这里</h2></div><div class="section-body about-body"><p class="large-copy">一些做过的事，<br>一些写下的想法。</p><p class="muted">{about}</p><a class="text-link" href="{common['github']}">在 GitHub 找到我 <span aria-hidden="true">↗</span></a></div></section>
<section id="projects" class="section" aria-labelledby="projects-title"><div class="section-label"><span>02 / PROJECTS</span><h2 id="projects-title">项目</h2></div><div class="section-body">{project_rows(site.get('projects', []))}</div></section>
<section id="writing" class="section writing-section" aria-labelledby="writing-title"><div class="section-label"><span>03 / WRITING</span><h2 id="writing-title">文字</h2><p class="muted">技术笔记与公开文章</p></div><div class="section-body"><div class="writing-toolbar"><span class="small-label">文章 <span class="count" id="article-count">{len(articles):02d}</span></span><label class="search-box"><span class="sr-only">搜索文章</span><input type="search" id="article-search" placeholder="搜索文章" autocomplete="off"><span aria-hidden="true">⌕</span></label></div><div class="article-list">{article_rows(articles)}</div><p class="empty" id="no-results" hidden>没有找到相关文章，换个关键词试试。</p><p class="sr-only" id="search-status" role="status" aria-live="polite"></p></div></section>
<section class="closing"><span class="eyebrow">KEEP IN TOUCH</span><p>从这里，<br>继续交流。</p><a href="{common['github']}" class="contact-link">GitHub <span aria-hidden="true">↗</span></a></section></main>'''
    pages = {'index.html': page(site['name'] + ' · 个人主页', '项目、技术笔记与公开文章。', home)}
    for article in articles:
        slug = validate_slug(article['slug'])
        article_date = f'<span>{text(article["date"])}</span>' if article.get('date') else ''
        body = f'''<main id="main" class="post-main"><a class="back-link" href="../../#writing">← 所有文章</a>
<article><header class="post-header"><div class="post-meta"><span>{text(article.get('category', '文章'))}</span>{article_date}</div><h1>{text(article['title'])}</h1><p class="post-summary">{text(article.get('summary', ''))}</p></header>
<div class="prose">{render_blocks(article['blocks'])}</div></article><a class="back-link post-back" href="../../#writing">← 返回文章列表</a></main>'''
        pages[f'posts/{slug}/index.html'] = page(article['title'] + ' · ' + site['name'], article.get('summary', ''), body, '../../', 'post')
    pages['404.html'] = page('页面未找到 · ' + site['name'], '页面未找到。', '<main id="main" class="post-main"><p class="eyebrow">404 / NOT FOUND</p><h1 class="error-title">这页暂时不在。</h1><a class="text-link" href="/">回到首页 ↗</a></main>', '/', 'post')

    output = root / 'dist'
    if output.is_symlink() or output.resolve() != root / 'dist':
        raise ValueError('Output must be the ordinary dist directory inside the checkout.')
    staging = Path(tempfile.mkdtemp(prefix='.build-', dir=root))
    try:
        for filename, html in pages.items():
            target = staging / filename
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(html, encoding='utf-8')
        for filename in ('style.css', 'main.js', 'favicon.svg'):
            shutil.copyfile(source / filename, staging / filename)
        (staging / '.nojekyll').touch()
        if output.exists():
            shutil.rmtree(output)
        staging.rename(output)
    finally:
        if staging.exists():
            shutil.rmtree(staging)
    return len(articles)


if __name__ == '__main__':
    print(f'Built dist/: homepage + {build_site()} article(s).')
