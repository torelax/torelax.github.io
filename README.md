# torelax 个人网站

基于 [Astro Cactus](https://github.com/chrismwilliams/astro-theme-cactus) v8.3.0，保留其 MIT LICENSE。上游基线：728f1f4eeb80208398649261d7635f311cafa011。原版文档见 docs/cactus-upstream.md。

## 开发与构建

使用 Node.js 24，pnpm 11.25.0。

```sh
pnpm install --frozen-lockfile
pnpm dev
pnpm exec astro check
pnpm build
pnpm preview --host 127.0.0.1 --port 8791
```

build 后自动运行 Pagefind，搜索需在构建预览中测试。

## 内容管理

- 网站标题、作者、域名、导航：src/site.config.ts
- 首页、关于、项目：src/pages/index.astro、about.astro、projects.astro
- 文章：content/posts/*.md
- 旧站原文：legacy/README.md；网站下载副本 public/archive/original-notes.md
- 已保留旧站全部 Python 部分，文章日期依据旧仓库提交时间。

网站为独立静态网站，不连接任何个人资料库，没有 EvoMyn 导出、同步、凭据或服务依赖。后续助手整理内容时，可根据用户要求查询资料库，再编辑普通 Markdown。

## GitHub Pages

Settings → Pages → Source 选择 GitHub Actions。PR 运行检查与构建；合并 main 后只部署 dist。域名已配置为 https://torelax.github.io/ 。

当前仅搭建框架，展示名暂用 GitHub 用户名；未提供的履历与项目保持空白。示例作者内容已移除。
