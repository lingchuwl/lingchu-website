#!/bin/bash

# 零初科技官网部署检查脚本

echo "=========================================="
echo "🔍 零初科技官方网站部署检查"
echo "=========================================="
echo ""

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

print_success() { echo -e "${GREEN}✅ $1${NC}"; }
print_error() { echo -e "${RED}❌ $1${NC}"; }
print_info() { echo -e "${BLUE}ℹ️  $1${NC}"; }
print_warning() { echo -e "${YELLOW}⚠️  $1${NC}"; }

# 检查1：网站文件完整性
echo "1. 检查网站文件完整性..."
if [ ! -f "index.html" ]; then
    print_error "index.html 文件不存在"
else
    file_size=$(stat -c%s "index.html")
    if [ $file_size -lt 10000 ]; then
        print_warning "index.html 文件过小 ($file_size 字节)"
    else
        print_success "index.html 文件正常 ($file_size 字节)"
    fi
fi

# 检查关键文件
required_files=("index.html" "css/style.css" "js/main.js" "README.md")
for file in "${required_files[@]}"; do
    if [ -f "$file" ]; then
        print_success "$file 存在"
    else
        print_error "$file 不存在"
    fi
done

echo ""

# 检查2：Git状态
echo "2. 检查Git状态..."
if [ -d ".git" ]; then
    git_status=$(git status --porcelain)
    if [ -z "$git_status" ]; then
        print_success "Git仓库干净，无未提交更改"
    else
        print_warning "Git仓库有未提交的更改"
        echo "$git_status"
    fi
    
    # 检查远程仓库
    remote_url=$(git remote get-url origin 2>/dev/null)
    if [ -n "$remote_url" ]; then
        print_success "远程仓库配置: $remote_url"
    else
        print_warning "未配置远程仓库"
    fi
else
    print_error "不是Git仓库"
fi

echo ""

# 检查3：网站功能检查
echo "3. 检查网站功能..."

# 检查HTML结构
if grep -q "<!DOCTYPE html>" index.html; then
    print_success "HTML文档类型正确"
else
    print_error "HTML文档类型错误"
fi

if grep -q "<title>零初科技" index.html; then
    print_success "网站标题正确"
else
    print_error "网站标题错误"
fi

# 检查响应式设计
if grep -q "viewport" index.html; then
    print_success "响应式viewport配置"
else
    print_error "缺少响应式viewport配置"
fi

# 检查关键部分
sections=("核心价值" "产品优势" "定价方案" "成功案例" "联系我们")
for section in "${sections[@]}"; do
    if grep -q "$section" index.html; then
        print_success "包含 '$section' 部分"
    else
        print_error "缺少 '$section' 部分"
    fi
done

echo ""

# 检查4：部署准备状态
echo "4. 检查部署准备状态..."

# 检查部署脚本
if [ -f "AUTO_DEPLOY.sh" ] && [ -x "AUTO_DEPLOY.sh" ]; then
    print_success "自动部署脚本就绪"
else
    print_error "自动部署脚本不可用"
fi

if [ -f "deploy-to-github.sh" ] && [ -x "deploy-to-github.sh" ]; then
    print_success "GitHub部署脚本就绪"
else
    print_error "GitHub部署脚本不可用"
fi

if [ -f "preview.sh" ] && [ -x "preview.sh" ]; then
    print_success "本地预览脚本就绪"
else
    print_error "本地预览脚本不可用"
fi

# 检查文档
if [ -f "DEPLOYMENT_GUIDE.md" ]; then
    guide_size=$(stat -c%s "DEPLOYMENT_GUIDE.md")
    if [ $guide_size -gt 1000 ]; then
        print_success "部署指南完整 ($guide_size 字节)"
    else
        print_warning "部署指南可能不完整"
    fi
else
    print_error "缺少部署指南"
fi

if [ -f "GITHUB_SETUP_GUIDE.md" ]; then
    print_success "GitHub设置指南就绪"
else
    print_error "缺少GitHub设置指南"
fi

echo ""

# 检查5：本地预览测试
echo "5. 测试本地预览..."
read -p "是否启动本地预览测试？(y/n): " start_preview
if [[ $start_preview =~ ^[Yy]$ ]]; then
    print_info "启动本地预览服务器..."
    python3 -m http.server 8000 &
    server_pid=$!
    sleep 2
    
    # 测试访问
    if curl -s -o /dev/null -w "%{http_code}" http://localhost:8000/ | grep -q "200"; then
        print_success "本地预览服务器运行正常"
        print_info "访问地址: http://localhost:8000"
        print_info "按 Ctrl+C 停止服务器"
        
        # 等待用户停止
        read -p "按回车键停止服务器..." 
        kill $server_pid 2>/dev/null
        print_success "服务器已停止"
    else
        print_error "本地预览服务器启动失败"
        kill $server_pid 2>/dev/null
    fi
else
    print_info "跳过本地预览测试"
fi

echo ""

# 总结报告
echo "=========================================="
echo "📊 部署检查总结报告"
echo "=========================================="
echo ""

# 显示GitHub部署信息
if [ -f "DEPLOYMENT_COMPLETE.txt" ]; then
    print_success "检测到已完成的部署记录"
    echo ""
    cat DEPLOYMENT_COMPLETE.txt
else
    print_info "尚未部署到GitHub"
    echo ""
    echo "📋 部署前准备清单："
    echo "   1. 注册GitHub账号（免费）"
    echo "   2. 创建仓库：lingchu-website"
    echo "   3. 获取访问令牌"
    echo "   4. 运行 ./AUTO_DEPLOY.sh"
    echo ""
    echo "📚 详细指南："
    echo "   • 查看 GITHUB_SETUP_GUIDE.md"
    echo "   • 查看 DEPLOYMENT_GUIDE.md"
fi

echo ""
echo "🔧 立即操作选项："
echo "   1. 查看部署指南：cat DEPLOYMENT_GUIDE.md | head -50"
echo "   2. 启动本地预览：./preview.sh"
echo "   3. 部署到GitHub：./AUTO_DEPLOY.sh"
echo "   4. 检查网站文件：ls -la"
echo ""
echo "📞 技术支持："
echo "   • 邮箱：contact@lingchu.com"
echo "   • 电话：400-123-4567"
echo ""
echo "=========================================="
echo "🎯 零初科技官方网站部署检查完成"
echo "=========================================="