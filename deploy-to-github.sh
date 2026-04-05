#!/bin/bash

# 零初科技官网GitHub部署脚本

echo "🚀 开始部署零初科技官网到GitHub Pages..."

# 检查Git
if ! command -v git &> /dev/null; then
    echo "❌ Git未安装，请先安装Git"
    exit 1
fi

# 检查当前目录
if [ ! -f "index.html" ]; then
    echo "❌ 错误：请在网站根目录运行此脚本"
    exit 1
fi

# 获取GitHub信息
echo ""
echo "📋 请输入GitHub部署信息："
echo ""

read -p "1. GitHub用户名: " github_username
read -p "2. 仓库名称（默认为lingchu-website）: " repo_name
repo_name=${repo_name:-lingchu-website}

echo ""
echo "是否使用自定义域名？"
read -p "3. 自定义域名（如www.lingchu.com，留空则不使用）: " custom_domain

# 创建CNAME文件（如果使用自定义域名）
if [ -n "$custom_domain" ]; then
    echo "$custom_domain" > CNAME
    echo "✅ 已创建CNAME文件：$custom_domain"
    git add CNAME
fi

# 推送到GitHub
echo ""
echo "📤 推送到GitHub..."

# 添加远程仓库
git remote add origin "https://github.com/$github_username/$repo_name.git" 2>/dev/null || {
    echo "⚠️  远程仓库已存在，更新中..."
    git remote set-url origin "https://github.com/$github_username/$repo_name.git"
}

# 推送代码
git branch -M main
git push -u origin main --force

echo ""
echo "🎉 代码推送完成！"
echo ""

# 显示部署说明
echo "📋 接下来需要手动操作："
echo ""
echo "1. 访问 https://github.com/$github_username/$repo_name"
echo "2. 点击 Settings → Pages"
echo "3. 分支选择 'main'，文件夹选择 '/ (root)'"
echo "4. 点击 Save"
echo ""
echo "⏳ 网站将在几分钟后可通过以下地址访问："
echo "   https://$github_username.github.io/$repo_name/"
echo ""

if [ -n "$custom_domain" ]; then
    echo "🌐 自定义域名配置："
    echo "   1. 在域名注册商处添加CNAME记录："
    echo "      $custom_domain CNAME $github_username.github.io"
    echo "   2. 等待DNS生效（通常需要几分钟到几小时）"
    echo "   3. 访问 https://$custom_domain"
    echo ""
fi

echo "💡 提示："
echo "   • 网站部署后，GitHub会自动启用SSL证书"
echo "   • 首次部署可能需要5-10分钟生效"
echo "   • 如需更新网站，只需运行：git add . && git commit -m '更新' && git push"
echo ""
echo "✅ 部署脚本执行完成！"