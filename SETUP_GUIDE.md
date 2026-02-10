# 快速设置指南

## 问题诊断

如果你遇到以下错误：

```
'NoneType' object is not callable
```

或

```
XHS_SIGN_SERVER_URL environment variable is required
```

**原因**：未配置签名服务器环境变量。

## 解决方案

### 步骤 1：部署签名服务器

签名服务器用于生成小红书 API 请求的签名，是 Vercel 部署必需的组件。

#### 方式 A：使用 Docker（推荐）

如果你有一台服务器（如阿里云、腾讯云、AWS 等）：

```bash
# 安装 Docker（如果未安装）
# Ubuntu/Debian
sudo apt-get update
sudo apt-get install docker.io

# 启动签名服务
docker run -d -p 5005:5005 --name xhs-sign-server reajason/xhs-api:latest

# 验证服务运行
docker ps | grep xhs-sign-server
```

服务启动后，记下你的服务器 IP 地址，例如：`123.456.789.0`

#### 方式 B：使用 Railway/Render 等平台

如果没有服务器，可以使用免费的容器托管平台：

**Railway.app：**
1. 访问 https://railway.app
2. 创建新项目
3. 选择 "Deploy from Docker Image"
4. 输入镜像：`reajason/xhs-api:latest`
5. 设置端口：`5005`
6. 部署后会得到一个 URL，如：`https://your-app.railway.app`

**Render.com：**
1. 访问 https://render.com
2. 创建新 Web Service
3. 选择 "Docker"
4. 输入镜像：`reajason/xhs-api:latest`
5. 设置端口：`5005`
6. 部署后会得到一个 URL

### 步骤 2：在 Vercel 配置环境变量

1. 登录 [Vercel Dashboard](https://vercel.com/dashboard)

2. 选择你的项目（easygo-xhs-publish）

3. 进入 **Settings** > **Environment Variables**

4. 添加新变量：
   - **Key**: `XHS_SIGN_SERVER_URL`
   - **Value**: 你的签名服务器地址
     - 如果使用 Docker：`http://123.456.789.0:5005`
     - 如果使用 Railway：`https://your-app.railway.app`
     - 如果使用 Render：`https://your-app.onrender.com`
   
5. 选择应用环境：Production, Preview, Development（全选）

6. 点击 **Save**

### 步骤 3：重新部署

```bash
# 触发重新部署
vercel --prod
```

或者在 Vercel Dashboard 中点击 "Redeploy"。

### 步骤 4：测试

部署完成后，测试 API：

```bash
curl -X POST https://your-app.vercel.app/api/publish \
  -H "Content-Type: application/json" \
  -H "X-XHS-Cookie: a1=your_cookie; web_session=your_session" \
  -d '{
    "title": "测试笔记",
    "content": "这是一条测试笔记",
    "image_urls": ["https://picsum.photos/800/600"]
  }'
```

如果配置正确，应该返回：

```json
{
  "success": true,
  "note_id": "...",
  "note_url": "https://www.xiaohongshu.com/explore/..."
}
```

## 常见问题

### Q1: Docker 服务器需要什么配置？

**A:** 最低配置：
- 1 核 CPU
- 512MB 内存
- 任何主流 Linux 发行版

### Q2: 签名服务器安全吗？

**A:** 
- 签名服务器只用于生成请求签名，不会存储任何敏感信息
- Cookie 是通过请求头传递的，不会经过签名服务器
- 建议配置防火墙，只允许 Vercel IP 访问

### Q3: 可以在本地测试吗？

**A:** 可以。本地开发时：

```bash
# 1. 在一个终端启动签名服务
docker run -d -p 5005:5005 reajason/xhs-api:latest

# 2. 在另一个终端设置环境变量并运行
export XHS_SIGN_SERVER_URL=http://localhost:5005
python app.py
```

### Q4: Railway/Render 免费额度够用吗？

**A:** 
- Railway：每月 500 小时免费
- Render：每月 750 小时免费

对于个人使用完全够用。

### Q5: 签名服务请求失败怎么办？

**A:** 检查：
1. 签名服务器是否正常运行：`curl http://your-server:5005/health`
2. 防火墙是否开放 5005 端口
3. Vercel 能否访问你的服务器（可能需要公网 IP）

### Q6: 需要多个签名服务器吗？

**A:** 不需要。一个签名服务器可以服务多个 Vercel 项目。

## 架构说明

```
用户请求
   ↓
Vercel (Flask API)
   ↓
签名服务器 (生成签名)
   ↓
小红书 API
```

签名服务器的作用是模拟浏览器环境，执行小红书的 JavaScript 签名算法，生成每个请求需要的 `x-s` 和 `x-t` 签名参数。

## 技术支持

如果仍有问题，请：
1. 查看 Vercel 部署日志
2. 查看签名服务器日志：`docker logs xhs-sign-server`
3. 提交 Issue 并附上错误日志

---

**祝你部署顺利！🎉**
