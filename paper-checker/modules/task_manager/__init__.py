#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
任务管理模块
负责任务的创建、查询、更新、删除、打包
"""

from .database import (
    init_database,
    create_task,
    get_task,
    update_task_status,
    get_user_tasks,
    cleanup_expired_tasks,
    get_statistics
)

from .generator import (
    generate_task_id,
    validate_task_id
)

from .package import (
    create_task_package
)

__all__ = [
    # 数据库操作
    'init_database',
    'create_task',
    'get_task',
    'update_task_status',
    'get_user_tasks',
    'cleanup_expired_tasks',
    'get_statistics',
    
    # 编号生成
    'generate_task_id',
    'validate_task_id',
    
    # 压缩包生成
    'create_task_package',
]
