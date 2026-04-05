#!/bin/bash

# 零初科技官网全自动部署脚本

echo "=========================================="
echo "🚀 零初科技官方网站全自动部署"
echo "=========================================="
echo ""

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 函数：打印带颜色的消息
print_success() { echo -e "${GREEN}✅ $1${NC}"; }
print_error() { echo -e "${RED}❌ $1${NC}"; }
print_info() { echo -e "${BLUE}ℹ️  $1${NC}"; }
print_warning() { echo -e "${YELLOW}⚠️  $1${NC}"; }

# 检查环境
print_info "检查系统环境..."
if ! command -v git &> /dev/null; then
    print_error "Git未安装，请先安装Git"
    exit 1
fi

if ! command -v curl &> /dev/null; then
    print_error "curl未安装，请先安装curl"
    exit 1
fi

print_success "系统环境检查通过"

# 检查当前目录
if [ ! -f "index.html" ]; then
    print_error "错误：请在网站根目录运行此脚本"
    exit 1
fi

print_success "网站文件检查通过"

echo ""
echo "=========================================="
echo "📋 部署信息配置"
echo "=========================================="
echo ""

# 获取部署信息
read -p "1. 请输入GitHub用户名: " github_username
if [ -z "$github_username" ]; then
    print_error "GitHub用户名不能为空"
    exit 1
fi

read -p "2. 请输入仓库名称（默认为lingchu-website）: " repo_name
repo_name=${repo_name:-lingchu-website}

echo ""
print_info "是否使用自定义域名？"
read -p "3. 自定义域名（如www.lingchu.com，留空则不使用）: " custom_domain

echo ""
echo "=========================================="
echo "🔧 开始部署流程"
echo "=========================================="
echo ""

# 步骤1：清理和准备
print_info "步骤1：清理和准备Git仓库..."
git clean -fd 2>/dev/null
git reset --hard 2>/dev/null
print_success "Git仓库已清理"

# 步骤2：添加所有文件
print_info "步骤2：添加网站文件到Git..."
git add . 2>/dev/null
if [ $? -ne 0 ]; then
    print_error "添加文件失败"
    exit 1
fi
print_success "文件添加完成"

# 步骤3：提交更改
print_info "步骤3：提交更改..."
git commit -m "部署零初科技官方网站 - $(date '+%Y-%m-%d %H:%M:%S')" 2>/dev/null
if [ $? -ne 0 ]; then
    print_warning "没有新的更改需要提交，继续部署..."
fi
print_success "提交完成"

# 步骤4：配置远程仓库
print_info "步骤4：配置GitHub远程仓库..."
git remote remove origin 2>/dev/null
git remote add origin "https://github.com/$github_username/$repo_name.git"
if [ $? -ne 0 ]; then
    print_error "配置远程仓库失败"
    exit 1
fi
print_success "远程仓库配置完成"

# 步骤5：创建CNAME文件（如果使用自定义域名）
if [ -n "$custom_domain" ]; then
    print_info "步骤5：配置自定义域名..."
    echo "$custom_domain" > CNAME
    git add CNAME
    git commit -m "添加自定义域名: $custom_domain" 2>/dev/null
    print_success "自定义域名配置完成: $custom_domain"
fi

# 步骤6：推送到GitHub
print_info "步骤6：推送到GitHub..."
git branch -M main
git push -u origin main --force
if [ $? -ne 0 ]; then
    print_error "推送失败，请检查："
    echo "  1. GitHub用户名是否正确"
    echo "  2. 仓库是否存在（如不存在请先创建）"
    echo "  3. 网络连接是否正常"
    exit 1
fi
print_success "代码推送成功！"

echo ""
echo "=========================================="
echo "🎉 部署完成！"
echo "=========================================="
echo ""

# 显示部署结果
print_success "✅ 网站代码已成功推送到GitHub！"
echo ""
echo "📋 接下来需要手动完成最后一步："
echo ""
echo "1. 访问 GitHub 仓库："
echo "   https://github.com/$github_username/$repo_name"
echo ""
echo "2. 启用 GitHub Pages："
echo "   a. 点击 'Settings'（设置）"
echo "   b. 左侧选择 'Pages'"
echo "   c. 分支选择 'main'"
echo "   d. 文件夹选择 '/ (root)'"
echo "   e. 点击 'Save'（保存）"
echo ""
echo "3. 等待部署生效（约5-10分钟）"
echo ""

# 显示访问地址
echo "🌐 网站访问地址："
echo "   主地址：https://$github_username.github.io/$repo_name/"
if [ -n "$custom_domain" ]; then
    echo "   自定义域名：https://$custom_domain"
    echo ""
    echo "📋 自定义域名配置说明："
    echo "   1. 在域名注册商处添加CNAME记录："
    echo "      $custom_domain CNAME $github_username.github.io"
    echo "   2. 等待DNS生效（通常需要几分钟到几小时）"
fi

echo ""
echo "🔧 测试网站状态："
echo "   curl -I https://$github_username.github.io/$repo_name/"
echo ""
echo "💡 后续操作："
echo "   • 网站部署后，GitHub会自动启用SSL证书"
echo "   • 首次访问可能需要清除浏览器缓存"
echo "   • 如需更新网站，运行：git add . && git commit -m '更新' && git push"
echo ""
echo "📞 技术支持："
echo "   • 邮箱：contact@lingchu.com"
echo "   • 电话：400-123-4567"
echo ""
echo "=========================================="
echo "🚀 零初科技官方网站部署完成！"
echo "=========================================="

# 创建部署完成标记
echo "部署时间: $(date '+%Y-%m-%d %H:%M:%S')" > DEPLOYMENT_COMPLETE.txt
echo "GitHub用户: $github_username" >> DEPLOYMENT_COMPLETE.txt
echo "仓库名称: $repo_name" >> DEPLOYMENT_COMPLETE.txt
if [ -n "$custom_domain" ]; then
    echo "自定义域名: $custom_domain" >> DEPLOYMENT_COMPLETE.txt
fi
echo "访问地址: https://$github_username.github.io/$repo_name/" >> DEPLOYMENT_COMPLETE.txt