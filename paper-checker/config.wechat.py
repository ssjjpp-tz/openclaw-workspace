#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
微信端独立配置
所有微信端特有的配置都在这里
"""

import os

# ========== 基础配置 ==========
VERSION = 'v1.0-wechat'
CHANNEL = 'wechat'  # 标识微信端

# ========== 数据库配置 ==========
# 微信端独立数据库，不与网页端冲突
DB_PATH = '/home/admin/.openclaw/workspace/paper-checker/tasks_wechat.db'

# ========== 目录配置 ==========
# 微信端独立的目录结构
BASE_DIR = '/home/admin/.openclaw/workspace/paper-checker'

# 上传目录（微信端独立）
UPLOAD_DIR = os.path.join(BASE_DIR, 'uploads_wechat')
os.makedirs(UPLOAD_DIR, exist_ok=True)

# 输出目录（微信端独立）
OUTPUT_DIR = os.path.join(BASE_DIR, 'output_wechat')
os.makedirs(OUTPUT_DIR, exist_ok=True)

# 压缩包目录（微信端独立）
PACKAGE_DIR = os.path.join(BASE_DIR, 'packages_wechat')
os.makedirs(PACKAGE_DIR, exist_ok=True)

# ========== 邮件配置 ==========
SMTP_HOST = 'smtp.163.com'
SMTP_PORT = 465
SMTP_USER = 'tlsjp@163.com'
SMTP_PASS = 'GFs4j38vb6eEEBvG'  # 需要替换为实际密码
SENDER_NAME = '学致源检测中心（微信端）'

# ========== 任务编号配置 ==========
# 微信端任务编号前缀（与网页端区分）
TASK_ID_PREFIX = 'TASK-WX-'  # TASK-WX-20260402-XXXXXX

# ========== 过期配置 ==========
# 任务保留天数
TASK_EXPIRE_DAYS = 7

# ========== 功能开关 ==========
# 微信端特有功能
ENABLE_WECHAT_FEATURES = {
    'auto_send_email': True,      # 自动发送邮件
    'progress_notification': True, # 进度通知
    'wechat_template': True,       # 微信端报告模板
}

# ========== 日志配置 ==========
LOG_DIR = os.path.join(BASE_DIR, 'logs_wechat')
os.makedirs(LOG_DIR, exist_ok=True)
LOG_FILE = os.path.join(LOG_DIR, 'wechat.log')
LOG_LEVEL = 'INFO'

# ========== 测试配置 ==========
TEST_MODE = False
TEST_EMAIL = 'test@example.com'

# ========== 打印配置信息 ==========
if __name__ == '__main__':
    print("=" * 70)
    print("微信端配置信息")
    print("=" * 70)
    print(f"版本：{VERSION}")
    print(f"渠道：{CHANNEL}")
    print(f"数据库：{DB_PATH}")
    print(f"上传目录：{UPLOAD_DIR}")
    print(f"输出目录：{OUTPUT_DIR}")
    print(f"任务编号前缀：{TASK_ID_PREFIX}")
    print(f"任务保留天数：{TASK_EXPIRE_DAYS} 天")
    print("=" * 70)
