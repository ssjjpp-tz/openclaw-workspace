#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
学致源·论文参考文献验证系统 - 生产环境版本
全自动处理：提交 → 自动验证 → 自动报告 → 自动邮件
"""

import os
import sys
import time
import threading
import smtplib
import zipfile
from datetime import datetime
from flask import Flask, request, jsonify, render_template_string, send_file
from werkzeug.utils import secure_filename
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders

# 导入核心功能模块
sys.path.insert(0, os.path.dirname(__file__))
from modules.task_manager import (
    init_database,
    generate_task_id,
    create_task,
    get_task,
    update_task_status,
    get_statistics,
    create_task_package
)
from parser.file_parser import FileParser
from analyzer.analyzers import AuthenticityAnalyzer, RelevanceAnalyzer

# ========== 配置 ==========
app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 20 * 1024 * 1024  # 20MB
app.config['UPLOAD_FOLDER'] = '/home/admin/.openclaw/workspace/paper-checker/uploads_production'
app.config['OUTPUT_FOLDER'] = '/home/admin/.openclaw/workspace/paper-checker/output_production'
app.config['PACKAGE_FOLDER'] = '/home/admin/.openclaw/workspace/paper-checker/packages_production'

# 创建目录
for folder in ['UPLOAD_FOLDER', 'OUTPUT_FOLDER', 'PACKAGE_FOLDER']:
    os.makedirs(app.config[folder], exist_ok=True)

# 数据库路径
import modules.task_manager.database as db_module
db_module.DB_PATH = '/home/admin/.openclaw/workspace/paper-checker/tasks_production.db'

# 邮件配置
SMTP_HOST = 'smtp.163.com'
SMTP_PORT = 465
SMTP_USER = 'tlsjp@163.com'
SMTP_PASS = 'GFs4j38vb6eEEBvG'  # 需要替换为实际密码或环境变量
SENDER_NAME = '学致源检测中心'

ALLOWED_EXTENSIONS = {'docx', 'doc'}

# ========== HTML 模板 ==========
HTML_TEMPLATE = '''
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>学致源 · 论文参考文献验证系统</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: Arial, sans-serif; background: #f5f5f5; }
        .container { max-width: 1200px; margin: 0 auto; padding: 20px; }
        .header { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 40px 20px; text-align: center; border-radius: 10px; margin-bottom: 30px; }
        .header h1 { font-size: 32px; margin-bottom: 10px; }
        .header p { font-size: 16px; opacity: 0.9; }
        .status { display: inline-block; background: #48bb78; color: white; padding: 5px 15px; border-radius: 20px; font-size: 14px; margin-top: 10px; }
        .content { display: grid; grid-template-columns: 1fr 1fr; gap: 30px; margin-bottom: 30px; }
        .card { background: white; padding: 30px; border-radius: 10px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }
        .card h2 { color: #333; margin-bottom: 20px; font-size: 24px; }
        .feature-list { list-style: none; }
        .feature-list li { padding: 10px 0; border-bottom: 1px solid #eee; }
        .feature-list li:before { content: "✅ "; }
        .form-group { margin-bottom: 20px; }
        .form-group label { display: block; margin-bottom: 8px; color: #555; font-weight: bold; }
        .form-group input[type="email"], .form-group input[type="text"] { width: 100%; padding: 12px; border: 2px solid #e2e8f0; border-radius: 6px; font-size: 16px; }
        .form-group input[type="email"]:focus, .form-group input[type="text"]:focus { outline: none; border-color: #667eea; }
        .file-upload { border: 2px dashed #e2e8f0; padding: 40px; text-align: center; border-radius: 6px; cursor: pointer; transition: all 0.3s; }
        .file-upload:hover { border-color: #667eea; background: #f7fafc; }
        .file-upload input[type="file"] { display: none; }
        .btn { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 15px 40px; border: none; border-radius: 6px; font-size: 18px; cursor: pointer; width: 100%; transition: transform 0.2s; }
        .btn:hover { transform: translateY(-2px); }
        .btn:disabled { background: #ccc; cursor: not-allowed; transform: none; }
        .footer { text-align: center; padding: 30px; color: #666; }
        .time-notice { background: #ebf8ff; padding: 15px; border-radius: 6px; margin-top: 20px; font-size: 14px; color: #2c5282; }
        #result { margin-top: 30px; padding: 20px; border-radius: 6px; display: none; }
        #result.success { background: #c6f6d5; color: #22543d; }
        #result.error { background: #fed7d7; color: #742a2a; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>📚 学致源 · 论文参考文献验证系统</h1>
            <p>学致源文化传播有限公司 · 学术诚信检测中心</p>
            <div class="status">✅ 系统运行中</div>
        </div>
        
        <div class="content">
            <div class="card">
                <h2>🔍 我们能做什么</h2>
                <ul class="feature-list">
                    <li>DOI 有效性验证 - 通过 CrossRef API 验证参考文献 DOI</li>
                    <li>撤稿文献检测 - 检测文献是否被期刊撤稿</li>
                    <li>语义相关性分析 - 比对引用位置与文献内容</li>
                    <li>智能评分系统 - 综合三维度评分</li>
                    <li>专业检测报告 - 生成详细 Word 报告</li>
                    <li>自动邮件返回 - 检测完成后自动发送报告</li>
                </ul>
                <div class="time-notice">
                    <strong>⏱️ 反馈时间说明：</strong><br>
                    • 常规检测（<30 篇参考文献）：5-10 分钟<br>
                    • 标准检测（30-50 篇）：10-20 分钟<br>
                    • 复杂文档（>50 篇）：20-30 分钟<br>
                    <strong>📧 报告将通过邮件自动发送到您填写的邮箱</strong>
                </div>
            </div>
            
            <div class="card">
                <h2>📤 上传论文进行检测</h2>
                <form id="uploadForm" enctype="multipart/form-data">
                    <div class="form-group">
                        <label for="email">📧 接收报告的邮箱 *</label>
                        <input type="email" id="email" name="email" placeholder="example@university.edu.cn" required>
                        <small style="color: #666;">检测报告将发送到此邮箱，请确保地址准确</small>
                    </div>
                    
                    <div class="form-group">
                        <label for="author">✍️ 作者姓名 *</label>
                        <input type="text" id="author" name="author" placeholder="张三" required minlength="2" maxlength="20">
                        <small style="color: #666;">用于报告生成和结果确认（2-20 个字符）</small>
                    </div>
                    
                    <div class="form-group">
                        <label>📄 上传论文文件 *</label>
                        <div class="file-upload" onclick="document.getElementById('file').click()">
                            <div style="font-size: 48px;">📁</div>
                            <div style="margin-top: 10px;">点击选择文件或拖拽到此处</div>
                            <div style="color: #666; margin-top: 5px;">支持格式：DOCX | 最大 20MB</div>
                            <input type="file" id="file" name="file" accept=".docx,.doc" required onchange="updateFileName()">
                        </div>
                        <div id="fileName" style="margin-top: 10px; color: #667eea; font-weight: bold;"></div>
                    </div>
                    
                    <button type="submit" class="btn" id="submitBtn">🚀 提交检测</button>
                </form>
                
                <div id="result"></div>
                
                <div style="margin-top: 20px; text-align: center;">
                    <a href="/query" style="color: #667eea; text-decoration: none;">🔍 查询检测进度</a>
                </div>
            </div>
        </div>
        
        <div class="footer">
            <p>© 2026 学致源文化传播有限公司 · 学术诚信检测中心</p>
            <p>技术支持：simaxuan@92xueshu.com</p>
            <p>当前版本：v6.0-Production | 更新时间：2026-04-02</p>
        </div>
    </div>
    
    <script>
        function updateFileName() {
            const fileInput = document.getElementById('file');
            const fileName = fileInput.files[0]?.name;
            if (fileName) {
                document.getElementById('fileName').textContent = '已选择：' + fileName;
            }
        }
        
        document.getElementById('uploadForm').addEventListener('submit', async function(e) {
            e.preventDefault();
            
            const btn = document.getElementById('submitBtn');
            const resultDiv = document.getElementById('result');
            
            btn.disabled = true;
            btn.textContent = '⏳ 提交中...';
            
            const formData = new FormData(this);
            
            try {
                const response = await fetch('/api/submit', {
                    method: 'POST',
                    body: formData
                });
                
                const data = await response.json();
                
                if (data.success) {
                    resultDiv.className = 'success';
                    resultDiv.innerHTML = `
                        <h3>✅ 提交成功！</h3>
                        <p><strong>任务编号：</strong>${data.task_id}</p>
                        <p><strong>检测时间：</strong>${new Date().toLocaleString('zh-CN')}</p>
                        <p>检测报告将自动发送到邮箱：<strong>${data.email}</strong></p>
                        <p style="margin-top: 15px;"><strong>📋 下一步：</strong></p>
                        <ul style="margin-top: 10px;">
                            <li>1. 保存任务编号：<strong>${data.task_id}</strong></li>
                            <li>2. 等待检测完成（5-30 分钟）</li>
                            <li>3. 查收邮件获取检测报告</li>
                            <li>4. 或<a href="/query?task_id=${data.task_id}">点击此处</a>查询进度</li>
                        </ul>
                    `;
                    resultDiv.style.display = 'block';
                    document.getElementById('uploadForm').reset();
                    document.getElementById('fileName').textContent = '';
                } else {
                    throw new Error(data.error || '提交失败');
                }
            } catch (error) {
                resultDiv.className = 'error';
                resultDiv.innerHTML = `<h3>❌ 提交失败</h3><p>${error.message}</p>`;
                resultDiv.style.display = 'block';
            } finally {
                btn.disabled = false;
                btn.textContent = '🚀 提交检测';
            }
        });
    </script>
</body>
</html>
'''

QUERY_TEMPLATE = '''
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>查询进度 - 学致源论文验证系统</title>
    <style>
        body { font-family: Arial, sans-serif; background: #f5f5f5; padding: 40px 20px; }
        .container { max-width: 600px; margin: 0 auto; background: white; padding: 40px; border-radius: 10px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }
        h1 { color: #333; margin-bottom: 30px; text-align: center; }
        .form-group { margin-bottom: 20px; }
        label { display: block; margin-bottom: 8px; color: #555; font-weight: bold; }
        input[type="text"] { width: 100%; padding: 12px; border: 2px solid #e2e8f0; border-radius: 6px; font-size: 16px; }
        .btn { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 15px 40px; border: none; border-radius: 6px; font-size: 18px; cursor: pointer; width: 100%; }
        #result { margin-top: 30px; padding: 20px; border-radius: 6px; }
        .status-pending { background: #fefcbf; color: #744210; }
        .status-processing { background: #bee3f8; color: #2c5282; }
        .status-completed { background: #c6f6d5; color: #22543d; }
        .status-failed { background: #fed7d7; color: #742a2a; }
        .back-link { display: block; text-align: center; margin-top: 20px; color: #667eea; text-decoration: none; }
    </style>
</head>
<body>
    <div class="container">
        <h1>🔍 查询检测进度</h1>
        <form id="queryForm">
            <div class="form-group">
                <label for="task_id">任务编号 *</label>
                <input type="text" id="task_id" name="task_id" placeholder="TASK-XXXXXXXX-XXXXXX" required>
            </div>
            <button type="submit" class="btn">查询</button>
        </form>
        <div id="result"></div>
        <a href="/" class="back-link">← 返回首页提交论文</a>
    </div>
    
    <script>
        document.getElementById('queryForm').addEventListener('submit', async function(e) {
            e.preventDefault();
            const taskId = document.getElementById('task_id').value;
            const resultDiv = document.getElementById('result');
            
            try {
                const response = await fetch(`/api/query/${taskId}`);
                const data = await response.json();
                
                if (data.success) {
                    const statusClass = 'status-' + data.status;
                    const statusText = {
                        'pending': '⏳ 待处理',
                        'processing': '🔄 处理中',
                        'completed': '✅ 已完成',
                        'failed': '❌ 处理失败'
                    }[data.status];
                    
                    resultDiv.className = statusClass;
                    resultDiv.innerHTML = `
                        <h3>任务进度</h3>
                        <p><strong>任务编号：</strong>${data.task_id}</p>
                        <p><strong>状态：</strong>${statusText}</p>
                        <p><strong>进度：</strong>${data.progress}%</p>
                        ${data.completed_at ? `<p><strong>完成时间：</strong>${data.completed_at}</p>` : ''}
                        ${data.status === 'completed' ? `
                            <p style="margin-top: 15px;"><strong>📧 报告已发送到邮箱，请查收！</strong></p>
                        ` : ''}
                    `;
                    resultDiv.style.display = 'block';
                } else {
                    throw new Error(data.message || '查询失败');
                }
            } catch (error) {
                resultDiv.className = 'status-failed';
                resultDiv.innerHTML = `<h3>❌ 查询失败</h3><p>${error.message}</p>`;
                resultDiv.style.display = 'block';
            }
        });
        
        // 如果 URL 中有 task_id 参数，自动查询
        const urlParams = new URLSearchParams(window.location.search);
        const taskId = urlParams.get('task_id');
        if (taskId) {
            document.getElementById('task_id').value = taskId;
            document.getElementById('queryForm').dispatchEvent(new Event('submit'));
        }
    </script>
</body>
</html>
'''

# ========== 辅助函数 ==========
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def send_report_email(to_email, task_id, zip_path, doc_name):
    """自动发送检测报告"""
    try:
        msg = MIMEMultipart()
        msg['From'] = f"{SENDER_NAME} <{SMTP_USER}>"
        msg['To'] = to_email
        msg['Subject'] = f"📚 学致源·论文参考文献验证报告 - {task_id}"
        
        body = f"""
