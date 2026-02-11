# 📁 文件清单

## 🎯 项目结构

```
EasyGo_XHS_publish/
│
├── 📄 发布服务器文件（部署到 Vercel）
│   ├── app.py                 # 主程序
│   ├── requirements.txt       # Python 依赖
│   ├── vercel.json           # Vercel 配置
│   ├── .env.example          # 环境变量示例
│   ├── .vercelignore         # Vercel 忽略文件
│   └── pyproject.toml        # Python 项目配置
│
├── 📄 项目文档
│   ├── README.md             # 项目说明（必读）
│   ├── QUICKSTART.md         # 快速开始指南
│   └── FILES.md              # 本文件
│
├── 🔧 配置文件
│   └── .gitignore            # Git 忽略文件
│
└── 📁 sign-server/（签名服务器，部署到 Render）
    ├── sign_server.py        # 主程序
    ├── requirements.txt      # Python 依赖
    ├── render.yaml          # Render 配置
    ├── README.md            # 签名服务器文档
    └── .gitignore           # Git 忽略文件
```

---

## 🔴 Render 部署文件（sign-server/）

部署签名服务器到 Render.com 需要的文件：

| 文件 | 必需 | 说明 |
|------|------|------|
| `sign_server.py` | ✅ | 签名服务器主文件 |
| `requirements.txt` | ✅ | Python 依赖（Flask, Playwright, gevent） |
| `render.yaml` | ⭐ | Render 配置（推荐，自动配置） |
| `README.md` | ⭐ | 文档说明 |
| `.gitignore` | ⭐ | Git 忽略文件 |

**部署配置：**
- **地区**: Singapore（新加坡）
- **Build Command**: `pip install -r requirements.txt && playwright install chromium && playwright install-deps`
- **Start Command**: `python sign_server.py`
- **Health Check**: `/health`

---

## 🟢 Vercel 部署文件（主文件夹）

部署发布服务器到 Vercel 需要的文件：

| 文件 | 必需 | 说明 |
|------|------|------|
| `app.py` | ✅ | 发布服务器主文件 |
| `requirements.txt` | ✅ | Python 依赖（Flask, xhs, requests） |
| `vercel.json` | ✅ | Vercel 配置 |
| `.vercelignore` | ⭐ | Vercel 忽略文件 |
| `.env.example` | ⭐ | 环境变量示例 |
| `pyproject.toml` | ⭐ | Python 项目配置 |

**环境变量（必须配置）：**
```
XHS_SIGN_SERVER_URL = https://your-sign-server.onrender.com
```

---

## 📚 文档文件

| 文件 | 说明 |
|------|------|
| `README.md` | 完整的项目说明文档 |
| `QUICKSTART.md` | 快速开始指南（3步部署） |
| `FILES.md` | 本文件（文件清单） |
| `sign-server/README.md` | 签名服务器专用文档 |

---

## 🗂️ 配置文件

| 文件 | 说明 |
|------|------|
| `.gitignore` | Git 忽略文件（主文件夹） |
| `sign-server/.gitignore` | Git 忽略文件（签名服务器） |
| `.env.example` | 环境变量示例 |
| `.vercelignore` | Vercel 部署忽略文件 |
| `vercel.json` | Vercel 平台配置 |
| `render.yaml` | Render 平台配置 |
| `pyproject.toml` | Python 项目元数据 |

---

## 📦 依赖说明

### 发布服务器依赖（requirements.txt）

```txt
Flask==3.0.0          # Web 框架
xhs>=0.2.13          # 小红书 SDK
requests==2.31.0      # HTTP 请求
Pillow==10.1.0       # 图片处理
```

### 签名服务器依赖（sign-server/requirements.txt）

```txt
flask==3.0.0          # Web 框架
gevent==23.9.1        # 异步服务器
playwright==1.40.0    # 浏览器自动化
requests==2.31.0      # HTTP 请求
```

---

## 🚫 已删除的文件

以下文件已从主文件夹删除（不再需要）：

- ❌ `stealth.min.js` - 自动从 CDN 下载
- ❌ `sign_server.py` - 已移至 sign-server/
- ❌ `requirements.sign.txt` - 已重命名为 sign-server/requirements.txt
- ❌ `render.yaml` - 已移至 sign-server/
- ❌ `start_all.bat` - 本地启动脚本
- ❌ `start_all.sh` - 本地启动脚本
- ❌ `stop_all.sh` - 本地停止脚本
- ❌ `test_sign_server.py` - 测试文件
- ❌ `test_api.py` - 测试文件
- ❌ `test_logging.py` - 测试文件
- ❌ `DEPLOY_RENDER.md` - 合并到 QUICKSTART.md
- ❌ `FILES_TO_DEPLOY.md` - 合并到本文件
- ❌ `EasyGo-xhs-sign-server/` - 旧的签名服务器文件夹

---

## 📋 部署检查清单

### Render 部署（sign-server/）

- [ ] `sign_server.py` 存在
- [ ] `requirements.txt` 存在
- [ ] `render.yaml` 配置正确（地区：Singapore）
- [ ] Git 仓库已创建
- [ ] 推送到 GitHub
- [ ] Render 连接仓库
- [ ] 部署成功，健康检查通过

### Vercel 部署（主文件夹）

- [ ] `app.py` 存在
- [ ] `requirements.txt` 存在
- [ ] `vercel.json` 存在
- [ ] 执行 `vercel` 命令
- [ ] 执行 `vercel --prod`
- [ ] 环境变量 `XHS_SIGN_SERVER_URL` 已配置
- [ ] 重新部署生效
- [ ] 健康检查通过

---

## 🔗 文件关系图

```
用户请求
   ↓
app.py (Vercel)
   ↓ 使用 XHS_SIGN_SERVER_URL
sign-server/sign_server.py (Render)
   ↓ 自动下载
stealth.min.js (CDN)
```

---

## 💡 提示

1. **不要修改文件结构**：保持当前结构，部署最简单
2. **不要手动上传 stealth.min.js**：会自动下载
3. **不要在主文件夹运行签名服务器**：它们是分开部署的
4. **环境变量很重要**：Vercel 必须配置 `XHS_SIGN_SERVER_URL`

---

## 📞 需要帮助？

- 先看 `QUICKSTART.md`（快速开始）
- 再看 `README.md`（详细说明）
- 最后看 `sign-server/README.md`（签名服务器）

---

**✅ 文件结构已整理完毕！**
