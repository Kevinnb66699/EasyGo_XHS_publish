# 📦 Vercel 部署指南

## 快速部署步骤

### 1️⃣ 准备工作

确保你已经完成以下准备：

- [x] 安装了 Git
- [x] 有 GitHub 账号
- [x] 有 Vercel 账号（可以用 GitHub 登录）
- [x] 获取了小红书 Cookie

### 2️⃣ 推送代码到 GitHub

```bash
# 初始化 Git 仓库
git init

# 添加所有文件
git add .

# 提交代码
git commit -m "Initial commit: 小红书发布 API"

# 创建 GitHub 仓库后，关联远程仓库
git remote add origin https://github.com/your-username/your-repo.git

# 推送代码
git push -u origin main
```

### 3️⃣ 在 Vercel 部署

#### 方式一：通过 Web 界面部署（推荐）

1. 访问 [Vercel](https://vercel.com)
2. 点击 "New Project"
3. 导入你的 GitHub 仓库
4. 在配置页面：
   - **Root Directory**: `./`
   - **Build Command**: 留空
   - **Output Directory**: 留空
   - **Install Command**: 留空
5. 点击 "Deploy"
6. 等待部署完成（约 1-2 分钟）

#### 方式二：通过 CLI 部署

```bash
# 安装 Vercel CLI
npm install -g vercel

# 登录
vercel login

# 部署
vercel

# 生产环境部署
vercel --prod
```

### 4️⃣ 验证部署

部署完成后，测试健康检查端点：

```bash
curl https://your-project.vercel.app/api/health
```

期望返回：
```json
{
  "status": "healthy",
  "service": "xiaohongshu-publish-api",
  "version": "1.0.0"
}
```

### 5️⃣ 测试发布功能

```bash
curl -X POST https://your-project.vercel.app/api/publish \
  -H "Content-Type: application/json" \
  -H "X-XHS-Cookie: your_cookie_here" \
  -d '{
    "title": "测试笔记",
    "content": "这是一条通过 API 发布的测试笔记"
  }'
```

## ⚠️ 常见部署问题

### 问题 1: 依赖安装失败

**错误信息**：`No solution found when resolving dependencies`

**解决方案**：检查 `requirements.txt` 中的版本号是否正确。

### 问题 2: 函数超时

**错误信息**：`Function execution timed out`

**解决方案**：
- Vercel 免费版的函数执行时间限制为 10 秒
- 如果图片下载较慢，可能会超时
- 考虑升级到 Pro 版本（60 秒超时）

### 问题 3: Cookie 无效

**错误信息**：`Invalid cookie format or expired`

**解决方案**：
- 重新获取小红书 Cookie
- 确保 Cookie 包含 `a1` 字段
- Cookie 可能有有效期，需要定期更新

### 问题 4: 图片下载失败

**错误信息**：`Failed to download image`

**解决方案**：
- 确保图片 URL 可公开访问
- 检查图片 URL 是否正确
- 某些图片可能有防盗链，需要处理 Referer

## 🔧 环境变量配置（可选）

在 Vercel 项目设置中添加环境变量：

| 变量名 | 说明 | 示例 |
|--------|------|------|
| `ALLOWED_ORIGINS` | 允许的跨域来源 | `https://your-domain.com` |
| `LOG_LEVEL` | 日志级别 | `INFO` 或 `DEBUG` |

## 📊 监控和日志

### 查看部署日志

1. 进入 Vercel 项目控制台
2. 点击 "Deployments"
3. 选择最新部署
4. 点击 "Functions" 查看执行日志

### 查看实时日志

```bash
vercel logs your-project-name --follow
```

## 🚀 性能优化建议

1. **图片优化**
   - 使用 CDN 托管图片
   - 压缩图片大小
   - 使用合适的图片格式

2. **错误处理**
   - 添加更详细的错误日志
   - 实现错误通知（如钉钉、Slack）

3. **请求限流**
   - 使用 Vercel Edge Config 实现限流
   - 避免被小红书封禁

## 📱 更新部署

当你修改代码后：

```bash
# 提交更改
git add .
git commit -m "Update: 描述你的更改"
git push

# Vercel 会自动重新部署
```

## 🔗 相关链接

- [Vercel 文档](https://vercel.com/docs)
- [xhs 库文档](https://reajason.github.io/xhs/)
- [项目 README](./README.md)

## 💡 提示

1. **第一次部署** 可能需要几分钟，耐心等待
2. **免费版限制**：
   - 每月 100GB 带宽
   - 每天 6000 次函数调用
   - 10 秒函数超时
3. **建议使用私有仓库** 以保护你的代码和配置

---

如有问题，请提交 Issue 或查看 README.md 中的常见问题解答。