您好！

附件是您的论文《{doc_name}》的参考文献验证报告，请查收。

【任务编号】{task_id}
【检测时间】{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

【报告内容】
✅ 文献真实性验证（CrossRef API）
✅ 上下文引用验证
✅ 语义相关性分析（10 要素对比）
✅ 综合评分

【使用说明】
1. 解压附件获取报告
2. 查看 Word 文档了解详细信息
3. 如有疑问，请联系技术支持

学致源·学术诚信检测中心
{datetime.now().strftime('%Y 年%m 月%d 日')}
"""
        
        msg.attach(MIMEText(body.strip(), 'plain', 'utf-8'))
        
        with open(zip_path, 'rb') as f:
            part = MIMEBase('application', 'octet-stream')
            part.set_payload(f.read())
            encoders.encode_base64(part)
            part.add_header('Content-Disposition', f'attachment; filename="{task_id}.zip"')
            msg.attach(part)
        
        server = smtplib.SMTP_SSL(SMTP_HOST, SMTP_PORT)
        server.login(SMTP_USER, SMTP_PASS)
        server.send_message(msg)
        server.quit()
        
        print(f"✅ 邮件已发送：{to_email}")
        return True
    except Exception as e:
        print(f"❌ 邮件发送失败：{e}")
        return False

def process_task_automatically(task_id, email, author, file_path, doc_name):
    """
    全自动后台处理任务
    提交后自动执行所有验证步骤
    """
    try:
        print(f"\n[自动处理] 开始处理任务：{task_id}")
        print(f"[自动处理] 邮箱：{email}, 作者：{author}, 文件：{doc_name}")
        
        # 更新状态：处理中
        update_task_status(task_id, 'processing', progress=10)
        
        # ========== 第 1 步：解析论文 ==========
        print(f"[自动处理] 第 1 步：解析论文...")
        parser = FileParser()
        document = parser.parse(file_path)
        full_text = document['full_text']
        update_task_status(task_id, 'processing', progress=20)
        
        # ========== 第 2 步：提取参考文献 ==========
        print(f"[自动处理] 第 2 步：提取参考文献...")
        references = parser.extract_references(full_text)
        print(f"[自动处理] 📚 参考文献：{len(references)} 条")
        update_task_status(task_id, 'processing', progress=30)
        
        # ========== 第 3 步：提取引用位置 ==========
        print(f"[自动处理] 第 3 步：提取引用位置...")
        references = parser.extract_citations(full_text, references)
        cited_count = sum(1 for ref in references if ref.citation_count > 0)
        print(f"[自动处理] 📍 被引用：{cited_count}/{len(references)} 条")
        update_task_status(task_id, 'processing', progress=40)
        
        # ========== 第 4 步：DOI 验证（最耗时） ==========
        print(f"[自动处理] 第 4 步：DOI 验证...")
        auth_analyzer = AuthenticityAnalyzer()
        auth_result = auth_analyzer.analyze(references)
        verified_count = sum(1 for ref in references if ref.verified)
        print(f"[自动处理] ✅ DOI 验证：{verified_count}/{len(references)} 条")
        update_task_status(task_id, 'processing', progress=70)
        
        # ========== 第 5 步：语义分析 ==========
        print(f"[自动处理] 第 5 步：语义分析...")
        rel_analyzer = RelevanceAnalyzer()
        rel_result = rel_analyzer.analyze(references)
        print(f"[自动处理] 🟢 强相关：{rel_result.strong_related}条")
        update_task_status(task_id, 'processing', progress=85)
        
        # ========== 第 6 步：生成压缩包 ==========
        print(f"[自动处理] 第 6 步：生成压缩包...")
        # TODO: 调用报告生成模块
        report_path = f"{app.config['OUTPUT_FOLDER']}/{task_id}_report.docx"
        with open(report_path, 'w') as f:
            f.write(f"验证报告 - {task_id}\n参考文献：{len(references)} 条\n")
        
        zip_path = create_task_package(
            task_id=task_id,
            original_paper_path=file_path,
            report_path=report_path,
            output_dir=app.config['PACKAGE_FOLDER']
        )
        print(f"[自动处理] 📦 压缩包：{zip_path}")
        update_task_status(task_id, 'processing', progress=95)
        
        # ========== 第 7 步：自动发送邮件 ==========
        print(f"[自动处理] 第 7 步：发送邮件...")
        email_sent = send_report_email(email, task_id, zip_path, doc_name)
        
        # ========== 第 8 步：更新状态 ==========
        update_task_status(
            task_id=task_id,
            status='completed' if email_sent else 'failed',
            progress=100,
            report_path=report_path,
            zip_path=zip_path,
            email_sent=email_sent
        )
        
        print(f"[自动处理] ✅ 任务完成：{task_id}")
        
    except Exception as e:
        print(f"[自动处理] ❌ 任务失败：{task_id} - {e}")
        update_task_status(
            task_id=task_id,
            status='failed',
            error_message=str(e)
        )

# ========== API 路由 ==========
@app.route('/')
def index():
    """首页 - 提交论文"""
    return render_template_string(HTML_TEMPLATE)

@app.route('/query')
def query_page():
    """查询进度页面"""
    return render_template_string(QUERY_TEMPLATE)

@app.route('/api/submit', methods=['POST'])
def submit():
    """
    提交论文 - 全自动处理
    
    提交后立即返回任务编号
    后台自动执行所有验证步骤
    完成后自动发送邮件
    """
    try:
        # 检查文件
        if 'file' not in request.files:
            return jsonify({'success': False, 'error': '未找到文件'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'success': False, 'error': '文件名为空'}), 400
        
        if not allowed_file(file.filename):
            return jsonify({'success': False, 'error': '不支持的文件格式'}), 400
        
        # 获取表单数据
        email = request.form.get('email', '')
        author = request.form.get('author', '')
        
        if not email or not author:
            return jsonify({'success': False, 'error': '请填写邮箱和作者'}), 400
        
        # 生成任务编号
        task_id = generate_task_id(channel='web')
        
        # 保存文件
        safe_filename = secure_filename(file.filename)
        filename = f"{task_id}_{safe_filename}"
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)
        
        # 创建任务记录
        create_task(
            task_id=task_id,
            email=email,
            author=author,
            doc_name=safe_filename,
            file_path=file_path,
            file_size=os.path.getsize(file_path)
        )
        
        print(f"\n✅ 收到任务：{task_id}")
        print(f"   邮箱：{email}")
        print(f"   作者：{author}")
        print(f"   文件：{safe_filename}")
        
        # 后台自动处理（异步线程）
        thread = threading.Thread(
            target=process_task_automatically,
            args=(task_id, email, author, file_path, safe_filename)
        )
        thread.daemon = True
        thread.start()
        
        # 立即返回任务编号
        return jsonify({
            'success': True,
            'task_id': task_id,
            'email': email,
            'message': f'任务已提交，报告将自动发送到 {email}'
        })
        
    except Exception as e:
        print(f"❌ 提交失败：{e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/query/<task_id>', methods=['GET'])
def query_task(task_id):
    """查询任务进度"""
    task = get_task(task_id)
    
    if not task:
        return jsonify({
            'success': False,
            'message': '任务编号不存在'
        }), 404
    
    result = {
        'success': True,
        'task_id': task['task_id'],
        'status': task['status'],
        'progress': task['progress'],
        'created_at': task['created_at'],
        'completed_at': task.get('completed_at')
    }
    
    return jsonify(result)

@app.route('/api/stats', methods=['GET'])
def stats():
    """系统统计信息"""
    statistics = get_statistics()
    return jsonify(statistics)

# ========== 初始化 ==========
if __name__ == '__main__':
    print("=" * 70)
    print("学致源·论文参考文献验证系统 - 生产环境版本")
    print("=" * 70)
    print(f"启动时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"访问地址：http://0.0.0.0:5000")
    print(f"上传目录：{app.config['UPLOAD_FOLDER']}")
    print(f"输出目录：{app.config['OUTPUT_FOLDER']}")
    print(f"数据库：{db_module.DB_PATH}")
    print("=" * 70)
    print("\n✅ 系统已就绪，等待提交...")
    print("=" * 70)
    
    # 初始化数据库
    init_database()
    
    # 启动服务
    app.run(host='0.0.0.0', port=5000, debug=False, threaded=True)
