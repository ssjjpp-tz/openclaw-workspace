# 📚 学致源论文检测系统 - 长期记忆

**创建时间：** 2026-03-31  
**系统版本：** v2.0  
**模板编号：** XZY-RPT-2026-V2

---

## 🏢 公司信息

- **公司全称：** 学致源文化传播有限公司
- **部门名称：** 学致源 · 学术诚信检测中心
- **简称：** 学致源

---

## 📄 报告模板（固化）

### 模板配置
- **版本：** v2.0
- **编号：** XZY-RPT-2026-V2
- **字体：** 仿宋（正文）、黑体（标题）
- **字号：** 五号 (10.5pt) / 小四 (12pt)
- **格式：** DOCX (Word)

### 报告结构（9 部分）
1. 封面 - 报告编号、文档信息、学致源 branding
2. 稿件基本信息 - 篇名、作者、单位等
3. 检测概览 - 核心指标（大字）、总体评价
4. DOI 验证详情 - 表格形式
5. 语义相关性分析 - 逐条详细分析
6. 问题列表 - 红/黄/绿分类
7. 修改建议 - 具体可操作
8. 评分详情 - 表格 + 评级
9. 落款与免责声明 - 学致源版权

### 评分标准（固化）
- **DOI 有效性：** 40% 权重，≥90% 得满分
- **引用相关性：** 40% 权重，≥80% 强相关得满分
- **撤稿风险：** 20% 权重，0 撤稿得满分

**评级标准：**
- ⭐⭐⭐⭐⭐ 优秀 (≥90 分)
- ⭐⭐⭐⭐ 良好 (≥80 分)
- ⭐⭐⭐ 合格 (≥70 分)
- ⭐⭐ 待改进 (≥60 分)
- ⭐ 不合格 (<60 分)

**通过标准：**
- ✅ 通过：总分≥80 且无撤稿
- ⚠️ 待修改：60≤总分<80
- ❌ 不通过：总分<60 或有撤稿

---

## 📂 关键文件位置

| 文件 | 路径 | 作用 |
|------|------|------|
| 一键运行脚本 | `/home/admin/.openclaw/workspace/paper-checker/run_verification.py` | 自动执行完整流程 |
| 报告生成器 | `/home/admin/.openclaw/workspace/paper-checker/generate_report_docx.py` | 生成学致源标准报告 |
| 相关性分析 | `/home/admin/.openclaw/workspace/paper-checker/analyze_correlation.py` | 语义相关性分析 |
| 使用说明 | `/home/admin/.openclaw/workspace/paper-checker/README.md` | 完整操作手册 |
| 报告输出 | `/home/admin/.openclaw/workspace/reports/` | 生成的报告存储 |

---

## 📧 邮件流程

### 任务人流向
```
任务人 (308724135@qq.com)
         ↓ 发送论文
         ↓
   tlsjp@163.com (检测邮箱)
         ↓ 自动处理
         ↓
   生成 DOCX 报告
         ↓ 自动回复
         ↓
任务人 (308724135@qq.com) ← 收到报告
```

### 邮件自动保存
- ✅ 发送的邮件自动保存在 163 邮箱"已发送"文件夹
- ✅ 不需要额外存储
- ✅ 随时可以查看历史记录

### 邮件模板
**主题：** 【学致源】论文参考文献验证报告 - {报告编号}

**收件人：** 原邮件发件人（任务人）

**正文包含：**
- 报告编号
- 核心指标（DOI 有效率、相关度、评分）
- 总体评价
- 主要问题
- 附件说明
- 复核联系方式

---

## 🛠️ 调用方法

### 方法 1：一键运行（推荐）
```bash
cd /home/admin/.openclaw/workspace/paper-checker
python3 run_verification.py \
  --docx /path/to/paper.docx \
  --doc-name "论文标题" \
  --author "作者姓名" \
  --recipient "308724135@qq.com"
```

### 方法 2：分步执行
```bash
# 1. 提取 DOI
python3 extract_dois.py --docx paper.docx --output dois.json

# 2. 验证 DOI
python3 verify_dois.py --input dois.json --output verified.json

# 3. 相关性分析
python3 analyze_correlation.py --docx paper.docx --refs verified.json --output correlation.json

# 4. 生成报告
python3 generate_report_docx.py \
  --refs verified.json \
  --correlation correlation.json \
  --output report.docx \
  --doc-name "论文标题" \
  --author "作者姓名"
```

### 方法 3：从邮件自动处理
```bash
# 检查新邮件
cd /home/admin/.openclaw/workspace/skills/imap-smtp-email
node scripts/imap.js check --limit 5

# 下载附件
node scripts/imap.js download <uid> --dir /home/admin/.openclaw/workspace/paper-checker/inbox

# 转换格式
libreoffice --headless --convert-to docx --outdir /tmp inbox/*.doc

# 运行验证
python3 /home/admin/.openclaw/workspace/paper-checker/run_verification.py \
  --docx /tmp/paper.docx \
  --recipient "原发件人邮箱"
```

---

## ✅ 固化检查清单

每次生成报告前确认：

- [ ] 模板版本号显示为 v2.0
- [ ] 模板编号显示为 XZY-RPT-2026-V2
- [ ] 字体使用仿宋（正文）和黑体（标题）
- [ ] 报告包含 9 个部分
- [ ] 评分标准正确（40%+40%+20%）
- [ ] 学致源 branding 正确显示
- [ ] 邮件发送给任务人（原发件人）
- [ ] 报告自动保存到邮箱"已发送"

---

## 📝 修改日志

| 版本 | 日期 | 修改内容 |
|------|------|----------|
| v2.0 | 2026-03-31 | 学致源 branding、完整 9 部分结构、仿宋字体 |
| v1.0 | 2026-03-30 | 初始版本，基础报告结构 |

---

**此文件记录学致源论文检测系统的关键信息，确保每次调用使用相同学致源模板。**

*最后更新：2026-03-31*
