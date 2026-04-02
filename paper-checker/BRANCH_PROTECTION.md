# 分支保护规则

**创建时间：** 2026-04-02  
**状态：** ✅ 生效中

---

## 🛡️ 受保护分支

### wechat 分支（微信端）

**所有者：** 小龙女二代（微信端 Agent）

**保护规则：**
- ✅ 微信端 Agent 可以自由修改
- ❌ 网页端 Agent **不能直接修改**
- ⚠️ 网页端要修改 → 必须创建 PR → 微信端 Agent 审核

**包含文件：**
```
config.wechat.py
app.wechat.py
uploads_wechat/
output_wechat/
packages_wechat/
logs_wechat/
tasks_wechat.db
```

---

### web 分支（网页端）

**所有者：** 网页端 Agent

**保护规则：**
- ✅ 网页端 Agent 可以自由修改
- ❌ 微信端 Agent **不能直接修改**
- ⚠️ 微信端要修改 → 必须创建 PR → 网页端 Agent 审核

**包含文件：**
```
config.web.py
app.web.py
uploads_web/
output_web/
packages_web/
logs_web/
tasks_web.db
```

---

### main 分支（公共稳定版）

**所有者：** 双方共同所有

**保护规则：**
- ❌ **禁止直接 push**
- ⚠️ 必须通过 Pull Request
- ⚠️ 需要至少 1 人审核
- ⚠️ 修改对方模块需要对方审核

**包含文件：**
```
modules/validator.py
modules/citation_context_extractor.py
modules/semantic.py
modules/task_manager/
```

---

## 📋 修改流程

### 微信端要修改 main 分支

```bash
# 1. 在 wechat 分支开发
git checkout wechat
# ... 修改代码 ...
git commit -m "微信端功能：xxx"

# 2. 创建 PR 到 main
git push origin wechat
# GitHub 上创建 PR: wechat → main

# 3. 通知网页端审核
# 在聊天里说："创建了 PR #123，请审核"

# 4. 网页端审核
# 网页端 Agent 查看 PR，确认没问题
# 点击 "Merge" 合并

# 5. 合并完成
```

### 网页端要修改 main 分支

```bash
# 1. 在 web 分支开发
git checkout web
# ... 修改代码 ...
git commit -m "网页端功能：yyy"

# 2. 创建 PR 到 main
git push origin web
# GitHub 上创建 PR: web → main

# 3. 通知微信端审核
# 在聊天里说："创建了 PR #124，请审核"

# 4. 微信端审核
# 微信端 Agent 查看 PR，确认没问题
# 点击 "Merge" 合并

# 5. 合并完成
```

---

## ⚠️ 禁止行为

**以下行为会导致功能丢失，严格禁止：**

### ❌ 禁止直接修改对方分支
```bash
# 错误示例
git checkout wechat
# 网页端 Agent 直接修改微信端代码 ❌

git checkout web
# 微信端 Agent 直接修改网页端代码 ❌
```

### ❌ 禁止直接 push 到 main
```bash
# 错误示例
git checkout main
git push origin main  # 没有经过 PR ❌
```

### ❌ 禁止删除对方分支
```bash
# 错误示例
git branch -D wechat  # 删除微信端分支 ❌
git push origin --delete wechat  # 删除远程分支 ❌
```

### ❌ 禁止强制推送覆盖历史
```bash
# 错误示例
git push --force origin main  # 强制推送，覆盖历史 ❌
```

---

## ✅ 正确做法

### 1. 修改前先沟通
```
在聊天里说：
"我要修改 xxx 模块，可以吗？"
等对方确认后再修改
```

### 2. 使用 PR 流程
```
分支开发 → 创建 PR → 对方审核 → 合并
```

### 3. 定期同步
```
每天同步一次 main 分支
git pull origin main
```

### 4. 备份重要版本
```
创建版本标签
git tag -a v1.0-wechat
git push origin v1.0-wechat
```

---

## 🔍 检查清单

**修改代码前检查：**

- [ ] 我在正确的分支上吗？
- [ ] 我修改的文件属于我的模块吗？
- [ ] 如果要修改对方模块，已经沟通过了吗？
- [ ] 如果要修改 main 分支，创建 PR 了吗？
- [ ] 已经通知对方审核了吗？
- [ ] 已经备份当前版本了吗？

---

## 📊 违规处理

**如果发现违规修改：**

1. **立即通知对方**
   ```
   "⚠️ 发现未经审核的修改，提交人：xxx"
   ```

2. **恢复到修改前版本**
   ```bash
   git revert <commit-hash>
   git push origin <branch>
   ```

3. **记录违规事件**
   ```markdown
   | 日期 | 违规人 | 违规内容 | 处理方式 |
   |------|--------|----------|----------|
   | 2026-04-02 | xxx | 直接 push main | 已恢复 |
   ```

4. **更新保护规则（如果需要）**
   ```
   加强分支保护
   添加更多检查
   ```

---

## 📞 联系方式

**微信端 Agent：**
- 名字：小龙女二代
- 通道：微信
- 响应时间：即时

**网页端 Agent：**
- 名字：网页端 Agent
- 通道：网页聊天
- 响应时间：即时

---

**创建时间：** 2026-04-02  
**最后更新：** 2026-04-02  
**状态：** ✅ 生效中
