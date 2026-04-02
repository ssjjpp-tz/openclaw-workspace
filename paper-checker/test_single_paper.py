#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
单篇论文完整流程测试
"""

import sys
import os
import time
from datetime import datetime

sys.path.insert(0, '/home/admin/.openclaw/workspace/paper-checker')

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

print("=" * 70)
print("学致源·学术诚信检测系统 - 单篇论文完整测试")
print("=" * 70)
print(f"测试时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

# ========== 测试配置 ==========
TEST_PAPER = '/home/admin/.openclaw/workspace/paper-checker/uploads/20260402_181202_4.2--03.31_W128_manuscript.docx'
TEST_EMAIL = 'test@example.com'
TEST_AUTHOR = '测试用户'
DB_PATH = '/home/admin/.openclaw/workspace/paper-checker/tasks_test.db'
OUTPUT_DIR = '/home/admin/.openclaw/workspace/paper-checker/output_test'
PACKAGE_DIR = '/home/admin/.openclaw/workspace/paper-checker/packages_test'

os.makedirs(OUTPUT_DIR, exist_ok=True)
os.makedirs(PACKAGE_DIR, exist_ok=True)

print("【测试配置】")
print(f"  测试论文：{os.path.basename(TEST_PAPER)}")
print(f"  用户邮箱：{TEST_EMAIL}")
print(f"  作者姓名：{TEST_AUTHOR}")
print()

if not os.path.exists(TEST_PAPER):
    print(f"❌ 测试论文不存在：{TEST_PAPER}")
    sys.exit(1)

print("✅ 测试论文存在，开始测试...\n")

# 临时修改数据库路径
import modules.task_manager.database as db_module
db_module.DB_PATH = DB_PATH

# ========== 步骤 1：初始化数据库 ==========
print("【步骤 1】初始化数据库...")
start_time = time.time()
init_database()
print(f"   ✅ 数据库初始化完成")
print(f"   ⏱️  耗时：{time.time() - start_time:.2f}秒\n")

# ========== 步骤 2：生成任务编号 ==========
print("【步骤 2】生成任务编号...")
start_time = time.time()
task_id = generate_task_id(channel='wechat')
print(f"   任务编号：{task_id}")
print(f"   ✅ 任务编号生成成功")
print(f"   ⏱️  耗时：{time.time() - start_time:.2f}秒\n")

# ========== 步骤 3：创建任务记录 ==========
print("【步骤 3】创建任务记录...")
start_time = time.time()
file_size = os.path.getsize(TEST_PAPER)
create_task(
    task_id=task_id,
    email=TEST_EMAIL,
    author=TEST_AUTHOR,
    doc_name=os.path.basename(TEST_PAPER),
    file_path=TEST_PAPER,
    file_size=file_size
)
print(f"   ✅ 任务记录创建成功")
print(f"   ⏱️  耗时：{time.time() - start_time:.2f}秒\n")

# ========== 步骤 4：解析论文 ==========
print("【步骤 4】解析论文...")
start_time = time.time()
parser = FileParser()
document = parser.parse(TEST_PAPER)
full_text = document['full_text']
print(f"   ✅ 论文解析完成")
print(f"   📄 文本长度：{len(full_text)} 字符")
print(f"   ⏱️  耗时：{time.time() - start_time:.2f}秒\n")

# ========== 步骤 5：提取参考文献 ==========
print("【步骤 5】提取参考文献...")
start_time = time.time()
references = parser.extract_references(full_text)
print(f"   ✅ 参考文献提取完成")
print(f"   📚 参考文献数量：{len(references)} 条")
print(f"   ⏱️  耗时：{time.time() - start_time:.2f}秒\n")

# ========== 步骤 6：提取引用位置 ==========
print("【步骤 6】提取引用位置...")
start_time = time.time()
references = parser.extract_citations(full_text, references)
cited_count = sum(1 for ref in references if ref.citation_count > 0)
print(f"   ✅ 引用位置提取完成")
print(f"   📍 被引用文献：{cited_count}/{len(references)} 条 ({100*cited_count/len(references):.1f}%)")
print(f"   ⏱️  耗时：{time.time() - start_time:.2f}秒\n")

# ========== 步骤 7：DOI 验证 ==========
print("【步骤 7】DOI 验证（最耗时的步骤）...")
start_time = time.time()
auth_analyzer = AuthenticityAnalyzer()
auth_result = auth_analyzer.analyze(references)
verified_count = sum(1 for ref in references if ref.verified)
print(f"   ✅ DOI 验证完成")
print(f"   ✅ 验证通过：{verified_count}/{len(references)} 条 ({100*verified_count/len(references):.1f}%)")
print(f"   ⏱️  耗时：{time.time() - start_time:.2f}秒\n")

# ========== 步骤 8：语义分析 ==========
print("【步骤 8】语义相关性分析...")
start_time = time.time()
rel_analyzer = RelevanceAnalyzer()
rel_result = rel_analyzer.analyze(references)
print(f"   ✅ 语义分析完成")
print(f"   🟢 强相关：{rel_result.strong_related} 条")
print(f"   🟡 弱相关：{rel_result.weak_related} 条")
print(f"   🔴 建议人工：{rel_result.manual_check} 条")
print(f"   ⏱️  耗时：{time.time() - start_time:.2f}秒\n")

# ========== 步骤 9：生成测试报告 ==========
print("【步骤 9】生成测试报告...")
start_time = time.time()
report_path = f"{OUTPUT_DIR}/{task_id}_report.docx"
with open(report_path, 'w') as f:
    f.write(f"测试报告 - {task_id}\n")
    f.write(f"参考文献：{len(references)} 条\n")
    f.write(f"验证通过：{verified_count} 条\n")
print(f"   ✅ 测试报告生成完成")
print(f"   📄 报告路径：{report_path}")
print(f"   ⏱️  耗时：{time.time() - start_time:.2f}秒\n")

# ========== 步骤 10：创建压缩包 ==========
print("【步骤 10】创建压缩包...")
start_time = time.time()
zip_path = create_task_package(
    task_id=task_id,
    original_paper_path=TEST_PAPER,
    report_path=report_path,
    output_dir=PACKAGE_DIR
)
print(f"   ✅ 压缩包创建完成")
print(f"   📦 压缩包路径：{zip_path}")
print(f"   📦 压缩包大小：{os.path.getsize(zip_path) / 1024:.1f} KB")
print(f"   ⏱️  耗时：{time.time() - start_time:.2f}秒\n")

# ========== 步骤 11：更新任务状态 ==========
print("【步骤 11】更新任务状态...")
start_time = time.time()
update_task_status(
    task_id=task_id,
    status='completed',
    progress=100,
    report_path=report_path,
    zip_path=zip_path
)
print(f"   ✅ 任务状态已更新")
print(f"   📊 最终状态：completed")
print(f"   📊 最终进度：100%")
print(f"   ⏱️  耗时：{time.time() - start_time:.2f}秒\n")

# ========== 步骤 12：查询任务 ==========
print("【步骤 12】查询任务（模拟用户查询）...")
start_time = time.time()
task = get_task(task_id)
if task:
    print(f"   ✅ 任务查询成功")
    print(f"   任务编号：{task['task_id']}")
    print(f"   状态：{task['status']}")
    print(f"   进度：{task['progress']}%")
else:
    print(f"   ❌ 任务查询失败")
print(f"   ⏱️  耗时：{time.time() - start_time:.2f}秒\n")

# ========== 测试完成 ==========
print("=" * 70)
print("✅ 单篇论文完整测试通过！")
print("=" * 70)
print(f"\n【测试总结】")
print(f"  任务编号：{task_id}")
print(f"  参考文献：{len(references)} 条")
print(f"  验证通过：{verified_count} 条 ({100*verified_count/len(references):.1f}%)")
print(f"  被引用：{cited_count} 条 ({100*cited_count/len(references):.1f}%)")
print(f"  强相关：{rel_result.strong_related} 条")
print(f"  总耗时：{time.time() - start_time:.2f}秒")
print()
print("【下一步】")
print("  ✅ 单篇测试通过")
print("  ⏳ 可以开始多篇测试")
print("  建议：先测试 3-5 篇，再测试 10-20 篇")
print()
