# GitHub账号注册与仓库创建指南

## 🚀 快速开始（5分钟完成）

### 步骤1：注册GitHub账号（2分钟）
1. **访问**：https://github.com/signup
2. **填写信息**：
   - 邮箱地址（建议使用公司邮箱）
   - 密码（至少15个字符或至少8个字符包含数字和小写字母）
   - 用户名（如：lingchu-tech）
3. **验证邮箱**：查看邮箱，点击验证链接
4. **完成问卷**：简单选择使用目的（可选）

### 步骤2：创建仓库（1分钟）
1. **登录GitHub**：https://github.com
2. **点击右上角"+"** → "New repository"
3. **填写仓库信息**：
   - Repository name: `lingchu-website`
   - Description: `零初科技官方网站`
   - Public（公开）
   - 不勾选"Initialize this repository with a README"
4. **点击"Create repository"**

### 步骤3：获取访问令牌（2分钟）
1. **点击右上角头像** → "Settings"
2. **左侧选择"Developer settings"**
3. **选择"Personal access tokens"** → "Tokens (classic)"
4. **点击"Generate new token"** → "Generate new token (classic)"
5. **填写信息**：
   - Note: `零初科技网站部署`
   - Expiration: `90 days`（推荐）
   - Select scopes: 勾选 `repo`（全部权限）
6. **点击"Generate token"**
7. **复制令牌**（只显示一次，请妥善保存）

## 📋 完整详细步骤

### 1. GitHub账号注册

#### 1.1 访问注册页面
```
https://github.com/signup
```

#### 1.2 填写注册信息
- **邮箱**：建议使用 `contact@lingchu.com` 或公司邮箱
- **密码要求**：
  - 至少15个字符
  - 或至少8个字符，包含数字和小写字母
- **用户名**：建议使用 `lingchu-tech` 或 `lingchu-official`

#### 1.3 完成人机验证
- 可能需要完成简单的验证码
- 验证邮箱地址

#### 1.4 个性化设置（可选）
- 团队规模：选择适合的选项
- 使用目的：选择"Work"或"School"
- 功能兴趣：选择"Web development"

### 2. 创建网站仓库

#### 2.1 登录后创建仓库
1. 点击页面右上角的"+"图标
2. 选择"New repository"

#### 2.2 配置仓库设置
```
Repository name: lingchu-website
Description: 零初科技官方网站 - 智能工作流引擎
Public: ✓ (必须选择公开，GitHub Pages需要)
Initialize with README: ✗ (不勾选)
Add .gitignore: None
License: None
```

#### 2.3 创建完成
点击"Create repository"后，你会看到空的仓库页面。

### 3. 配置访问令牌

#### 3.1 为什么需要访问令牌？
GitHub要求使用令牌进行API访问，特别是：
- 从命令行推送代码
- 自动化部署
- 提高安全性

#### 3.2 创建令牌步骤
1. **进入设置**：右上角头像 → Settings
2. **开发者设置**：左侧最底部"Developer settings"
3. **个人访问令牌**：选择"Personal access tokens" → "Tokens (classic)"
4. **生成新令牌**：点击"Generate new token" → "Generate new token (classic)"

#### 3.3 令牌权限配置
```
Token名称: lingchu-website-deploy
有效期: 90 days (推荐)
权限范围:
  ✓ repo (全部仓库权限)
  ✓ workflow (工作流权限，可选)
```

#### 3.4 保存令牌
**重要**：令牌只显示一次，请立即保存到安全的地方！

### 4. 验证账号状态

#### 4.1 检查账号是否激活
```bash
# 使用curl验证
curl -I https://api.github.com/users/你的用户名
# 应该返回 HTTP 200
```

#### 4.2 检查仓库是否创建
```bash
# 检查仓库是否存在
curl -I https://api.github.com/repos/你的用户名/lingchu-website
# 应该返回 HTTP 200
```

### 5. 常见问题解决

#### 问题1：邮箱未验证
**症状**：无法创建仓库或推送代码
**解决**：
1. 检查邮箱收件箱
2. 点击GitHub发送的验证链接
3. 如未收到，在GitHub设置中重新发送验证邮件

#### 问题2：用户名已存在
**症状**：注册时提示用户名已被使用
**解决**：
- 尝试其他变体：`lingchu-tech`, `lingchu-official`, `lingchu-company`
- 添加数字：`lingchu2024`, `lingchu-tech01`

#### 问题3：访问令牌无效
**症状**：推送代码时提示认证失败
**解决**：
1. 重新生成令牌
2. 确保复制完整的令牌（以`ghp_`开头）
3. 检查令牌是否过期

#### 问题4：仓库创建失败
**症状**：无法创建公开仓库
**解决**：
- 免费账号可以创建无限公开仓库
- 检查网络连接
- 清除浏览器缓存后重试

### 6. 安全建议

#### 6.1 令牌安全
- **不要分享**：令牌相当于密码
- **定期更新**：每90天更新一次
- **限制权限**：只授予必要权限
- **环境变量**：不要硬编码在脚本中

#### 6.2 账号安全
- **启用双因素认证**：Settings → Security → 2FA
- **使用强密码**：至少15个字符
- **定期检查登录活动**：Settings → Security → Security log

#### 6.3 仓库安全
- **定期备份**：本地保存代码副本
- **分支保护**：保护main分支
- **代码审查**：启用pull request审查

### 7. 部署前检查清单

#### 完成以下所有项目：
- [ ] GitHub账号注册完成
- [ ] 邮箱已验证
- [ ] 用户名确定：`________________`
- [ ] 仓库创建：`lingchu-website`
- [ ] 访问令牌生成并保存
- [ ] 双因素认证已启用（推荐）

#### 信息记录表：
```
GitHub用户名: ________________
注册邮箱: ________________
仓库名称: lingchu-website
访问令牌: ________________
令牌有效期: 90天
```

### 8. 技术支持

#### 遇到问题？
1. **GitHub官方文档**：https://docs.github.com
2. **社区支持**：https://github.com/community
3. **联系GitHub支持**：https://support.github.com

#### 零初科技支持：
- **技术问题**：tech@lingchu.com
- **部署协助**：提供上述信息，我们可以协助部署
- **紧急支持**：400-123-4567

### 9. 下一步：部署网站

完成GitHub设置后，运行部署脚本：

```bash
cd /root/.openclaw/workspace/lingchu-website-clean
./AUTO_DEPLOY.sh
```

按照提示输入：
1. GitHub用户名
2. 仓库名称（默认为lingchu-website）
3. 自定义域名（可选）

### 10. 验证部署

部署完成后，验证网站：

1. **等待5-10分钟**：GitHub Pages需要时间部署
2. **访问网站**：`https://你的用户名.github.io/lingchu-website/`
3. **检查状态**：返回HTTP 200表示成功
4. **测试功能**：导航、表单、响应式设计

---

**🎯 目标：15分钟内完成GitHub设置并部署网站**

**立即开始注册，让你的公司官网上线！** 🚀