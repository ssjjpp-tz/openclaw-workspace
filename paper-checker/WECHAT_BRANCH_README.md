# 微信端独立分支说明

**分支名称：** `wechat`  
**创建时间：** 2026-04-02  
**状态：** ✅ 独立开发

---

## 📋 分支结构

```
main 分支（公共稳定版）
  ├─ wechat 分支（微信端独立）← 当前所在
  └─ web 分支（网页端独立）
```

---

## 🎯 独立内容

### 1. 独立配置
**文件：** `config.wechat.py`

**独立内容：**
- ✅ 数据库：`tasks_wechat.db`（不与网页端共享）
- ✅ 上传目录：`uploads_wechat/`
- ✅ 输出目录：`output_wechat/`
- ✅ 压缩包目录：`packages_wechat/`
- ✅ 任务编号前缀：`TASK-WX-`

---

### 2. 独立 API 服务器
**文件：** `app.wechat.py`

**独立接口：**
```
POST   /api/wechat/submit          # 提交任务
GET    /api/wechat/query/<id>      # 查询进度
GET    /api/wechat/download/<id>   # 下载报告
GET    /api/wechat/stats           # 统计信息
GET    /api/wechat/health          # 健康检查
```

**独立端口：** `5001`（网页端可能用 5000）

---

### 3. 独立数据库
**文件：** `tasks_wechat.db`

**表结构：**
```sql
CREATE TABLE tasks (
    task_id TEXT UNIQUE NOT NULL,      -- 微信端：TASK-WX-xxxxx
    email TEXT NOT NULL,
    author TEXT NOT NULL,
    doc_name TEXT NOT NULL,
    file_path TEXT NOT NULL,
    status TEXT DEFAULT 'pending',
    progress INTEGER DEFAULT 0,
    report_path TEXT,
    zip_path TEXT,
    created_at DATETIME,
    completed_at DATETIME,
    expires_at DATETIME
);
```

---

### 4. 独立任务编号
**格式：** `TASK-WX-YYYYMMDD-XXXXXX`

**示例：**
- `TASK-WX-20260402-A3F5B2`
- `TASK-WX-20260402-9C8D1E`

**与网页端区分：**
- 微信端：`TASK-WX-xxxxx`
- 网页端：`TASK-WEB-xxxxx` 或 `TASK-xxxxx`

---

## 🚀 启动微信端服务

```bash
# 切换到微信端分支
git checkout wechat

# 启动微信端 API 服务器
python3 app.wechat.py

# 访问地址
http://localhost:5001
```

---

## 🧪 测试微信端

### 1. 提交任务
```bash
curl -X POST http://localhost:5001/api/wechat/submit \
  -F "email=test@wechat.com" \
  -F "author=微信用户" \
  -F "file=@test_paper.docx"
```

**返回：**
```json
{
  "success": true,
  "task_id": "TASK-WX-20260402-A3F5B2",
  "message": "任务已提交，请保存任务编号：TASK-WX-20260402-A3F5B2",
  "channel": "wechat"
}
```

### 2. 查询进度
```bash
curl http://localhost:5001/api/wechat/query/TASK-WX-20260402-A3F5B2
```

**返回：**
```json
{
  "task_id": "TASK-WX-20260402-A3F5B2",
  "status": "completed",
  "progress": 100,
  "channel": "wechat",
  "report_url": "/api/wechat/download/TASK-WX-20260402-A3F5B2/report",
  "zip_url": "/api/wechat/download/TASK-WX-20260402-A3F5B2/zip"
}
```

### 3. 下载报告
```bash
curl -O http://localhost:5001/api/wechat/download/TASK-WX-20260402-A3F5B2/zip
```

---

## 📁 目录结构

```
paper-checker/
├── config.wechat.py              # 微信端配置
├── app.wechat.py                 # 微信端 API 服务器
├── tasks_wechat.db               # 微信端数据库
├── uploads_wechat/               # 微信端上传目录
├── output_wechat/                # 微信端输出目录
├── packages_wechat/              # 微信端压缩包目录
├── logs_wechat/                  # 微信端日志目录
│
├── modules/
│   ├── task_manager/             # 任务管理模块（共用）
│   ├── validator.py              # 文献验证（共用）
│   ├── citation_context_extractor.py  # 上下文提取（共用）
│   └── semantic.py               # 语义分析（共用）
│
└── WECHAT_BRANCH_README.md       # 本文档
```

---

## 🔄 与 main 分支的关系

### 共享内容（从 main 同步）
- ✅ 核心功能模块（三大验证）
- ✅ 任务管理模块基础逻辑
- ✅ 报告生成模块

### 独立内容（微信端特有）
- ✅ 配置文件（`config.wechat.py`）
- ✅ API 服务器（`app.wechat.py`）
- ✅ 数据库（`tasks_wechat.db`）
- ✅ 目录结构（`uploads_wechat/` 等）
- ✅ 任务编号前缀（`TASK-WX-`）

---

## ⚠️ 注意事项

### 1. 数据库隔离
- ❌ 微信端不使用 `tasks.db`（可能是网页端的）
- ✅ 微信端使用 `tasks_wechat.db`（独立）

### 2. 端口隔离
- ❌ 微信端不使用 5000 端口（可能网页端在用）
- ✅ 微信端使用 5001 端口

### 3. 任务编号隔离
- ❌ 微信端不使用 `TASK-` 前缀（可能重复）
- ✅ 微信端使用 `TASK-WX-` 前缀

### 4. 文件目录隔离
- ❌ 微信端不使用 `uploads/`（可能网页端在用）
- ✅ 微信端使用 `uploads_wechat/`

---

## 📊 分支切换

```bash
# 切换到微信端分支
git checkout wechat

# 切换到 main 分支
git checkout main

# 切换到网页端分支（如果有）
git checkout web
```

---

## 🎯 开发流程

### 微信端开发
```bash
# 1. 切换到微信端分支
git checkout wechat

# 2. 开发微信端功能
# ... 修改代码 ...

# 3. 提交
git add .
git commit -m "微信端功能：xxx"

# 4. 推送到远程
git push origin wechat
```

### 同步 main 分支的更新
```bash
# 1. 切换到 main 分支
git checkout main

# 2. 拉取最新代码
git pull origin main

# 3. 切换回微信端分支
git checkout wechat

# 4. 合并 main 分支的更新
git merge main

# 5. 解决冲突（如果有）
# 6. 测试微信端功能
# 7. 提交合并结果
git commit -m "合并 main 分支更新"
```

---

## ✅ 完成状态

**微信端独立完成：**
- ✅ 独立配置（`config.wechat.py`）
- ✅ 独立 API 服务器（`app.wechat.py`）
- ✅ 独立数据库（`tasks_wechat.db`）
- ✅ 独立任务编号（`TASK-WX-`）
- ✅ 独立目录结构
- ✅ 完整测试脚本

**可以随时启动，不影响网页端！**

---

**创建时间：** 2026-04-02  
**创建人：** 小龙女二代 🐉  
**分支状态：** ✅ 独立可用
