# 小红书发布 API

一个基于 Python 的小红书自动发布 API，支持部署到 Vercel Serverless 平台。

## ✨ 特性

- 🚀 支持文字和图片笔记发布（最多9张图片）
- 🔐 基于 Cookie 的身份验证
- ⚡ Serverless 部署，按需付费
- 🔄 自动重试机制（指数退避）
- 📝 完整的日志记录
- 🛡️ 错误处理和参数验证
- 💾 图片自动下载和验证

## 📋 目录结构

```
xiaohongshu-api/
├── api/
│   └── publish.py          # 主 API 端点
├── requirements.txt         # Python 依赖
├── vercel.json             # Vercel 配置
├── .gitignore              # Git 忽略文件
└── README.md               # 项目文档
```

## 🔧 技术栈

- **语言**: Python 3.9+
- **框架**: Flask 3.0
- **小红书 SDK**: xhs 0.2.13+
- **部署平台**: Vercel Serverless Functions

## 📦 安装依赖

### 本地开发

```bash
# 克隆项目
git clone <your-repo-url>
cd EasyGo_XHS_publish

# 安装依赖
pip install -r requirements.txt
```

## 🚀 使用方法

### API 端点

**POST** `/api/publish`

### 请求示例

#### 请求头（Headers）

```http
Content-Type: application/json
X-XHS-Cookie: a1=xxx; webId=yyy; web_session=zzz
```

#### 请求体（Request Body）

**发布纯文字笔记：**
```json
{
  "title": "我的第一篇笔记",
  "content": "这是笔记的正文内容，可以很长很长..."
}
```

**发布单张图片笔记：**
```json
{
  "title": "美食分享",
  "content": "今天做的美食超级好吃！",
  "image_url": "https://example.com/food.jpg"
}
```

**发布多张图片笔记：**
```json
{
  "title": "旅行日记",
  "content": "今天去了很多好玩的地方",
  "image_urls": [
    "https://example.com/photo1.jpg",
    "https://example.com/photo2.jpg",
    "https://example.com/photo3.jpg"
  ]
}
```

**发布私密笔记：**
```json
{
  "title": "私密日记",
  "content": "只有我自己能看到",
  "is_private": true
}
```

### 字段说明

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `title` | string | ✅ | 笔记标题，最多20个字符 |
| `content` | string | ✅ | 笔记正文内容 |
| `image_url` | string | ❌ | 单张图片 URL（与 image_urls 二选一） |
| `image_urls` | array | ❌ | 多张图片 URL 数组，最多9张 |
| `is_private` | boolean | ❌ | 是否为私密笔记，默认 false |

### 响应格式

**成功响应（200）：**
```json
{
  "success": true,
  "note_id": "65a3f2e1000000001f00f234",
  "note_url": "https://www.xiaohongshu.com/explore/65a3f2e1000000001f00f234"
}
```

**失败响应（4xx/5xx）：**
```json
{
  "success": false,
  "error": "错误描述信息"
}
```

### 错误码说明

| HTTP 状态码 | 错误信息 | 说明 |
|------------|---------|------|
| 400 | `X-XHS-Cookie header is required` | 缺少 Cookie 请求头 |
| 400 | `title is required` | 缺少标题字段 |
| 400 | `content is required` | 缺少内容字段 |
| 401 | `Invalid cookie format or expired` | Cookie 格式无效或已过期 |
| 500 | `Failed to publish note: ...` | 发布失败 |

## 🧪 本地测试

### 1. 启动本地服务器

```bash
python api/publish.py
```

服务器将在 `http://localhost:5000` 启动。

### 2. 使用 curl 测试

```bash
curl -X POST http://localhost:5000/api/publish \
  -H "Content-Type: application/json" \
  -H "X-XHS-Cookie: a1=your_cookie_here; webId=xxx" \
  -d '{
    "title": "测试标题",
    "content": "这是一条测试笔记",
    "image_url": "https://picsum.photos/800/600"
  }'
```

