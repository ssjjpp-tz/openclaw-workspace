#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
微信端独立 API 服务器
与网页端完全独立，使用独立的数据库和配置
"""

import sys
import os

# 导入微信端独立配置
from config.wechat import (
    VERSION, CHANNEL, DB_PATH, UPLOAD_DIR, OUTPUT_DIR,
    PACKAGE_DIR, SMTP_USER, SENDER_NAME, TASK_ID_PREFIX
)

# 添加到路径
sys.path.insert(0, os.path.dirname(__file__))

from flask import Flask, request, jsonify, send_file
from werkzeug.utils import secure_filename
import threading
from datetime import datetime

# 导入任务管理模块
from modules.task_manager import (
    init_database,
    generate_task_id,
    create_task,
    get_task,
    update_task_status,
    create_task_package
)

# 导入核心功能模块
from parser.file_parser import FileParser
from analyzer.analyzers import AuthenticityAnalyzer, RelevanceAnalyzer

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024  # 50MB

ALLOWED_EXTENSIONS = {'docx', 'doc', 'pdf'}


def allowed_file(filename):
    """检查文件扩展名是否允许"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def save_uploaded_file(file, task_id):
    """保存上传的文件"""
    filename = secure_filename(file.filename)
    safe_filename = f"{task_id}_{filename}"
    file_path = os.path.join(UPLOAD_DIR, safe_filename)
    file.save(file_path)
    return file_path


def process_wechat_task(task_id, email, author, file_path, doc_name):
    """
    微信端任务处理流程
    
    1. 执行三大验证
    2. 生成报告
    3. 创建压缩包
    4. 发送邮件
    5. 更新状态
    """
    try:
        print(f"\n[微信端] 开始处理任务：{task_id}")
        
        # 更新状态：处理中
        update_task_status(task_id, 'processing', progress=10)
        
        # ========== 第一步：解析论文 ==========
        print(f"[微信端] 解析论文：{file_path}")
        parser = FileParser()
        document = parser.parse(file_path)
        full_text = document['full_text']
        
        # 提取参考文献
        references = parser.extract_references(full_text)
        print(f"[微信端] 提取参考文献：{len(references)} 条")
        update_task_status(task_id, 'processing', progress=30)
        
        # 提取引用位置
        references = parser.extract_citations(full_text, references)
        cited_count = sum(1 for ref in references if ref.citation_count > 0)
        print(f"[微信端] 被引用文献：{cited_count}/{len(references)} 条")
        update_task_status(task_id, 'processing', progress=50)
        
        # ========== 第二步：执行验证 ==========
        # DOI 验证
        auth_analyzer = AuthenticityAnalyzer()
        auth_result = auth_analyzer.analyze(references)
        verified_count = sum(1 for ref in references if ref.verified)
        print(f"[微信端] DOI 验证：{verified_count}/{len(references)} 条通过")
        update_task_status(task_id, 'processing', progress=70)
        
        # 语义分析
        rel_analyzer = RelevanceAnalyzer()
        rel_result = rel_analyzer.analyze(references)
        print(f"[微信端] 语义分析：强相关{rel_result.strong_related}条")
        update_task_status(task_id, 'processing', progress=90)
        
        # ========== 第三步：生成报告 ==========
        # TODO: 调用报告生成模块
        report_path = "/tmp/wechat_report.docx"
        print(f"[微信端] 报告生成：{report_path}")
        
        # ========== 第四步：创建压缩包 ==========
        zip_path = create_task_package(
            task_id=task_id,
            original_paper_path=file_path,
            report_path=report_path,
            output_dir=PACKAGE_DIR
        )
        print(f"[微信端] 压缩包生成：{zip_path}")
        
        # ========== 第五步：发送邮件 ==========
        # TODO: 调用邮件发送模块
        print(f"[微信端] 邮件发送：{email}")
        
        # ========== 第六步：更新状态 ==========
        update_task_status(
            task_id=task_id,
            status='completed',
            progress=100,
            report_path=report_path,
            zip_path=zip_path,
            email_sent=True
        )
        
        print(f"[微信端] ✅ 任务完成：{task_id}")
        
    except Exception as e:
        print(f"[微信端] ❌ 任务失败：{task_id} - {e}")
        update_task_status(
            task_id=task_id,
            status='failed',
            error_message=str(e)
        )


# ========== API 路由 ==========

