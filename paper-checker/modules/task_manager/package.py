#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
任务管理模块 - 压缩包生成
创建包含报告和原始论文的 ZIP 压缩包
"""

import zipfile
import os
from datetime import datetime


def create_task_package(task_id: str, 
                        original_paper_path: str, 
                        report_path: str,
                        output_dir: str,
                        include_readme: bool = True) -> str:
    """
    创建任务压缩包
    
    参数：
    - task_id: 任务编号
    - original_paper_path: 原始论文路径
    - report_path: 检测报告路径
    - output_dir: 压缩包输出目录
    - include_readme: 是否包含说明文件
    
    返回：压缩包路径
    """
    os.makedirs(output_dir, exist_ok=True)
    
    zip_path = os.path.join(output_dir, f'{task_id}.zip')
    
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        # 1. 添加原始论文（必须）
        if os.path.exists(original_paper_path):
            zipf.write(
                original_paper_path, 
                '01_原始论文.docx'
            )
            print(f"   ✅ 已添加：01_原始论文.docx")
        else:
            print(f"   ⚠️ 警告：原始论文不存在 {original_paper_path}")
        
        # 2. 添加检测报告（必须）
        if os.path.exists(report_path):
            zipf.write(
                report_path, 
                '02_检测报告_完整验证报告.docx'
            )
            print(f"   ✅ 已添加：02_检测报告_完整验证报告.docx")
        else:
            print(f"   ⚠️ 警告：报告不存在 {report_path}")
        
        # 3. 添加说明文件（可选）
        if include_readme:
            readme_content = f"""学致源·学术诚信检测中心
====================================

任务编号：{task_id}
检测时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

压缩包内容：
------------------------------------
1. 01_原始论文.docx - 您上传的原始论文
2. 02_检测报告_完整验证报告.docx - V12 详细版检测报告

报告包含：
------------------------------------
✅ 文献真实性验证（CrossRef API）
✅ 上下文引用验证（句子边界检测）
✅ 语义相关性分析（10 要素对比）
✅ 综合评分

报告结构（V12 详细版 - 9 部分）：
------------------------------------
1. 📄 封面页
2. 📊 检测概览
3. ✅ 文献验证详情
4. 📝 引用验证
5. 🔍 语义相关性分析（10 要素对比）
6. ⚠️ 问题列表
7. 📝 修改建议
8. 📊 评分详情
9. ℹ️ 检测说明

学致源文化传播有限公司
版权所有 © 2026 Xuezhiyuan Culture Communication Co., Ltd.
"""
            zipf.writestr('README.txt', readme_content)
            print(f"   ✅ 已添加：README.txt")
    
    print(f"   ✅ 压缩包已创建：{zip_path}")
    return zip_path


if __name__ == '__main__':
    # 测试
    print("压缩包生成测试")
    print("需要提供测试文件路径")