### 3. 使用 Python 测试

```python
import requests

url = "http://localhost:5000/api/publish"
headers = {
    "Content-Type": "application/json",
    "X-XHS-Cookie": "a1=your_cookie_here; webId=xxx"
}
data = {
    "title": "测试标题",
    "content": "这是一条测试笔记"
}

response = requests.post(url, json=data, headers=headers)
print(response.json())
```

## 🌐 Vercel 部署

### 1. 安装 Vercel CLI

```bash
npm install -g vercel
```

### 2. 登录 Vercel

```bash
vercel login
```

### 3. 部署项目

```bash
vercel
```

首次部署时，按照提示配置：
- Set up and deploy? **Y**
- Which scope? 选择你的账户
- Link to existing project? **N**
- What's your project's name? **easygo-xhs-publish**
- In which directory is your code located? **.**

### 4. 生产环境部署

```bash
vercel --prod
```

部署完成后，你会得到一个 URL，例如：
```
https://easygo-xhs-publish.vercel.app
```

### 5. 测试线上接口

```bash
curl -X POST https://easygo-xhs-publish.vercel.app/api/publish \
  -H "Content-Type: application/json" \
  -H "X-XHS-Cookie: your_cookie_here" \
  -d '{
    "title": "线上测试",
    "content": "部署成功！"
  }'
```

## 🔑 获取小红书 Cookie

