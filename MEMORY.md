# MEMORY.md - Long-Term Memory

## Preferences

- **联网搜索优先使用 searxng skill** —— 只要涉及联网搜索任务，优先调用 searxng 技能而非直接使用 web_search 工具。

## Skills Installed (2026-03-25)

**文档生成类：**
- `generate-word-docx` - Word 文档生成 (.docx)
- `generate-excel` - Excel 表格生成 (.xlsx)
- `pdf-generator` - PDF 文档生成

**数据与工具类：**
- `data-pandas` - Python Pandas 数据分析
- `doi-lookup` - 学术论文 DOI 查询
- `web-scraper` - 网页数据抓取

**开发类：**
- `github-cli` - GitHub CLI 集成
- `git-commit` - Git commit 自动化
- `refactor` - 代码重构

**自动化与集成：**
- `n8n` - n8n 工作流自动化
- `todoist` - Todoist 任务管理
- `imap-smtp-email` - 邮件收发 (IMAP/SMTP)
- `obsidian` - Obsidian 笔记管理

**智能与记忆：**
- `hippocampus-memory` - 持久化记忆系统
- `ontology` - 知识图谱/结构化记忆
- `proactive-agent` - 主动代理模式
- `self-improvement` - 自我改进/错误学习

**搜索与发现：**
- `searxng` - 本地隐私搜索引擎（搜索优先使用）
- `find-skills` - 技能发现与安装
- `skill-vetter` - 安全检查技能

**其他：**
- `agent-browser` - 无头浏览器自动化
- `weather` - 天气查询
- `healthcheck` - 安全审计
- `skill-creator` - 技能创建工具
- `qqbot-cron` - QQ 机器人定时提醒
- `qqbot-media` - QQ 媒体发送

## Notes

- Created: 2026-03-05

## 学致源论文检测系统 (2026-03-31 更新)

**核心功能**：论文参考文献验证 + DOI 反向查询 + 真实性标注 + 多源摘要获取

**检测流程**：
1. **DOI 补充** - 如果文章没提供 DOI，通过作者 + 年份反向查询
2. **多源摘要获取** - 从 CrossRef/PubMed/Semantic Scholar/arXiv 获取摘要
3. **真实性标注** - 未找到 DOI 的文献标注为"⚠️ 真实性存疑"
4. **引用定位** - 支持两种格式：数字格式 [1][2] 和 作者 - 年份格式
5. **相关性分析** - 多维度评分（主题 + 关键词 + 上下文 + 引用意图）
6. **报告生成** - 包含 DOI 验证表、相关性分析、问题列表、修改建议

**多源数据策略**（重要！）：
- 不依赖单一 API，避免限流和信息缺失
- CrossRef：DOI 元数据（可能有摘要）
- PubMed：生物医学文献（摘要完整）
- Semantic Scholar：计算机/生物医学（有摘要，免费 API）
- arXiv：预印本（有摘要）
- **Google Scholar**：覆盖最广，如果都找不到 → 真实性高度存疑

**真实性评估**：
- ✅ 真实性高 - 多源确认，有摘要
- ⚠️ 真实性中等 - 有基本信息，但缺少摘要
- ❌ 真实性存疑 - 信息不完整
- 🔴 真实性高度存疑 - 所有数据源都找不到完整信息

**评分标准**：
- DOI 有效性 40% + 引用相关性 40% + 撤稿风险 20%
- 相关性分析：主题相似度 40 分 + 关键词重叠 30 分 + 上下文 20 分 + 引用意图 10 分

**文件位置**：`/home/admin/.openclaw/workspace/paper-checker/`

**邮件发送**：
- 作者邮箱 + 委托人邮箱都要发送
- 附件：ZIP 压缩包（原始论文 + 检测报告 + 说明文件）

**文件清理策略**：
- 处理完成后**不立即删除**，保留 24 小时用于回溯
- 定时清理：每天凌晨 3 点执行 `cleanup_old_files.py`
- 清理规则：
  - ✅ 保留：处理完成 < 24 小时的文件
  - 🗑️ 清理：处理完成 > 24 小时的文件
  - ⏭️ 跳过：未处理（pending）的文件
- 手动清理：`python3 cleanup_old_files.py`

**任务追踪系统**：
- 每个上传任务生成唯一编号：`TASK-YYYYMMDD-序号`
- 任务状态流转：`pending → processing → processed → sent → completed`
- 通过任务编号可查询：
  - 任务详情（文件、作者、邮箱）
  - 报告编号
  - 当前状态
  - 完整时间线
- 查询方式：
  - CLI: `python3 task_manager.py status <任务 ID>`
  - API: `GET /task/<任务 ID>`
  - 列表：`python3 task_manager.py list`
  - 统计：`python3 task_manager.py stats`
- 数据库：`/home/admin/.openclaw/workspace/paper-checker/tasks/tasks.json`