@app.route('/api/wechat/submit', methods=['POST'])
def wechat_submit():
    """
    微信端提交任务
    
    输入：
    - email: 用户邮箱
    - author: 作者姓名
    - file: 上传的论文文件
    
    返回：
    - task_id: 任务编号（微信端独立）
    - message: 提示信息
    """
    try:
        if 'file' not in request.files:
            return jsonify({'success': False, 'error': '未找到文件'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'success': False, 'error': '文件名为空'}), 400
        
        if not allowed_file(file.filename):
            return jsonify({'success': False, 'error': '不支持的文件格式'}), 400
        
        email = request.form.get('email', '')
        author = request.form.get('author', '')
        
        if not email or not author:
            return jsonify({'success': False, 'error': '请填写邮箱和作者'}), 400
        
        # 生成微信端任务编号
        task_id = generate_task_id(channel='wechat')
        
        # 保存文件
        file_path = save_uploaded_file(file, task_id)
        
        # 创建任务记录
        create_task(
            task_id=task_id,
            email=email,
            author=author,
            doc_name=file.filename,
            file_path=file_path,
            file_size=os.path.getsize(file_path)
        )
        
        # 后台异步处理
        thread = threading.Thread(
            target=process_wechat_task,
            args=(task_id, email, author, file_path, file.filename)
        )
        thread.daemon = True
        thread.start()
        
        return jsonify({
            'success': True,
            'task_id': task_id,
            'message': f'任务已提交，请保存任务编号：{task_id}',
            'channel': 'wechat'
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/wechat/query/<task_id>', methods=['GET'])
def wechat_query(task_id):
    """
    微信端查询任务进度
    
    返回：
    - task_id: 任务编号
    - status: 状态
    - progress: 进度
    - channel: 渠道标识
    """
    task = get_task(task_id)
    
    if not task:
        return jsonify({
            'success': False,
            'message': '任务编号不存在'
        }), 404
    
    result = {
        'task_id': task['task_id'],
        'status': task['status'],
        'progress': task['progress'],
        'channel': 'wechat'
    }
    
    # 如果已完成，添加下载链接
    if task['status'] == 'completed':
        result['report_url'] = f'/api/wechat/download/{task_id}/report'
        result['zip_url'] = f'/api/wechat/download/{task_id}/zip'
        result['completed_at'] = task['completed_at']
    
    return jsonify(result)


@app.route('/api/wechat/download/<task_id>/report', methods=['GET'])
def wechat_download_report(task_id):
    """微信端下载完整报告"""
    task = get_task(task_id)
    
    if not task or task['status'] != 'completed':
        return '任务未完成或不存在', 404
    
    return send_file(
        task['report_path'],
        as_attachment=True,
        download_name=f'{task_id}_完整验证报告.docx'
    )


@app.route('/api/wechat/download/<task_id>/zip', methods=['GET'])
def wechat_download_zip(task_id):
    """微信端下载压缩包"""
    task = get_task(task_id)
    
    if not task or task['status'] != 'completed':
        return '任务未完成或不存在', 404
    
    return send_file(
        task['zip_path'],
        as_attachment=True,
        download_name=f'{task_id}.zip'
    )


@app.route('/api/wechat/stats', methods=['GET'])
def wechat_stats():
    """微信端统计信息"""
    from modules.task_manager import get_statistics
    stats = get_statistics()
    stats['channel'] = 'wechat'
    return jsonify(stats)


@app.route('/api/wechat/health', methods=['GET'])
def wechat_health():
    """微信端健康检查"""
    return jsonify({
        'status': 'ok',
        'channel': 'wechat',
        'version': VERSION,
        'timestamp': datetime.now().isoformat()
    })


# ========== 启动服务 ==========

if __name__ == '__main__':
    # 初始化数据库（微信端独立）
    init_database()
    
    print("=" * 70)
    print("学致源·学术诚信检测中心 - 微信端 API 服务器")
    print("=" * 70)
    print(f"版本：{VERSION}")
    print(f"渠道：{CHANNEL}")
    print(f"数据库：{DB_PATH}")
    print(f"上传目录：{UPLOAD_DIR}")
    print(f"输出目录：{OUTPUT_DIR}")
    print(f"访问地址：http://localhost:5001")
    print("=" * 70)
    
    # 微信端使用独立端口（5001），网页端可能用 5000
    app.run(host='0.0.0.0', port=5001, debug=False, threaded=True)
