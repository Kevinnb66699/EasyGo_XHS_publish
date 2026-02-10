# 部署指南

## 📦 需要上传到 GitHub 的文件（签名服务器）

将 `xhs-sign-server/` 文件夹中的以下 8 个文件上传到 GitHub 仓库：

```
xhs-sign-server/
├── server.py              ✅ 主程序（必需）
├── requirements.txt       ✅ Python 依赖（必需）
├── Dockerfile            ✅ Docker 配置（必需）
├── railway.json          ✅ Railway 配置（必需）
├── .dockerignore         ✅ Docker 忽略规则（必需）
├── .gitignore           ✅ Git 忽略规则（必需）
├── README.md            ✅ 项目说明（推荐）
└── test_server.py       ✅ 测试脚本（推荐）
```

## 🚀 部署步骤

### 1. 上传到 GitHub

```bash
cd xhs-sign-server

# 初始化 Git
git init

# 添加文件
git add .

# 提交
git commit -m "Initial commit: XHS signature server"

# 连接远程仓库（替换为你的 GitHub 用户名）
git remote add origin https://github.com/YOUR_USERNAME/xhs-sign-server.git

# 推送
git branch -M main
git push -u origin main
```

### 2. 在 Railway 部署

1. 访问 https://railway.app
2. 登录（推荐使用 GitHub 账号）
3. 点击 **New Project**
4. 选择 **Deploy from GitHub repo**
5. 授权 Railway 访问你的 GitHub
6. 选择 `xhs-sign-server` 仓库
7. 等待构建完成（5-10 分钟）

### 3. 获取域名

1. 点击你的服务
2. 进入 **Settings** > **Networking**
3. 点击 **Generate Domain**
4. 复制域名（如：`https://xhs-sign-production-xxxx.up.railway.app`）

### 4. 配置 Vercel

1. 登录 Vercel Dashboard
2. 进入你的项目 > **Settings** > **Environment Variables**
3. 添加环境变量：
   - **Key**: `XHS_SIGN_SERVER_URL`
   - **Value**: 你的 Railway 域名
4. 点击 **Save**
5. 重新部署：`vercel --prod`

### 5. 测试

```bash
# 测试签名服务
python test_server.py https://your-railway-domain.up.railway.app

# 测试小红书 API
curl -X POST https://your-vercel-app.vercel.app/api/publish \
  -H "Content-Type: application/json" \
  -H "X-XHS-Cookie: a1=xxx; web_session=yyy" \
  -d '{
    "title": "测试笔记",
    "content": "测试内容",
    "image_urls": ["https://picsum.photos/800/600"]
  }'
```

## ❓ 常见问题

### Q: 需要在 GitHub 创建什么类型的仓库？

**A:** 创建一个新的空仓库：
- 仓库名：`xhs-sign-server`
- 类型：Public 或 Private 都可以
- 不要勾选 "Initialize this repository with a README"

### Q: Railway 构建失败怎么办？

**A:** 查看构建日志，常见问题：
- Dockerfile 语法错误
- 依赖安装失败
- 内存不足（升级到 Hobby 计划）

### Q: 免费额度够用吗？

**A:** Railway 免费计划：
- 500 小时/月（约 20 天持续运行）
- 512MB 内存
- 个人使用完全够用

## 📞 获取帮助

如果遇到问题：

1. 查看 Railway 部署日志
2. 运行 `test_server.py` 测试
3. 查看 `SETUP_GUIDE.md` 详细故障排查

---

**完成后，你的小红书发布 API 就可以正常工作了！** 🎉
