#!/bin/bash

# 零初科技官网部署脚本

echo "🚀 开始部署零初科技官网..."

# 检查是否在正确的目录
if [ ! -f "index.html" ]; then
    echo "❌ 错误：请在网站根目录运行此脚本"
    exit 1
fi

# 检查Git
if ! command -v git &> /dev/null; then
    echo "❌ Git未安装，请先安装Git"
    exit 1
fi

# 询问GitHub用户名
read -p "请输入GitHub用户名: " github_username

# 询问仓库名（默认为lingchu-website）
read -p "请输入GitHub仓库名（默认为lingchu-website）: " repo_name
repo_name=${repo_name:-lingchu-website}

# 询问是否使用自定义域名
read -p "是否使用自定义域名？(y/n，默认为n): " use_custom_domain
use_custom_domain=${use_custom_domain:-n}

if [ "$use_custom_domain" = "y" ] || [ "$use_custom_domain" = "Y" ]; then
    read -p "请输入自定义域名（如www.lingchu.com）: " custom_domain
    echo "$custom_domain" > CNAME
    echo "✅ 已创建CNAME文件：$custom_domain"
fi

# 初始化Git仓库
echo "📦 初始化Git仓库..."
git init
git add .
git commit -m "初始提交：零初科技官网"

# 添加远程仓库
echo "🔗 添加远程仓库..."
git remote add origin "https://github.com/$github_username/$repo_name.git"

# 推送到GitHub
echo "⬆️  推送到GitHub..."
git branch -M main
git push -u origin main

echo ""
echo "🎉 部署完成！"
echo ""
echo "接下来需要手动操作："
echo "1. 访问 https://github.com/$github_username/$repo_name"
echo "2. 点击 Settings → Pages"
echo "3. 分支选择 'main'，文件夹选择 '/ (root)'"
echo "4. 点击 Save"
echo ""
echo "📱 网站将在几分钟后可通过以下地址访问："
echo "   https://$github_username.github.io/$repo_name/"
echo ""
if [ "$use_custom_domain" = "y" ] || [ "$use_custom_domain" = "Y" ]; then
    echo "🌐 自定义域名配置："
    echo "   1. 在域名注册商处添加CNAME记录："
    echo "      $custom_domain CNAME $github_username.github.io"
    echo "   2. 等待DNS生效（通常需要几分钟到几小时）"
    echo "   3. 访问 https://$custom_domain"
fi
echo ""
echo "💡 提示：如需更新网站，只需运行："
echo "   git add . && git commit -m '更新内容' && git push"