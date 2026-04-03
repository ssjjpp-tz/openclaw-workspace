#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
任务管理模块 - 数据库操作
负责任务的创建、查询、更新、删除
"""

import sqlite3
import os
from datetime import datetime, timedelta
from typing import Optional, Dict, List

# 数据库路径
DB_PATH = '/var/www/html/paper-checker/tasks_production.db'


def get_db_connection():
    """获取数据库连接"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_database():
    """
    初始化数据库表结构
    
    创建任务表，包含所有必要字段
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # 检查表是否存在
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='tasks'")
    table_exists = cursor.fetchone() is not None
    
    if table_exists:
        # 表已存在，删除重建（测试用）
        cursor.execute('DROP TABLE tasks')
        print("   📝 删除旧表，重新创建...")
    
    cursor.execute('''
    CREATE TABLE tasks (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        
        -- 唯一标识
        task_id TEXT UNIQUE NOT NULL,
        
        -- 用户信息
        email TEXT NOT NULL,
        author TEXT NOT NULL,
        
        -- 任务信息
        doc_name TEXT NOT NULL,
        file_path TEXT NOT NULL,
        file_size INTEGER,
        
        -- 任务状态
        status TEXT DEFAULT 'pending',
        progress INTEGER DEFAULT 0,
        error_message TEXT,
        
        -- 处理结果
        report_path TEXT,
        zip_path TEXT,
        email_sent BOOLEAN DEFAULT FALSE,
        
        -- 时间戳
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        started_at DATETIME,
        completed_at DATETIME,
        expires_at DATETIME
    )
    ''')
    
    # 创建索引
    cursor.execute('CREATE INDEX idx_task_id ON tasks(task_id)')
    cursor.execute('CREATE INDEX idx_email ON tasks(email)')
    cursor.execute('CREATE INDEX idx_status ON tasks(status)')
    cursor.execute('CREATE INDEX idx_expires_at ON tasks(expires_at)')
    
    conn.commit()
    conn.close()
    
    print(f"✅ 数据库初始化完成：{DB_PATH}")


def create_task(task_id: str, email: str, author: str, doc_name: str, file_path: str, file_size: int = None) -> str:
    """
    创建新任务
    
    参数：
    - task_id: 任务编号（唯一）
    - email: 用户邮箱
    - author: 作者姓名
    - doc_name: 文档名称
    - file_path: 文件路径
    - file_size: 文件大小（字节）
    
    返回：任务编号
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    expires_at = datetime.now() + timedelta(days=7)  # 7 天后过期
    
    cursor.execute('''
    INSERT INTO tasks (
        task_id, email, author, doc_name, file_path, file_size,
        status, progress, created_at, expires_at
    ) VALUES (?, ?, ?, ?, ?, ?, 'pending', 0, ?, ?)
    ''', (task_id, email, author, doc_name, file_path, file_size, datetime.now(), expires_at))
    
    conn.commit()
    conn.close()
    
    print(f"✅ 任务已创建：{task_id}")
    return task_id


def get_task(task_id: str) -> Optional[Dict]:
    """
    查询任务详情
    
    参数：
    - task_id: 任务编号
    
    返回：任务信息字典，如果不存在返回 None
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
    SELECT * FROM tasks WHERE task_id = ?
    ''', (task_id,))
    
    row = cursor.fetchone()
    conn.close()
    
    if row:
        return dict(row)
    else:
        return None


def update_task_status(task_id: str, status: str, progress: int = None, 
                       error_message: str = None, report_path: str = None, 
                       zip_path: str = None) -> bool:
    """
    更新任务状态
    
    参数：
    - task_id: 任务编号
    - status: 新状态（pending/processing/completed/failed）
    - progress: 进度（0-100）
    - error_message: 错误信息
    - report_path: 报告路径
    - zip_path: 压缩包路径
    
    返回：是否更新成功
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # 构建更新 SQL
    updates = ['status = ?']
    params = [status]
    
    if progress is not None:
        updates.append('progress = ?')
        params.append(progress)
    
    if error_message is not None:
        updates.append('error_message = ?')
        params.append(error_message)
    
    if report_path is not None:
        updates.append('report_path = ?')
        params.append(report_path)
    
    if zip_path is not None:
        updates.append('zip_path = ?')
        params.append(zip_path)
    
    # 如果状态变为 processing，记录开始时间
    if status == 'processing':
        updates.append('started_at = ?')
        params.append(datetime.now())
    
    # 如果状态变为 completed，记录完成时间
    if status == 'completed':
        updates.append('completed_at = ?')
        params.append(datetime.now())
    
    params.append(task_id)
    
    sql = f"UPDATE tasks SET {', '.join(updates)} WHERE task_id = ?"
    
    cursor.execute(sql, params)
    conn.commit()
    
    updated = cursor.rowcount > 0
    conn.close()
    
    if updated:
        print(f"✅ 任务状态已更新：{task_id} → {status}")
    else:
        print(f"❌ 任务更新失败：{task_id}")
    
    return updated


def get_user_tasks(email: str) -> List[Dict]:
    """
    获取用户的所有任务
    
    参数：
    - email: 用户邮箱
    
    返回：任务列表
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
    SELECT task_id, doc_name, status, progress, created_at, completed_at
    FROM tasks
    WHERE email = ?
    ORDER BY created_at DESC
    ''', (email,))
    
    rows = cursor.fetchall()
    conn.close()
    
    return [dict(row) for row in rows]


def cleanup_expired_tasks() -> int:
    """
    清理过期任务（7 天前）
    
    返回：删除的任务数量
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
    DELETE FROM tasks
    WHERE expires_at < ?
    ''', (datetime.now(),))
    
    deleted_count = cursor.rowcount
    conn.commit()
    conn.close()
    
    if deleted_count > 0:
        print(f"✅ 已清理 {deleted_count} 个过期任务")
    
    return deleted_count


def get_statistics() -> Dict:
    """
    获取任务统计信息
    
    返回：统计信息字典
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    stats = {}
    
    # 总任务数
    cursor.execute('SELECT COUNT(*) as count FROM tasks')
    stats['total'] = cursor.fetchone()['count']
    
    # 按状态统计
    cursor.execute('''
    SELECT status, COUNT(*) as count
    FROM tasks
    GROUP BY status
    ''')
    stats['by_status'] = {row['status']: row['count'] for row in cursor.fetchall()}
    
    # 今日任务数
    cursor.execute('''
    SELECT COUNT(*) as count FROM tasks
    WHERE DATE(created_at) = DATE('now')
    ''')
    stats['today'] = cursor.fetchone()['count']
    
    # 平均处理时间（分钟）
    cursor.execute('''
    SELECT AVG(JULIANDAY(completed_at) - JULIANDAY(started_at)) * 24 * 60 as avg_minutes
    FROM tasks
    WHERE status = 'completed' AND started_at IS NOT NULL
    ''')
    result = cursor.fetchone()
    stats['avg_process_time'] = round(result['avg_minutes'], 2) if result['avg_minutes'] else 0
    
    conn.close()
    
    return stats


# 初始化数据库
if __name__ == '__main__':
    init_database()
    print("数据库初始化完成！")
