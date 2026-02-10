# ⚡ 快速开始指南

## 5 分钟部署到 Vercel

### 步骤 1: 获取小红书 Cookie（2 分钟）

1. 打开浏览器，访问 [小红书网页版](https://www.xiaohongshu.com)
2. 登录你的账号
3. 按 `F12` 打开开发者工具
4. 切换到 **Network** 标签
5. 刷新页面（`F5`）
6. 点击任意请求，找到 **Request Headers**
7. 复制完整的 `Cookie` 值

**Cookie 格式示例**：
```
a1=18d9876543210abc; webId=xyz123; web_session=040069b1234567890abcdef
```

> ⚠️ **重要**：至少需要包含 `a1` 字段

---

### 步骤 2: 部署到 Vercel（3 分钟）

#### 选项 A：GitHub + Vercel Web（推荐）

1. **推送到 GitHub**
   ```bash
   git init
   git add .
   git commit -m "Initial commit"
   git remote add origin https://github.com/你的用户名/仓库名.git
   git push -u origin main
   ```

2. **在 Vercel 部署**
   - 访问 [vercel.com](https://vercel.com)
   - 点击 "New Project"
   - 导入 GitHub 仓库
   - 配置留空，直接点击 "Deploy"
   - 等待 1-2 分钟

3. **记录你的 API 地址**
   ```
   https://你的项目名.vercel.app
   ```

#### 选项 B：Vercel CLI

```bash
# 安装 CLI
npm install -g vercel

# 登录
vercel login

# 部署
vercel --prod
```

---

### 步骤 3: 测试 API

#### 健康检查

```bash
curl https://你的项目名.vercel.app/api/health
```

**期望返回**：
```json
{
  "status": "healthy",
  "service": "xiaohongshu-publish-api",
  "version": "1.0.0"
}
```

#### 发布测试笔记

```bash
curl -X POST https://你的项目名.vercel.app/api/publish \
  -H "Content-Type: application/json" \
  -H "X-XHS-Cookie: 你的Cookie" \
  -d '{
    "title": "我的第一条API笔记",
    "content": "这是通过API自动发布的笔记！\n\n如果你看到这条，说明部署成功！🎉"
  }'
```

**成功返回**：
```json
{
  "success": true,
  "note_id": "65a3f2e1000000001f00f234",
  "note_url": "https://www.xiaohongshu.com/explore/65a3f2e1000000001f00f234"
}
```

---

## 🎯 使用场景示例

### 场景 1: 发布纯文字笔记

```python
import requests

url = "https://你的项目名.vercel.app/api/publish"
headers = {
    "Content-Type": "application/json",
    "X-XHS-Cookie": "你的Cookie"
}
data = {
    "title": "今日分享",
    "content": "今天学到了一个新技巧！"
}

response = requests.post(url, json=data, headers=headers)
print(response.json())
```

### 场景 2: 发布带图片的笔记

```python
data = {
    "title": "美食分享",
    "content": "今天做的美食超好吃！",
    "image_url": "https://your-cdn.com/food.jpg"
}

response = requests.post(url, json=data, headers=headers)
print(response.json())
```

### 场景 3: 发布多图笔记

```python
data = {
    "title": "旅行日记",
    "content": "今天去了很多好玩的地方",
    "image_urls": [
        "https://your-cdn.com/photo1.jpg",
        "https://your-cdn.com/photo2.jpg",
        "https://your-cdn.com/photo3.jpg"
    ]
}

response = requests.post(url, json=data, headers=headers)
print(response.json())
```

### 场景 4: 发布私密笔记

```python
data = {
    "title": "私人日记",
    "content": "这是我的私密想法",
    "is_private": True
}

response = requests.post(url, json=data, headers=headers)
print(response.json())
```

---

## 🔧 进阶配置

### 本地测试

```bash
# 安装依赖
pip install -r requirements.txt

# 运行本地服务器
python api/publish.py

# 测试（在另一个终端）
curl http://localhost:5000/api/health
```

### 使用测试脚本

1. 编辑 `test_api.py`
2. 修改 `COOKIE` 和 `API_URL`
3. 运行测试：
   ```bash
   python test_api.py
   ```

---

## ❓ 常见问题

### Q1: Cookie 过期了怎么办？

**A**: 重新获取 Cookie（步骤 1），然后在调用 API 时使用新的 Cookie。

### Q2: 为什么发布失败？

**A**: 检查：
- ✅ Cookie 是否正确且未过期
- ✅ 标题和内容是否都提供了
- ✅ 图片 URL 是否可访问
- ✅ 网络连接是否正常

### Q3: 如何查看错误日志？

**A**: 
1. 访问 Vercel 项目控制台
2. 点击 "Deployments" → 最新部署
3. 点击 "Functions" 查看日志

### Q4: 免费版有什么限制？

**A**: Vercel 免费版：
- 每月 100GB 带宽
- 每天 6000 次函数调用
- 10 秒函数超时

通常个人使用足够了！

---

## 📚 更多资源

- **完整文档**: 查看 [README.md](./README.md)
- **部署指南**: 查看 [DEPLOYMENT.md](./DEPLOYMENT.md)
- **xhs 库文档**: https://reajason.github.io/xhs/
- **Vercel 文档**: https://vercel.com/docs

---

## 🎉 恭喜！

你现在已经拥有了一个可以自动发布小红书笔记的 API 了！

**下一步可以做什么？**

- 📱 集成到你的自动化脚本中
- 🤖 连接到聊天机器人
- ⏰ 设置定时发布任务
- 🔗 连接到 n8n/Zapier 等自动化平台

有任何问题，随时提 Issue！🚀
