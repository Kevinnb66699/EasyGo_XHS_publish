# 主程序上传到 GitHub

## 📦 将要上传的文件

以下文件会被上传到 GitHub（已自动排除 xhs-sign-server 文件夹）：

```
EasyGo_XHS_publish/
├── app.py                ✅ 主程序（Flask API）
├── requirements.txt      ✅ Python 依赖
├── vercel.json          ✅ Vercel 配置
├── pyproject.toml       ✅ 项目配置
├── .gitignore           ✅ Git 忽略规则
├── .vercelignore        ✅ Vercel 忽略规则
├── .env.example         ✅ 环境变量示例
├── README.md            ✅ 项目说明
├── DEPLOY.md            ✅ 部署指南
├── SETUP_GUIDE.md       ✅ 设置指南
├── FILES_CHECKLIST.md   ✅ 文件清单
├── test_api.py          ✅ API 测试脚本
└── test_logging.py      ✅ 日志测试脚本
```

**不会上传**：
- ❌ `xhs-sign-server/` - 已在 .gitignore 中排除

---

## 🚀 上传步骤

### 1. 检查当前状态

```bash
# 进入主项目目录
cd d:\Desktop\Code\Cursor\EasyGo_XHS_publish

# 查看 Git 状态（如果已初始化）
git status
```

### 2. 初始化 Git（如果还没有）

```bash
# 初始化 Git 仓库
git init

# 查看将要提交的文件
git status
```

**确认**：`xhs-sign-server/` 应该不在列表中（已被 ignore）

### 3. 添加文件

```bash
# 添加所有文件（会自动排除 .gitignore 中的文件）
git add .

# 查看暂存的文件
git status
```

### 4. 提交更改

```bash
git commit -m "Initial commit: XHS publish API for Vercel"
```

### 5. 创建 GitHub 仓库

1. 访问 https://github.com/new
2. 仓库名称：`EasyGo_XHS_publish`（或你喜欢的名字）
3. 类型：Private（推荐）或 Public
4. **不要**勾选 "Initialize this repository with a README"
5. 点击 "Create repository"

### 6. 连接远程仓库

```bash
# 替换 YOUR_USERNAME 为你的 GitHub 用户名
git remote add origin https://github.com/YOUR_USERNAME/EasyGo_XHS_publish.git

# 设置主分支
git branch -M main

# 推送到 GitHub
git push -u origin main
```

### 7. 验证

访问你的 GitHub 仓库页面，确认：
- ✅ 看到 13 个文件
- ✅ 没有看到 `xhs-sign-server` 文件夹
- ✅ README.md 正常显示

---

## 🔧 如果 Git 仓库已存在

如果之前已经初始化过 Git：

```bash
# 查看当前状态
git status

# 查看是否已配置远程仓库
git remote -v

# 如果已配置，直接推送
git add .
git commit -m "Update: Fix NoneType error and add signature server support"
git push
```

---

## ❓ 常见问题

### Q: 确认 xhs-sign-server 已被忽略？

**A:** 运行以下命令：

```bash
git status
```

如果没有看到 `xhs-sign-server/`，说明已被成功忽略。

### Q: 如果不小心已经提交了 xhs-sign-server 怎么办？

**A:** 从 Git 中移除（不删除本地文件）：

```bash
git rm -r --cached xhs-sign-server
git commit -m "Remove xhs-sign-server folder from tracking"
git push
```

### Q: 主程序和签名服务器要分开部署吗？

**A:** 是的！
- **主程序**：部署到 Vercel
- **签名服务器**：单独部署到 Railway（作为独立仓库）

---

## 📋 检查清单

上传前确认：

- [ ] `.gitignore` 已包含 `xhs-sign-server/`
- [ ] 运行 `git status` 确认 xhs-sign-server 未被追踪
- [ ] 已创建 GitHub 仓库
- [ ] README.md 内容完整
- [ ] .env.example 已包含必要说明

---

## 🎯 下一步

主程序上传成功后：

1. ✅ 主程序已在 GitHub
2. ⏭️ 下一步：上传签名服务器到独立仓库
3. ⏭️ 然后：部署签名服务器到 Railway
4. ⏭️ 最后：在 Vercel 配置环境变量并部署

---

**准备好了吗？开始上传主程序吧！** 🚀
