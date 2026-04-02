#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
任务管理模块 - 任务编号生成
生成唯一的任务编号

支持多端独立：
- 微信端：TASK-WX-YYYYMMDD-XXXXXX
- 网页端：TASK-WEB-YYYYMMDD-XXXXXX
- 通用：TASK-YYYYMMDD-XXXXXX
"""

import uuid
from datetime import datetime


def generate_task_id(channel: str = 'wechat') -> str:
    """
    生成唯一任务编号
    
    格式：{PREFIX}-YYYYMMDD-XXXXXX
    - PREFIX: 渠道前缀（TASK-WX/TASK-WEB/TASK）
    - YYYYMMDD: 日期（8 位）
    - XXXXXX: 6 位随机字符（确保唯一性）
    
    示例：
    - TASK-WX-20260402-A3F5B2  (微信端)
    - TASK-WEB-20260402-9C8D1E (网页端)
    - TASK-20260402-B61866     (通用)
    
    参数：
    - channel: 渠道标识（wechat/web/common）
    
    返回：任务编号字符串
    """
    # 渠道前缀映射
    prefix_map = {
        'wechat': 'TASK-WX',
        'web': 'TASK-WEB',
        'common': 'TASK'
    }
    
    prefix = prefix_map.get(channel.lower(), 'TASK')
    date_str = datetime.now().strftime('%Y%m%d')
    unique_id = uuid.uuid4().hex[:6].upper()
    
    return f"{prefix}-{date_str}-{unique_id}"


def validate_task_id(task_id: str) -> bool:
    """
    验证任务编号格式是否正确
    
    参数：
    - task_id: 任务编号
    
    返回：是否正确
    """
    import re
    pattern = r'^TASK-\d{8}-[A-F0-9]{6}$'
    return bool(re.match(pattern, task_id))


if __name__ == '__main__':
    # 测试生成
    print("生成 10 个任务编号测试唯一性：")
    for i in range(10):
        task_id = generate_task_id()
        valid = validate_task_id(task_id)
        print(f"  {i+1}. {task_id} - {'✅ 格式正确' if valid else '❌ 格式错误'}")
