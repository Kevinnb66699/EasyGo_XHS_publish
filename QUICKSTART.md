# 🚀 快速开始

## 📦 项目结构

```
主文件夹（发布服务器 → Vercel）
├── app.py
├── requirements.txt
├── vercel.json
└── sign-server/（签名服务器 → Render）
    ├── sign_server.py
    ├── requirements.txt
    └── render.yaml
```

---

## 🎯 三步部署

### 第 1 步：部署签名服务器到 Render（新加坡）

#### 方式一：使用 Git（推荐）

```bash
# 1. 进入签名服务器目录
cd sign-server

# 2. 初始化 Git
git init
git add .
git commit -m "Initial commit"

# 3. 推送到 GitHub
git remote add origin https://github.com/你的用户名/xhs-sign-server.git
git push -u origin main

# 4. 在 Render.com 部署
# - 访问 https://dashboard.render.com
# - 点击 "New +" → "Web Service"
# - 连接 GitHub 仓库
# - Render 会自动检测 render.yaml
# - 确认地区是 Singapore
# - 点击 "Create Web Service"
```

#### 方式二：手动配置

1. 访问 [Render Dashboard](https://dashboard.render.com)
2. 点击 "New +" → "Web Service"
3. 配置：

| 配置项 | 值 |
|--------|-----|
| Name | `xhs-sign-server` |
| Region | `Singapore` |
| Build Command | `pip install -r requirements.txt && playwright install chromium && playwright install-deps` |
| Start Command | `python sign_server.py` |
| Health Check Path | `/health` |

4. 等待部署完成（5-10分钟）

#### 获取签名服务器 URL

部署成功后，Render 会提供 URL：
```
https://xhs-sign-server-xxxxx.onrender.com
```

**保存这个 URL，下一步需要用！**

---

### 第 2 步：部署发布服务器到 Vercel

```bash
# 1. 回到主文件夹
cd ..

# 2. 确保在主文件夹
ls  # 应该看到 app.py, vercel.json, sign-server/

# 3. 部署到 Vercel
vercel

# 4. 生产环境部署
vercel --prod
```

---

### 第 3 步：配置环境变量

1. 访问 [Vercel Dashboard](https://vercel.com/dashboard)
2. 选择你的项目
3. 进入 "Settings" → "Environment Variables"
4. 添加环境变量：

```
变量名: XHS_SIGN_SERVER_URL
值: https://xhs-sign-server-xxxxx.onrender.com
（替换为你在第1步获取的 Render URL）
```

5. 点击 "Save"
6. 重新部署：

```bash
vercel --prod
```

---

## 🧪 测试

### 1. 测试签名服务器

```bash
curl https://your-sign-server.onrender.com/health
```

预期响应：
```json
{
  "status": "healthy",
  "browser_ready": true,
  "a1": "188b...",
  "timestamp": 1706774400
}
```

### 2. 测试发布服务器

```bash
curl https://your-app.vercel.app/api/health
```

预期响应：
```json
{
  "status": "healthy",
  "service": "xiaohongshu-publish-api",
  "version": "1.0.0"
}
```

### 3. 测试完整流程

```bash
curl -X POST https://your-app.vercel.app/api/publish \
  -H "Content-Type: application/json" \
  -H "X-XHS-Cookie: a1=xxx; web_session=xxx; webId=xxx" \
  -d '{
    "title": "测试标题",
    "content": "测试内容",
    "image_urls": ["https://picsum.photos/800/600"]
  }'
```

---

## 🔑 获取 Cookie

1. 访问 https://www.xiaohongshu.com
2. 登录你的账号
3. 按 `F12` 打开开发者工具
4. 切换到 `Network` 标签
5. 刷新页面
6. 点击任意请求，找到 `Cookie`
7. 复制完整 Cookie（必须包含 a1、web_session、webId）

---

## ✅ 完成检查清单

- [ ] 签名服务器已部署到 Render（新加坡）
- [ ] 签名服务器健康检查通过
- [ ] 发布服务器已部署到 Vercel
- [ ] 环境变量 `XHS_SIGN_SERVER_URL` 已配置
- [ ] Vercel 已重新部署
- [ ] 发布服务器健康检查通过
- [ ] 已获取有效的小红书 Cookie
- [ ] 完整流程测试通过

---

## 📊 预计时间

- ⏱️ 签名服务器部署：5-10 分钟
- ⏱️ 发布服务器部署：1-2 分钟
- ⏱️ 配置和测试：3-5 分钟
- **总计：10-20 分钟**

---

## ❓ 常见问题

### 签名服务器一直在部署中

**原因：** 安装 Playwright 浏览器需要时间。

**解决：** 等待 10 分钟，查看 Render 日志。

### Vercel 无法连接签名服务器

**检查：**
1. 环境变量是否正确
2. Render 服务是否启动（Free Plan 会休眠）
3. 先访问签名服务器 URL 唤醒

### Cookie 验证失败

**确认：**
1. Cookie 包含 a1、web_session、webId
2. Cookie 未过期
3. 从已登录的小红书网页获取

---

## 💡 提示

1. **Render Free Plan**：15分钟无请求后休眠，首次调用需要等待唤醒（30-60秒）
2. **生产环境**：建议升级 Render 到 Starter Plan ($7/月)，避免休眠
3. **Cookie 有效期**：定期更新 Cookie，建议每周检查一次

---

## 📞 需要帮助？

- 查看主 README.md 详细文档
- 查看 Render 和 Vercel 日志
- 检查环境变量配置

---

**🎉 部署完成！开始使用吧！**
