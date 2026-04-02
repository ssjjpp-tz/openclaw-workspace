# 学致源论文验证系统 - 部署说明

**版本：** v6.0-Production  
**更新日期：** 2026-04-02  
**状态：** ✅ 可部署

---

## 📋 系统特点

**全自动处理：**
- ✅ 用户提交论文后，自动验证
- ✅ 自动执行三大验证（DOI、上下文、语义）
- ✅ 自动生成报告
- ✅ 自动发送邮件
- ✅ 无需人工操作

**性能：**
- ✅ 单篇：80 秒
- ✅ 3 篇并行：88 秒（2.86x 效率）
- ✅ 产能：40-45 篇/小时

---

## 🚀 部署方式

### 方式 1：自动部署（推荐）

**步骤：**

1. **上传部署文件到服务器**
   ```bash
   # 将整个 paper-checker 目录上传到服务器
   scp -r paper-checker/ user@106.14.15.241:/tmp/
   ```

2. **执行部署脚本**
   ```bash
   ssh user@106.14.15.241
   cd /tmp/paper-checker
   chmod +x deploy.sh
   sudo ./deploy.sh
   ```

3. **验证部署**
   ```bash
   # 检查服务状态
   systemctl status xueziyuan
   
   # 查看日志
   journalctl -u xueziyuan -f
   
   # 访问网页
   http://106.14.15.241:5000
   ```

---

### 方式 2：手动部署

**步骤：**

1. **安装依赖**
   ```bash
   sudo apt update
   sudo apt install python3 python3-pip
   pip3 install flask docx python-docx
   ```

2. **复制文件**
   ```bash
   sudo cp app.production.py /var/www/html/referencecheck/app.py
   sudo cp -r modules/ /var/www/html/referencecheck/
   sudo cp -r parser/ /var/www/html/referencecheck/
   sudo cp -r analyzer/ /var/www/html/referencecheck/
   sudo cp -r models/ /var/www/html/referencecheck/
   ```

3. **创建目录**
   ```bash
   sudo mkdir -p /var/www/html/referencecheck/{uploads,output,packages}
   sudo chmod 755 /var/www/html/referencecheck/{uploads,output,packages}
   ```

4. **配置邮件**
   ```bash
   # 编辑 app.py，修改邮件配置
   sudo nano /var/www/html/referencecheck/app.py
   # 修改 SMTP_PASS 为实际密码
   ```

5. **启动服务**
   ```bash
   cd /var/www/html/referencecheck
   sudo python3 app.py &
   ```

---

## ⚙️ 配置说明

### 邮件配置

**编辑文件：** `app.production.py`

```python
SMTP_HOST = 'smtp.163.com'
SMTP_PORT = 465
SMTP_USER = 'tlsjp@163.com'
SMTP_PASS = 'YOUR_PASSWORD'  # ← 替换为实际密码
SENDER_NAME = '学致源检测中心'
```

### 数据库配置

**默认路径：**
```
/tasks_production.db
```

**自动创建，无需手动配置**

### 目录配置

```
/uploads_production/      # 上传的论文
/output_production/       # 生成的报告
/packages_production/     # 压缩包
```

---

## 🔧 Nginx 配置（可选）

**如果需要 80 端口访问：**

1. **安装 Nginx**
   ```bash
   sudo apt install nginx
   ```

2. **配置反向代理**
   ```bash
   sudo nano /etc/nginx/sites-available/referencecheck
   ```

3. **添加配置**
   ```nginx
   server {
       listen 80;
       server_name 106.14.15.241;
       
       location / {
           proxy_pass http://127.0.0.1:5000;
           proxy_set_header Host $host;
           proxy_set_header X-Real-IP $remote_addr;
       }
   }
   ```

4. **启用配置**
   ```bash
   sudo ln -s /etc/nginx/sites-available/referencecheck /etc/nginx/sites-enabled/
   sudo nginx -t
   sudo systemctl restart nginx
   ```

---

## 📊 测试验证

### 1. 检查服务状态

```bash
systemctl status xueziyuan
```

**预期输出：**
```
● xueziyuan.service - 学致源论文验证系统
   Active: active (running)
```

### 2. 访问网页

```
http://106.14.15.241:5000
```

**预期：** 看到提交页面

### 3. 提交测试论文

1. 填写邮箱
2. 填写作者姓名
3. 上传 DOCX 文件
4. 点击"提交检测"

**预期：** 返回任务编号

### 4. 查看后台日志

```bash
journalctl -u xueziyuan -f
```

**预期：** 看到自动处理日志

### 5. 检查邮件

**预期：** 收到包含报告的邮件

---

## 🎯 功能清单

**提交页面：**
- ✅ 邮箱输入
- ✅ 作者姓名输入
- ✅ 文件上传（DOCX，20MB）
- ✅ 提交按钮
- ✅ 进度查询链接

**自动处理：**
- ✅ 后台自动解析论文
- ✅ 自动提取参考文献
- ✅ 自动 DOI 验证
- ✅ 自动语义分析
- ✅ 自动生成报告
- ✅ 自动发送邮件

**查询页面：**
- ✅ 任务编号查询
- ✅ 实时进度显示
- ✅ 状态更新（待处理/处理中/已完成）

---

## 📞 技术支持

**问题排查：**

1. **服务无法启动**
   ```bash
   journalctl -u xueziyuan -n 50
   ```

2. **邮件发送失败**
   ```bash
   # 检查邮件配置
   grep SMTP_PASS /var/www/html/referencecheck/app.py
   ```

3. **文件上传失败**
   ```bash
   # 检查目录权限
   ls -la /var/www/html/referencecheck/
   ```

**联系方式：**
- 部署文档：DEPLOY_INSTRUCTIONS.md
- 测试报告：TEST_REPORT_*.md
- GitHub: https://github.com/ssjjpp-tz/openclaw-workspace

---

## ✅ 部署完成检查清单

- [ ] Python 3.6+ 已安装
- [ ] 依赖已安装（flask, docx）
- [ ] 文件已复制到 /var/www/html/referencecheck/
- [ ] 目录权限已设置（uploads, output, packages）
- [ ] 邮件配置已修改
- [ ] systemd 服务已创建
- [ ] 服务已启动
- [ ] 网页可以访问
- [ ] 提交测试成功
- [ ] 邮件接收成功

---

**部署时间：** 约 10-15 分钟  
**难度：** ⭐⭐（简单）  
**状态：** ✅ 已测试，可部署
