# 零初科技官网

这是一个完全免费、外部可访问的公司官方网站。

## 网站特点

- ✅ **完全免费**：使用GitHub Pages免费托管
- ✅ **响应式设计**：适配手机、平板、电脑
- ✅ **现代化UI**：使用最新CSS和JavaScript技术
- ✅ **SEO友好**：优化的HTML结构和元标签
- ✅ **快速加载**：使用CDN加速资源
- ✅ **表单功能**：完整的联系表单

## 文件结构

```
lingchu-website/
├── index.html          # 主页面
├── README.md           # 说明文档
├── .gitignore          # Git忽略文件
└── CNAME              # 自定义域名配置（可选）
```

## 部署到GitHub Pages

### 步骤1：创建GitHub仓库
1. 登录GitHub
2. 点击右上角"+" → "New repository"
3. 仓库名：`lingchu-website`
4. 描述：零初科技官方网站
5. 选择"Public"（公开）
6. 点击"Create repository"

### 步骤2：上传文件
```bash
# 克隆仓库
git clone https://github.com/你的用户名/lingchu-website.git
cd lingchu-website

# 复制网站文件到仓库
cp -r /root/.openclaw/workspace/lingchu-website/* .

# 提交并推送
git add .
git commit -m "初始提交：零初科技官网"
git push origin main
```

### 步骤3：启用GitHub Pages
1. 进入仓库设置
2. 左侧菜单选择"Pages"
3. 分支选择"main"或"master"
4. 文件夹选择"/ (root)"
5. 点击"Save"

### 步骤4：访问网站
- 网站地址：`https://你的用户名.github.io/lingchu-website/`
- 自定义域名：可在CNAME文件中设置

## 自定义配置

### 修改公司信息
编辑`index.html`中的以下部分：
- 公司名称：第15行 `<title>零初科技 - 智能工作流引擎</title>`
- 联系方式：第XXX行 `400-123-4567` 和 `contact@lingchu.com`
- 公司地址：第XXX行 `北京市海淀区中关村科技园`

### 修改定价方案
编辑`index.html`中的定价部分：
- 基础版：¥999/月
- 专业版：¥2,999/月
- 企业版：定制价格

### 添加自定义域名
1. 在域名注册商处添加CNAME记录：
   ```
   www.lingchu.com CNAME 你的用户名.github.io
   ```
2. 在网站根目录创建`CNAME`文件：
   ```
   www.lingchu.com
   ```

## 技术栈

- **HTML5**：语义化标记
- **CSS3**：Flexbox、Grid、CSS变量
- **JavaScript**：原生JS，无框架依赖
- **Font Awesome**：图标库
- **Google Fonts**：字体库
- **GitHub Pages**：免费托管

## 维护建议

### 定期更新
1. 更新成功案例
2. 添加新闻动态
3. 更新产品功能
4. 优化SEO关键词

### 性能优化
1. 压缩图片
2. 合并CSS/JS文件
3. 使用CDN加速
4. 启用浏览器缓存

### SEO优化
1. 添加meta描述
2. 优化标题标签
3. 使用语义化HTML
4. 添加结构化数据

## 联系方式

- 技术支持：tech@lingchu.com
- 商务合作：business@lingchu.com
- 客服热线：400-123-4567

## 许可证

本项目采用MIT许可证。详见LICENSE文件。