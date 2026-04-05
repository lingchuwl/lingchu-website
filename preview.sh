#!/bin/bash

# 零初科技官网本地预览脚本

echo "🌐 启动零初科技官网本地预览..."

# 检查是否安装了Python
if command -v python3 &> /dev/null; then
    python_cmd="python3"
elif command -v python &> /dev/null; then
    python_cmd="python"
else
    echo "❌ 未找到Python，请先安装Python"
    exit 1
fi

# 检查是否在正确的目录
if [ ! -f "index.html" ]; then
    echo "❌ 错误：请在网站根目录运行此脚本"
    exit 1
fi

# 获取本地IP地址
local_ip=$(hostname -I | awk '{print $1}')

echo ""
echo "📱 网站将在以下地址打开："
echo "   本地地址：http://localhost:8000"
echo "   网络地址：http://$local_ip:8000"
echo ""
echo "🔄 按 Ctrl+C 停止服务器"
echo ""

# 启动HTTP服务器
$python_cmd -m http.server 8000