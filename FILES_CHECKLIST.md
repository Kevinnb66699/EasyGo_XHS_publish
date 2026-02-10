# 📦 文件清单 - 上传到 GitHub 仓库

## 签名服务器仓库（xhs-sign-server）

需要上传到 GitHub 的 **8 个文件**：

### 必需文件（6个）
- ✅ `server.py` - 签名服务器主程序
- ✅ `requirements.txt` - Python 依赖
- ✅ `Dockerfile` - Docker 构建配置
- ✅ `railway.json` - Railway 配置
- ✅ `.dockerignore` - Docker 忽略规则
- ✅ `.gitignore` - Git 忽略规则

### 推荐文件（2个）
- ✅ `README.md` - 项目说明
- ✅ `test_server.py` - 测试脚本

---

## 部署步骤

### 1. 创建 GitHub 仓库

在 GitHub 上创建新仓库：
- 仓库名：`xhs-sign-server`
- 类型：Public 或 Private
- 不要勾选初始化选项

### 2. 上传文件

```bash
cd xhs-sign-server

# 初始化 Git
git init

# 添加所有文件
git add .

# 提交
git commit -m "Initial commit: XHS signature server"

# 连接远程仓库（替换 YOUR_USERNAME）
git remote add origin https://github.com/YOUR_USERNAME/xhs-sign-server.git

# 推送
git branch -M main
git push -u origin main
```

### 3. 在 Railway 部署

1. 访问 https://railway.app
2. 登录（使用 GitHub 账号）
3. New Project → Deploy from GitHub repo
4. 选择 `xhs-sign-server` 仓库
5. 等待构建完成

### 4. 获取域名

1. Settings → Networking
2. Generate Domain
3. 复制域名

### 5. 配置 Vercel

1. Vercel Dashboard → 你的项目 → Settings → Environment Variables
2. 添加：
   - Key: `XHS_SIGN_SERVER_URL`
   - Value: 你的 Railway 域名
3. 重新部署：`vercel --prod`

### 6. 测试

```bash
# 测试签名服务
python test_server.py https://your-railway-domain.up.railway.app

# 应该看到：
# ✅ API 信息: 通过
# ✅ 健康检查: 通过
# ✅ 签名生成: 通过
# 🎉 所有测试通过！
```

---

## ✅ 完成标志

部署成功后：
- ✅ Railway 服务正常运行
- ✅ 健康检查返回 `"status": "healthy"`
- ✅ 测试脚本全部通过
- ✅ Vercel 环境变量已配置
- ✅ 小红书发布 API 正常工作

---

**就是这么简单！只需要 8 个文件！** 🎉