1. 打开浏览器，访问 [小红书网页版](https://www.xiaohongshu.com)
2. 登录你的账号
3. 打开浏览器开发者工具（F12）
4. 切换到 "Network" 标签
5. 刷新页面
6. 点击任意请求，查看 "Request Headers"
7. 找到 `Cookie` 字段，复制完整的 Cookie 值

**重要提示：**
- Cookie 包含敏感信息，请勿泄露
- Cookie 可能会过期，需要定期更新
- 至少需要包含 `a1` 字段

## 🛡️ 安全建议

1. **不要在代码中硬编码 Cookie**
   - 始终通过请求头传递
   - 使用环境变量存储（如果需要）

2. **添加请求频率限制**
   - 避免被小红书平台封禁
   - 建议每次发布间隔至少 5-10 秒

3. **添加请求签名验证**（可选）
   - 防止未授权的 API 调用
   - 使用 API Key 或 JWT 进行身份验证

4. **限制跨域请求**
   - 在 Vercel 中配置 CORS 白名单
   - 设置环境变量 `ALLOWED_ORIGINS`

## 🐛 常见问题

### Q: 报错 "'NoneType' object is not callable" 怎么办？
**A:** 这是因为没有配置 `XHS_SIGN_SERVER_URL` 环境变量。在 Vercel 上部署时，必须配置外部签名服务。请参考上面的"签名服务"章节进行配置。

### Q: 报错 "XHS_SIGN_SERVER_URL environment variable is required" 怎么办？
**A:** 请按照以下步骤配置：
1. 使用 Docker 部署签名服务：`docker run -d -p 5005:5005 reajason/xhs-api:latest`
2. 在 Vercel 项目设置中添加环境变量 `XHS_SIGN_SERVER_URL`
3. 重新部署项目

### Q: Cookie 过期怎么办？
**A:** API 会返回 401 错误，提示 `Invalid cookie format or expired`。你需要重新获取 Cookie 并更新。

### Q: 图片上传失败怎么办？
**A:** 小红书要求笔记必须包含至少一张图片。检查图片 URL 是否可访问，并确保图片格式正确（支持 jpg、png、webp 等）。

### Q: 小红书 API 限流怎么办？
**A:** 代码已实现指数退避重试机制（最多重试 3 次）。如果仍然失败，建议降低发布频率。

### Q: 如何发布视频笔记？
**A:** 当前版本仅支持图文笔记，暂不支持视频。后续版本会考虑添加。

### Q: 标题超过 20 个字符会怎样？
**A:** 代码会自动截断为前 20 个字符，并记录警告日志。

### Q: 支持定时发布吗？
**A:** API 本身不支持定时发布，但你可以结合 Cron 任务或其他调度工具实现。

### Q: 签名服务部署在哪里比较好？
**A:** 建议部署在稳定的服务器上，如：
- 阿里云 ECS
- 腾讯云 CVM  
- AWS EC2
- 自己的 VPS

确保服务器网络稳定，并且 Vercel 可以访问到该服务器。

## 📊 健康检查

API 提供健康检查端点：

```bash
curl https://your-app.vercel.app/api/health
```

返回：
```json
{
  "status": "healthy",
  "service": "xiaohongshu-publish-api",
  "version": "1.0.0"
}
```

## 📝 日志说明

API 会记录以下关键信息：
- ✅ 请求接收（Cookie 已脱敏）
- ✅ 参数验证结果
- ✅ 图片下载进度
- ✅ 小红书 API 调用
- ✅ 发布成功/失败详情
- ❌ 错误堆栈信息

在 Vercel 上查看日志：
1. 进入项目控制台
2. 点击 "Deployments"
3. 选择最新部署
4. 点击 "Functions" 查看日志

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

## 📄 许可证

MIT License

## ⚠️ 重要说明

### 关于 xhs 库

本项目使用的 [xhs 库](https://github.com/ReaJason/xhs) 是一个第三方小红书 API 封装工具。该库：

- ✅ 支持发布图文笔记（最多 9 张图片）
- ✅ 支持发布视频笔记
- ✅ 支持定时发布
- ✅ 支持添加话题和 @ 用户
- ⚠️ 需要有效的小红书 Cookie
- ⚠️ 某些功能可能需要配置签名服务（用于反爬虫）

### 签名服务（必需）

⚠️ **重要更新**：由于小红书的反爬虫机制，在 Vercel 等 Serverless 环境中部署时，**必须**配置外部签名服务。

#### 为什么需要签名服务？

小红书 API 需要对每个请求进行签名以通过安全验证。签名生成需要执行 JavaScript 代码，通常使用 Playwright 在浏览器环境中完成。但 Vercel Serverless 环境无法运行 Playwright，因此需要独立的签名服务器。

#### 配置签名服务

**方式一：使用 Docker 部署签名服务（推荐）**

1. 在有 Docker 环境的服务器上运行：

```bash
docker run -d -p 5005:5005 reajason/xhs-api:latest
```

2. 在 Vercel 环境变量中配置：

```bash
XHS_SIGN_SERVER_URL=http://your-server-ip:5005
```

**方式二：自建签名服务**

参考 [xhs 官方文档](https://reajason.github.io/xhs/basic.html#flask) 搭建签名服务器。

#### Vercel 环境变量配置

1. 登录 [Vercel Dashboard](https://vercel.com/dashboard)
2. 选择你的项目
3. 进入 "Settings" > "Environment Variables"
4. 添加以下环境变量：

| 变量名 | 值 | 说明 |
|-------|-----|------|
| `XHS_SIGN_SERVER_URL` | `http://your-server:5005` | 签名服务器地址（必需） |

5. 重新部署项目：

```bash
vercel --prod
```

#### 测试签名服务

可以通过以下命令测试签名服务是否正常：

```bash
curl -X POST http://your-server:5005/sign \
  -H "Content-Type: application/json" \
  -d '{
    "uri": "/api/sns/web/v2/note",
    "data": null,
    "a1": "your_a1_value",
    "web_session": "your_web_session"
  }'
```

应该返回包含 `x-s` 和 `x-t` 的签名信息。

## ⚠️ 免责声明

本项目仅供学习和研究使用，使用者需遵守小红书平台的相关规定和服务条款。因使用本项目导致的任何问题，开发者概不负责。

## 📮 联系方式

如有问题或建议，请提交 Issue。

---

**Made with ❤️ by EasyGo**
