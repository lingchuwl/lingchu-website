# 零初科技官网部署指南

## 🚀 快速开始

### 方案A：本地预览（立即查看）
```bash
# 1. 进入网站目录
cd /root/.openclaw/workspace/lingchu-website-clean

# 2. 启动本地服务器
./preview.sh

# 3. 浏览器打开
#    本地：http://localhost:8000
#    网络：http://10.1.0.6:8000
```

### 方案B：GitHub Pages部署（推荐）
```bash
# 1. 进入网站目录
cd /root/.openclaw/workspace/lingchu-website-clean

# 2. 运行部署脚本
./deploy-to-github.sh

# 3. 按照提示输入信息
#    - GitHub用户名
#    - 仓库名称
#    - 自定义域名（可选）
```

### 方案C：手动部署
```bash
# 1. 创建GitHub仓库
#    访问：https://github.com/new
#    仓库名：lingchu-website
#    公开仓库

# 2. 推送代码
cd /root/.openclaw/workspace/lingchu-website-clean
git remote add origin https://github.com/你的用户名/lingchu-website.git
git branch -M main
git push -u origin main

# 3. 启用GitHub Pages
#    仓库设置 → Pages → 分支选择main → 保存
```

## 📁 文件结构

```
lingchu-website-clean/
├── index.html              # 主页面
├── css/style.css          # 样式文件
├── js/main.js            # JavaScript文件
├── README.md             # 说明文档
├── DEPLOYMENT_GUIDE.md   # 部署指南
├── deploy-to-github.sh   # GitHub部署脚本
├── preview.sh            # 本地预览脚本
└── .gitignore           # Git忽略配置
```

## 🌐 访问地址

### 本地预览
- **本地访问**：`http://localhost:8000`
- **网络访问**：`http://10.1.0.6:8000`

### GitHub Pages
- **默认地址**：`https://你的用户名.github.io/lingchu-website/`
- **自定义域名**：`https://www.lingchu.com`（需配置）

## 🔧 配置说明

### 1. 修改公司信息
编辑 `index.html` 中的以下部分：

```html
<!-- 公司名称 -->
<title>零初科技 - 智能工作流引擎</title>

<!-- 联系方式 -->
<p>400-123-4567</p>
<p>contact@lingchu.com</p>

<!-- 公司地址 -->
<p>北京市海淀区中关村科技园</p>
```

### 2. 修改定价方案
编辑 `index.html` 中的定价部分：

```html
<!-- 基础版 -->
<div class="price">¥999<span>/月</span></div>

<!-- 专业版 -->
<div class="price">¥2,999<span>/月</span></div>

<!-- 企业版 -->
<div class="price">定制<span>价格</span></div>
```

### 3. 添加自定义域名
```bash
# 1. 创建CNAME文件
echo "www.lingchu.com" > CNAME

# 2. 提交到Git
git add CNAME
git commit -m "添加自定义域名"
git push

# 3. 配置DNS
#    在域名注册商处添加CNAME记录：
#    www.lingchu.com CNAME 你的用户名.github.io
```

## 📊 网站功能

### 核心页面
1. **首页** - 产品介绍和核心价值
2. **核心价值** - 智能决策、流程自动化、跨部门协作
3. **产品优势** - 效率提升、成本降低、高可用性
4. **定价方案** - 基础版、专业版、企业版
5. **成功案例** - 客户案例展示
6. **联系我们** - 联系表单和联系方式

### 技术特性
- ✅ 响应式设计（手机、平板、电脑）
- ✅ 现代化UI/UX设计
- ✅ 平滑滚动和动画效果
- ✅ 完整的联系表单
- ✅ SEO优化结构
- ✅ 快速加载（CDN加速）

## 🚀 部署步骤详解

### 步骤1：准备GitHub账号
1. 访问 https://github.com
2. 注册新账号（免费）
3. 验证邮箱地址

### 步骤2：创建仓库
1. 点击右上角 "+" → "New repository"
2. 仓库名：`lingchu-website`
3. 描述：零初科技官方网站
4. 选择 "Public"
5. 点击 "Create repository"

### 步骤3：部署网站
```bash
# 方法A：使用部署脚本（推荐）
./deploy-to-github.sh

# 方法B：手动部署
git init
git add .
git commit -m "初始提交"
git branch -M main
git remote add origin https://github.com/你的用户名/lingchu-website.git
git push -u origin main
```

### 步骤4：启用GitHub Pages
1. 进入仓库：https://github.com/你的用户名/lingchu-website
2. 点击 "Settings" → "Pages"
3. 分支选择 "main"，文件夹选择 "/ (root)"
4. 点击 "Save"

### 步骤5：等待部署完成
- 首次部署需要5-10分钟
- GitHub会自动启用SSL证书
- 访问地址：`https://你的用户名.github.io/lingchu-website/`

## 🔍 验证部署

### 检查网站状态
```bash
# 检查GitHub Pages状态
curl -I https://你的用户名.github.io/lingchu-website/

# 预期返回：HTTP/2 200
```

### 测试网站功能
1. **响应式测试**：在不同设备尺寸查看
2. **表单测试**：提交联系表单
3. **链接测试**：点击所有导航链接
4. **性能测试**：使用Google PageSpeed Insights

## 🔄 更新网站

### 小规模更新
```bash
# 1. 修改网站文件
vim index.html

# 2. 提交更新
git add .
git commit -m "更新网站内容"
git push
```

### 大规模更新
```bash
# 1. 备份当前版本
git tag v1.0.0

# 2. 进行更新
# 修改文件...

# 3. 提交更新
git add .
git commit -m "v1.1.0：添加新功能"
git push

# 4. 创建新标签
git tag v1.1.0
git push --tags
```

## 🛠️ 故障排除

### 常见问题

#### 1. 网站无法访问
```bash
# 检查GitHub Pages状态
# 访问：https://github.com/你的用户名/lingchu-website/settings/pages

# 检查DNS解析（如果使用自定义域名）
dig www.lingchu.com
```

#### 2. 样式或脚本不加载
```bash
# 检查控制台错误
# 浏览器按F12打开开发者工具

# 检查文件路径
# 确保css/和js/目录存在
```

#### 3. 表单不工作
```bash
# 检查JavaScript控制台
# 确保main.js文件正确加载

# 测试表单提交
# 提交后应显示成功消息
```

#### 4. 移动端显示问题
```bash
# 检查viewport设置
# 确保index.html中有：
# <meta name="viewport" content="width=device-width, initial-scale=1.0">
```

### 获取帮助
- **GitHub支持**：https://docs.github.com/pages
- **技术问题**：tech@lingchu.com
- **部署问题**：查看本指南或联系技术支持

## 📈 后续优化建议

### 1. SEO优化
- 添加Google Analytics
- 提交网站到搜索引擎
- 优化meta标签和描述

### 2. 内容更新
- 定期更新成功案例
- 添加博客/新闻板块
- 更新产品功能说明

### 3. 性能优化
- 压缩图片
- 合并CSS/JS文件
- 启用浏览器缓存

### 4. 安全增强
- 定期更新依赖
- 启用HTTPS（GitHub Pages自动提供）
- 添加安全头部

## 📞 技术支持

- **技术支持**：tech@lingchu.com
- **商务合作**：business@lingchu.com
- **客服热线**：400-123-4567
- **工作时间**：周一至周五 9:00-18:00

---

**🎉 恭喜！你的公司官方网站已准备就绪！**

**立即部署，让客户看到你的专业形象！** 🚀