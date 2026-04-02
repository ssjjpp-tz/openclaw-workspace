#!/bin/bash
# 修改前检查脚本
# 在修改代码前运行，确保不会误删对方功能

set -e

echo "========================================"
echo "🔍 修改前检查"
echo "========================================"
echo ""

# 1. 检查当前分支
CURRENT_BRANCH=$(git branch --show-current)
echo "📍 当前分支：$CURRENT_BRANCH"

if [ "$CURRENT_BRANCH" == "main" ]; then
  echo "⚠️  警告：你在 main 分支上！"
  echo "⚠️  main 分支禁止直接修改，必须通过 PR"
  echo ""
  echo "建议操作："
  echo "  1. 切换到你的分支（wechat 或 web）"
  echo "     git checkout wechat  # 或 web"
  echo "  2. 在你的分支上开发"
  echo "  3. 创建 PR 到 main"
  echo ""
  exit 1
fi

# 2. 检查修改的文件
echo ""
echo "📝 待修改的文件："
CHANGED_FILES=$(git diff --name-only 2>/dev/null || echo "")

if [ -z "$CHANGED_FILES" ]; then
  echo "   (暂无修改)"
else
  echo "$CHANGED_FILES" | while read -r file; do
    echo "   - $file"
  done
fi

# 3. 检查是否修改了受保护的文件
echo ""
echo "🔍 检查受保护文件..."

PROTECTED_FILES=(
  "config.wechat.py"
  "app.wechat.py"
  "uploads_wechat/"
  "output_wechat/"
  "packages_wechat/"
)

VIOLATION=false

for file in "${PROTECTED_FILES[@]}"; do
  if echo "$CHANGED_FILES" | grep -q "$file"; then
    echo ""
    echo "⚠️  警告：试图修改微信端受保护文件：$file"
    echo "⚠️  需要微信端 Agent（小龙女二代）审核！"
    VIOLATION=true
  fi
done

if [ "$VIOLATION" == "true" ]; then
  echo ""
  echo "❌ 检测到受保护文件修改"
  echo ""
  echo "请选择："
  echo "  1. 取消修改（推荐）"
  echo "  2. 继续修改（需要微信端 Agent 确认）"
  echo ""
  echo "是否继续？(y/N)"
  read -r response
  
  if [[ ! "$response" =~ ^[Yy]$ ]]; then
    echo ""
    echo "✅ 已取消修改"
    echo ""
    echo "建议操作："
    echo "  1. 恢复修改：git checkout -- ."
    echo "  2. 联系微信端 Agent 确认"
    echo "  3. 确认后再次运行此脚本"
    exit 1
  fi
fi

# 4. 检查是否备份
echo ""
echo "💾 备份检查..."

LAST_COMMIT=$(git log --oneline -1)
echo "最近提交：$LAST_COMMIT"

echo ""
echo "建议创建备份分支："
echo "  git checkout -b backup-before-$(date +%Y%m%d_%H%M%S)"
echo ""

# 5. 检查清单
echo "========================================"
echo "📋 修改前检查清单"
echo "========================================"
echo ""

QUESTIONS=(
  "我在正确的分支上吗？"
  "我修改的文件属于我的模块吗？"
  "如果要修改对方模块，已经沟通过了吗？"
  "如果要修改 main 分支，创建 PR 了吗？"
  "已经通知对方审核了吗？"
  "已经备份当前版本了吗？"
)

for i in "${!QUESTIONS[@]}"; do
  echo "$((i+1)). ${QUESTIONS[$i]}"
done

echo ""
echo "✅ 检查完成"
echo ""
echo "如果以上问题都确认无误，可以继续修改"
echo "否则请先解决相关问题"
echo ""
