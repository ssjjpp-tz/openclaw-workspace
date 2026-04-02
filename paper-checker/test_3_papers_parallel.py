#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
3 篇论文并行测试
测试并发处理能力
"""

import sys
import os
import time
import threading
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

# ========== 测试配置 ==========
TEST_PAPERS = [
    '/home/admin/.openclaw/workspace/paper-checker/uploads/20260402_181202_4.2--03.31_W128_manuscript.docx',
    '/home/admin/.openclaw/workspace/paper-checker/uploads/20260402_191617_20260402_181202_4.2--03.31_W128_manuscript.docx',
    '/home/admin/.openclaw/workspace/paper-checker/uploads/20260402_192526_20260402_181202_4.2--03.31_W128_manuscript.docx',
]

TEST_EMAIL = 'test@example.com'
TEST_AUTHOR = '测试用户'
DB_PATH = '/home/admin/.openclaw/workspace/paper-checker/tasks_parallel_test.db'
OUTPUT_DIR = '/home/admin/.openclaw/workspace/paper-checker/output_parallel_test'
PACKAGE_DIR = '/home/admin/.openclaw/workspace/paper-checker/packages_parallel_test'

os.makedirs(OUTPUT_DIR, exist_ok=True)
os.makedirs(PACKAGE_DIR, exist_ok=True)

# 临时修改数据库路径
import modules.task_manager.database as db_module
db_module.DB_PATH = DB_PATH

# ========== 测试结果统计 ==========
results = []
lock = threading.Lock()

# ========== 单篇处理函数 ==========
def process_paper(paper_path, paper_index):
    """处理单篇论文"""
    thread_name = f"Thread-{paper_index}"
    print(f"\n[{thread_name}] {'='*60}")
    print(f"[{thread_name}] 开始处理第 {paper_index} 篇论文")
    print(f"[{thread_name}] 文件：{os.path.basename(paper_path)}")
    print(f"[{thread_name}] {'='*60}\n")
    
    start_time = time.time()
    task_start = time.time()
    
    try:
        # 1. 生成任务编号
        task_id = generate_task_id(channel='wechat')
        print(f"[{thread_name}] 任务编号：{task_id}")
        
        # 2. 创建任务记录
        create_task(
            task_id=task_id,
            email=TEST_EMAIL,
            author=TEST_AUTHOR,
            doc_name=os.path.basename(paper_path),
            file_path=paper_path,
            file_size=os.path.getsize(paper_path)
        )
        
        # 3. 解析论文
        parser = FileParser()
        document = parser.parse(paper_path)
        full_text = document['full_text']
        
        # 4. 提取参考文献
        references = parser.extract_references(full_text)
        print(f"[{thread_name}] 📚 参考文献：{len(references)} 条")
        
        # 5. 提取引用位置
        references = parser.extract_citations(full_text, references)
        cited_count = sum(1 for ref in references if ref.citation_count > 0)
        print(f"[{thread_name}] 📍 被引用：{cited_count}/{len(references)} 条")
        
        # 6. DOI 验证（最耗时）
        print(f"[{thread_name}] 🔍 开始 DOI 验证...")
        auth_analyzer = AuthenticityAnalyzer()
        auth_result = auth_analyzer.analyze(references)
        verified_count = sum(1 for ref in references if ref.verified)
        print(f"[{thread_name}] ✅ DOI 验证完成：{verified_count}/{len(references)} 条")
        
        # 7. 语义分析
        print(f"[{thread_name}] 🧠 开始语义分析...")
        rel_analyzer = RelevanceAnalyzer()
        rel_result = rel_analyzer.analyze(references)
        print(f"[{thread_name}] ✅ 语义分析完成：强相关{rel_result.strong_related}条")
        
        # 8. 生成测试报告
        report_path = f"{OUTPUT_DIR}/{task_id}_report.docx"
        with open(report_path, 'w') as f:
            f.write(f"测试报告 - {task_id}\n")
            f.write(f"参考文献：{len(references)} 条\n")
            f.write(f"验证通过：{verified_count} 条\n")
        
        # 9. 创建压缩包
        zip_path = create_task_package(
            task_id=task_id,
            original_paper_path=paper_path,
            report_path=report_path,
            output_dir=PACKAGE_DIR
        )
        
        # 10. 更新任务状态
        update_task_status(
            task_id=task_id,
            status='completed',
            progress=100,
            report_path=report_path,
            zip_path=zip_path
        )
        
        # 计算耗时
        total_time = time.time() - task_start
        
        # 保存结果
        with lock:
            results.append({
                'index': paper_index,
                'task_id': task_id,
                'references': len(references),
                'verified': verified_count,
                'cited': cited_count,
                'strong': rel_result.strong_related,
                'weak': rel_result.weak_related,
                'manual': rel_result.manual_check,
                'time': total_time
            })
        
        print(f"\n[{thread_name}] {'='*60}")
        print(f"[{thread_name}] ✅ 第 {paper_index} 篇论文处理完成")
        print(f"[{thread_name}] ⏱️  总耗时：{total_time:.2f}秒 ({total_time/60:.1f}分钟)")
        print(f"[{thread_name}] {'='*60}\n")
        
    except Exception as e:
        print(f"\n[{thread_name}] ❌ 第 {paper_index} 篇论文处理失败：{e}\n")
        with lock:
            results.append({
                'index': paper_index,
                'error': str(e)
            })

# ========== 主程序 ==========
if __name__ == '__main__':
    print("=" * 70)
    print("学致源·学术诚信检测系统 - 3 篇论文并行测试")
    print("=" * 70)
    print(f"测试时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"测试论文：{len(TEST_PAPERS)} 篇")
    print(f"并发模式：3 篇同时处理")
    print("=" * 70)
    print()
    
    # 检查文件是否存在
    for i, paper in enumerate(TEST_PAPERS, 1):
        if not os.path.exists(paper):
            print(f"❌ 测试论文 {i} 不存在：{paper}")
            sys.exit(1)
        print(f"✅ 测试论文 {i}: {os.path.basename(paper)}")
    
    print()
    print("✅ 所有测试论文存在，开始并行测试...\n")
    
    # 初始化数据库
    print("【初始化】初始化数据库...")
    init_database()
    print("✅ 数据库初始化完成\n")
    
    # 记录开始时间
    total_start = time.time()
    
    # 创建并启动线程
    print("【并行处理】启动 3 个线程同时处理...\n")
    threads = []
    for i, paper in enumerate(TEST_PAPERS, 1):
        thread = threading.Thread(
            target=process_paper,
            args=(paper, i),
            name=f"Thread-{i}"
        )
        threads.append(thread)
        thread.start()
        time.sleep(0.5)  # 稍微错开启动时间
    
    # 等待所有线程完成
    print("【等待】等待所有线程完成...\n")
    for i, thread in enumerate(threads, 1):
        thread.join()
        print(f"✅ 线程 {i} 完成")
    
    # 计算总耗时
    total_time = time.time() - total_start
    
    # 打印汇总结果
    print("\n" + "=" * 70)
    print("✅ 3 篇论文并行测试完成！")
    print("=" * 70)
    print(f"\n【测试汇总】")
    print(f"  测试论文：{len(TEST_PAPERS)} 篇")
    print(f"  成功：{len([r for r in results if 'error' not in r])} 篇")
    print(f"  失败：{len([r for r in results if 'error' in r])} 篇")
    print(f"  总耗时：{total_time:.2f}秒 ({total_time/60:.1f}分钟)")
    print(f"  平均每篇：{total_time/len(TEST_PAPERS):.2f}秒")
    print()
    
    # 详细结果
    print("【详细结果】")
    print("-" * 70)
    print(f"{'论文':<6} {'任务编号':<25} {'文献':<6} {'验证':<6} {'引用':<6} {'强相关':<8} {'耗时':<10}")
    print("-" * 70)
    
    for r in sorted(results, key=lambda x: x['index']):
        if 'error' not in r:
            print(f"第{r['index']:<5} {r['task_id']:<25} {r['references']:<6} {r['verified']:<6} {r['cited']:<6} {r['strong']:<8} {r['time']:.1f}秒")
        else:
            print(f"第{r['index']:<5} ❌ 失败：{r['error']}")
    
    print("-" * 70)
    print()
    
    # 性能对比
    print("【性能对比】")
    avg_time = sum([r['time'] for r in results if 'error' not in r]) / len(results)
    print(f"  串行处理 3 篇预计：{avg_time * 3:.2f}秒 ({avg_time * 3 / 60:.1f}分钟)")
    print(f"  并行处理 3 篇实际：{total_time:.2f}秒 ({total_time / 60:.1f}分钟)")
    print(f"  效率提升：{avg_time * 3 / total_time:.2f}x")
    print()
    
    # 下一步建议
    print("【下一步建议】")
    if total_time < 120:
        print("  ✅ 3 篇并行测试通过，性能优秀！")
        print("  ⏳ 可以测试 5 篇并行")
    elif total_time < 180:
        print("  ✅ 3 篇并行测试通过，性能正常")
        print("  ⏳ 可以测试 5 篇并行（观察 API 限流）")
    else:
        print("  ⚠️ 3 篇并行耗时较长，可能遇到 API 限流")
        print("  ⏳ 建议保持 3 篇并发，或测试 5 篇观察情况")
    print()
