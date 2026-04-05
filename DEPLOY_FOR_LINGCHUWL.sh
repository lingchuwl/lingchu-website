#!/bin/bash

# 零初科技官网专用部署脚本 - 为 lingchuwl 定制

echo "=========================================="
echo "🚀 零初科技官方网站部署 - lingchuwl"
echo "=========================================="
echo ""

# 配置信息
GITHUB_USERNAME="lingchuwl"
GITHUB_REPO="lingchu-website"
GITHUB_EMAIL="84610996@qq.com"

# 颜色定义
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

print_success() { echo -e "${GREEN}✅ $1${NC}"; }
print_error() { echo -e "${RED}❌ $1${NC}"; }
print_warning() { echo -e "${YELLOW}⚠️  $1${NC}"; }

# 检查当前目录
if [ ! -f "index.html" ]; then
    print_error "错误：请在网站根目录运行此脚本"
    exit 1
fi

# 检查Git
if ! command -v git &> /dev/null; then
    print_error "Git未安装"
    exit 1
fi

echo "📋 配置信息："
echo "   用户名: $GITHUB_USERNAME"
echo "   仓库名: $GITHUB_REPO"
echo "   邮箱: $GITHUB_EMAIL"
echo ""

# 获取访问令牌
read -sp "请输入GitHub访问令牌: " GITHUB_TOKEN
echo ""

if [ -z "$GITHUB_TOKEN" ]; then
    print_error "访问令牌不能为空"
    exit 1
fi

echo ""
echo "=========================================="
echo "🔧 开始部署流程"
echo "=========================================="
echo ""

# 步骤1：配置Git
print_warning "步骤1：配置Git用户信息..."
git config user.name "$GITHUB_USERNAME"
git config user.email "$GITHUB_EMAIL"
print_success "Git配置完成"

# 步骤2：检查仓库是否存在
print_warning "步骤2：检查GitHub仓库..."
repo_status=$(curl -s -o /dev/null -w "%{http_code}" \
  -H "Authorization: token $GITHUB_TOKEN" \
  "https://api.github.com/repos/$GITHUB_USERNAME/$GITHUB_REPO")

if [ "$repo_status" = "200" ]; then
    print_success "仓库已存在: $GITHUB_USERNAME/$GITHUB_REPO"
elif [ "$repo_status" = "404" ]; then
    print_warning "仓库不存在，正在创建..."
    
    # 创建仓库
    create_result=$(curl -s -X POST \
      -H "Authorization: token $GITHUB_TOKEN" \
      -H "Accept: application/vnd.github.v3+json" \
      -d "{\"name\":\"$GITHUB_REPO\",\"description\":\"零初科技官方网站\",\"private\":false}" \
      "https://api.github.com/user/repos")
    
    if echo "$create_result" | grep -q "Bad credentials"; then
        print_error "令牌无效，请检查令牌权限"
        exit 1
    elif echo "$create_result" | grep -q "name already exists"; then
        print_success "仓库已存在（其他错误）"
    else
        print_success "仓库创建成功: $GITHUB_USERNAME/$GITHUB_REPO"
    fi
else
    print_error "检查仓库失败，HTTP状态码: $repo_status"
    exit 1
fi

# 步骤3：添加和提交更改
print_warning "步骤3：提交网站文件..."
git add .
git commit -m "部署零初科技官方网站 - $(date '+%Y-%m-%d %H:%M:%S')"
print_success "文件提交完成"

# 步骤4：配置远程仓库
print_warning "步骤4：配置远程仓库..."
git remote remove origin 2>/dev/null
git remote add origin "https://$GITHUB_TOKEN@github.com/$GITHUB_USERNAME/$GITHUB_REPO.git"
print_success "远程仓库配置完成"

# 步骤5：推送到GitHub
print_warning "步骤5：推送到GitHub..."
git branch -M main
git push -u origin main --force

if [ $? -eq 0 ]; then
    print_success "✅ 代码推送成功！"
else
    print_error "推送失败，请检查："
    echo "  1. 令牌权限是否正确（需要repo权限）"
    echo "  2. 网络连接是否正常"
    echo "  3. 仓库名称是否正确"
    exit 1
fi

echo ""
echo "=========================================="
echo "🎉 部署完成！"
echo "=========================================="
echo ""

print_success "✅ 网站代码已成功推送到GitHub！"
echo ""
echo "📋 接下来需要手动完成最后一步："
echo ""
echo "1. 访问 GitHub 仓库："
echo "   https://github.com/$GITHUB_USERNAME/$GITHUB_REPO"
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
echo "🌐 网站访问地址："
echo "   https://$GITHUB_USERNAME.github.io/$GITHUB_REPO/"
echo ""
echo "🔧 测试网站状态："
echo "   curl -I https://$GITHUB_USERNAME.github.io/$GITHUB_REPO/"
echo ""
echo "💡 提示："
echo "   • 首次部署可能需要5-10分钟生效"
echo "   • GitHub会自动启用SSL证书"
echo "   • 如需更新，运行: git add . && git commit -m '更新' && git push"
echo ""
echo "📞 技术支持：contact@lingchu.com"
echo ""
echo "=========================================="
echo "🚀 零初科技官方网站部署完成！"
echo "=========================================="

# 保存部署记录
echo "部署时间: $(date '+%Y-%m-%d %H:%M:%S')" > DEPLOYMENT_RECORD.txt
echo "GitHub用户: $GITHUB_USERNAME" >> DEPLOYMENT_RECORD.txt
echo "仓库: $GITHUB_REPO" >> DEPLOYMENT_RECORD.txt
echo "访问地址: https://$GITHUB_USERNAME.github.io/$GITHUB_REPO/" >> DEPLOYMENT_RECORD.txt
echo "技术支持: contact@lingchu.com" >> DEPLOYMENT_RECORD.txt