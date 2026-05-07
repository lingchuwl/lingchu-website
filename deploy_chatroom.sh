#!/bin/bash
# 部署AI聊天室到GitHub Pages
# 用法: GITHUB_TOKEN=xxx bash deploy_chatroom.sh

set -e

REPO="https://lingchuwl:${GITHUB_TOKEN}@github.com/lingchuwl/lingchu-website.git"
TMPDIR=$(mktemp -d)

echo "📦 克隆仓库..."
git clone --depth 1 "$REPO" "$TMPDIR/repo"

echo "📝 复制新文件..."
cp index.html "$TMPDIR/repo/"
cp chatroom.html "$TMPDIR/repo/"

cd "$TMPDIR/repo"

echo "🚀 提交并推送..."
git add -A
git commit -m "✨ 添加AI聊天室页面 - 支持零/初/壹/贰四位AI助手实时在线聊天"
git push origin main

echo "✅ 部署完成！"
echo "   https://lingchuwl.github.io/lingchu-website/"
echo "   https://lingchuwl.github.io/lingchu-website/chatroom.html"

rm -rf "$TMPDIR"
