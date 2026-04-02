#!/bin/bash
# 学致源论文验证系统 - 生产环境部署脚本
# 自动部署到服务器

set -e

echo "========================================"
echo "学致源论文验证系统 - 部署脚本"
echo "========================================"
echo ""

# 配置
DEPLOY_DIR="/var/www/html/referencecheck"
BACKUP_DIR="/backup/referencecheck_$(date +%Y%m%d_%H%M%S)"
PYTHON_VERSION="3.6"

echo "【1/5】检查 Python 版本..."
python3 --version || {
    echo "❌ Python3 未安装，请先安装：sudo apt install python3"
    exit 1
}

echo "✅ Python 版本检查通过"
echo ""

echo "【2/5】安装依赖..."
pip3 install flask docx python-docx || {
    echo "❌ 依赖安装失败"
    exit 1
}
echo "✅ 依赖安装完成"
echo ""

echo "【3/5】备份现有文件..."
if [ -d "$DEPLOY_DIR" ]; then
    mkdir -p "$BACKUP_DIR"
    cp -r "$DEPLOY_DIR"/* "$BACKUP_DIR"/ 2>/dev/null || true
    echo "✅ 已备份到：$BACKUP_DIR"
else
    echo "ℹ️  首次部署，无需备份"
    mkdir -p "$DEPLOY_DIR"
fi
echo ""

echo "【4/5】部署文件..."
# 复制生产环境文件
cp app.production.py "$DEPLOY_DIR/app.py"
cp -r modules/ "$DEPLOY_DIR/"
cp -r parser/ "$DEPLOY_DIR/"
cp -r analyzer/ "$DEPLOY_DIR/"
cp -r models/ "$DEPLOY_DIR/"

# 创建必要目录
mkdir -p "$DEPLOY_DIR/uploads"
mkdir -p "$DEPLOY_DIR/output"
mkdir -p "$DEPLOY_DIR/packages"

# 设置权限
chmod +x "$DEPLOY_DIR/app.py"
chmod 755 "$DEPLOY_DIR/uploads"
chmod 755 "$DEPLOY_DIR/output"
chmod 755 "$DEPLOY_DIR/packages"

echo "✅ 文件部署完成"
echo ""

echo "【5/5】配置系统服务..."
# 创建 systemd 服务文件
cat > /etc/systemd/system/xueziyuan.service << EOF
[Unit]
Description=学致源论文验证系统
After=network.target

[Service]
Type=simple
User=www-data
WorkingDirectory=$DEPLOY_DIR
ExecStart=/usr/bin/python3 $DEPLOY_DIR/app.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

# 重新加载 systemd
systemctl daemon-reload

# 启用服务
systemctl enable xueziyuan

# 启动服务
systemctl start xueziyuan

echo "✅ 系统服务配置完成"
echo ""

echo "========================================"
echo "✅ 部署完成！"
echo "========================================"
echo ""
echo "访问地址：http://$(hostname -I | awk '{print $1}'):5000"
echo "服务状态：systemctl status xueziyuan"
echo "查看日志：journalctl -u xueziyuan -f"
echo ""
echo "========================================"
