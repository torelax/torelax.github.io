# torelax · 个人主页

公开个人网站，部署目标为 https://torelax.github.io/ 。保留的旧站原文见 legacy/README.md。

## 本地预览

需要 Python 3.11 或更新版本，无构建依赖：

```powershell
python -m unittest discover -s tests -v
python scripts/build.py
python -m http.server 8790 --bind 127.0.0.1 --directory dist
```

打开 http://127.0.0.1:8790/ 。电脑上没有全局 Python 时，也可使用 EvoMyn 安装目录中的 resources/backend/python/python.exe。

## 更新公开内容

编辑 content/site.json 中的 name、about、projects 和 articles。未提供的履历、项目和联系方式保持空白。项目链接仅支持 HTTPS。

文章使用 slug、title、category、summary 和 blocks；块支持 p、h2、code、list、table。标题和正文均按文本转义，不执行正文中的 HTML。日期可省略；有日期时保持原始年、月或日精度。

## 从 EvoMyn 挑选文章

EvoMyn 和个人数据库留在本机；GitHub Actions 不连接本机，也不自动同步整个库。

1. 先明确每条记录的公开范围。导出正文前，检查正文里是否包含不应公开的信息。
2. 在 Git 忽略的 .local/publications.json 保存选择清单。初始内容为 {"articles": []}。例如以下结构中，实际记录ID必须替换为本人明确选择的真实 ID：

```json
{
  "articles": [
    {
      "record_id": "实际记录ID",
      "slug": "my-first-note",
      "include": ["title", "body"],
      "category": "随笔",
      "summary": "经过确认的公开摘要"
    }
  ]
}
```

3. 保持 EvoMyn 桌面应用开启。使用其自带 Python（内含 MCP SDK）运行 scripts/sync_evomyn.py。它读取本机 Codex 配置中的 evomyn 启动命令，并仅调用选定记录的 archive_get。不修改档案库。
4. 查看 git diff -- content/evomyn.json，确认导出的标题和整段正文都适合公开，再构建、预览和提交。

只允许导出 title、body，以及显式选择的 occurrence_date（兼容读取结果中的 date 字段）。fields、附件路径、关系、稳定记录 ID 和其他内部元数据不会写入公开内容。正文按原文导出，不会自动脱敏或摘要。当前库为空，已核对安装源码与 SDK 返回格式，但尚未验证真实非空记录的端到端导出；遇到未知结构或缺少正文时会中止，不覆盖旧导出。清单为空时不连接服务。

从清单移除文章后，必须重新运行导出和构建再发布，才能撤下网页。此前已提交到公开仓库的内容仍可能存在于 Git 历史或外部副本。

## 发布到 GitHub Pages

在仓库 Settings → Pages → Build and deployment 中，将 Source 设为 GitHub Actions。合并到 main 后，工作流运行单元测试、生成 dist/，只上传这个目录并部署。PR 只测试和构建，不发布。

dist/、.local/ 和预览截图均被 Git 忽略。不要把数据库、备份、令牌、服务会话文件或未选定记录放入这个公开仓库。content/ 本身属于公开网站源码。

本仓库不包含定时同步任务。每次发布先从本机显式导出，检查差异后提交；合并后的网站部署由 Actions 完成。