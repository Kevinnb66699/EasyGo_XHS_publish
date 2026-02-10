# 🔧 Vercel 404 错误修复说明

## 问题描述

部署到 Vercel 后出现 **404 NOT_FOUND** 错误。

## 根本原因

Vercel 的 Python Serverless Functions 有特定的文件映射规则：
- `api/filename.py` 自动映射到 `/api/filename` 路由
- Flask 路由定义和 Vercel 的文件映射需要正确配合

## 已修复的内容

### 1. 简化 `vercel.json`

**之前**（复杂且过时）：
```json
{
  "version": 2,
  "builds": [
    {
      "src": "api/*.py",
      "use": "@vercel/python"
    }
  ],
  "routes": [
    {
      "src": "/api/(.*)",
      "dest": "api/$1"
    }
  ]
}
```

**现在**（简洁正确）：
```json
{
  "version": 2
}
```

Vercel 会自动检测 `api/` 目录下的 Python 文件。

### 2. 调整 Flask 路由

**api/publish.py** - 添加了根路由 `/`：
```python
@app.route('/', methods=['POST'])           # 新增：映射到 /api/publish
@app.route('/api/publish', methods=['POST'])  # 保留：兼容性
def publish():
    ...
```

**api/health.py** - 新建健康检查文件：
```python
@app.route('/', methods=['GET'])            # 新增：映射到 /api/health
@app.route('/api/health', methods=['GET'])   # 保留：兼容性
def health():
    ...
```

### 3. 文件结构

```
api/
├── health.py    # 映射到 /api/health
└── publish.py   # 映射到 /api/publish
```

## 部署步骤

### 1️⃣ 提交更改

```bash
git add .
git commit -m "Fix: 修复 Vercel 404 错误"
git push
```

### 2️⃣ 等待自动部署

Vercel 会自动检测 Git 推送并重新部署（约 1-2 分钟）。

### 3️⃣ 测试接口

**健康检查**：
```bash
curl https://easygo-xhs-publish.vercel.app/api/health
```

**发布测试**：
```bash
curl -X POST https://easygo-xhs-publish.vercel.app/api/publish \
  -H "Content-Type: application/json" \
  -H "X-XHS-Cookie: 你的Cookie" \
  -d '{
    "title": "测试",
    "content": "修复后的测试"
  }'
```

## 工作原理

### Vercel Python Functions 映射规则

| 文件路径 | 自动映射的 URL |
|---------|---------------|
| `api/health.py` | `/api/health` |
| `api/publish.py` | `/api/publish` |
| `api/user/info.py` | `/api/user/info` |

### Flask 路由配合

在每个文件中，定义 `@app.route('/')` 来处理文件映射的路由：

```python
# api/publish.py
@app.route('/')  # 处理 /api/publish（由文件名决定）
def publish():
    ...
```

## 常见问题

### Q: 为什么需要两个路由装饰器？

```python
@app.route('/')                    # Vercel 文件映射
@app.route('/api/publish')         # 本地开发兼容
```

**A**: 
- 第一个 `/` 用于 Vercel 的文件映射
- 第二个 `/api/publish` 用于本地开发时保持一致的 API 路径

### Q: 还是 404 怎么办？

**A**: 检查以下几点：
1. ✅ `vercel.json` 只包含 `{"version": 2}`
2. ✅ Python 文件在 `api/` 目录下
3. ✅ 每个文件定义了 `@app.route('/')`
4. ✅ 等待部署完成（可能需要 1-2 分钟）
5. ✅ 清除浏览器缓存

### Q: 如何添加新的 API 端点？

**A**: 创建新文件，例如 `api/status.py`：

```python
from flask import Flask, jsonify

app = Flask(__name__)

@app.route('/')  # 映射到 /api/status
def status():
    return jsonify({"status": "ok"})
```

## 验证清单

- [x] 简化 `vercel.json`
- [x] 调整 Flask 路由
- [x] 创建独立的 `api/health.py`
- [x] 提交并推送代码
- [ ] 等待 Vercel 自动部署
- [ ] 测试 `/api/health` 接口
- [ ] 测试 `/api/publish` 接口

## 参考资源

- [Vercel Python Runtime](https://vercel.com/docs/functions/serverless-functions/runtimes/python)
- [Flask on Vercel](https://vercel.com/guides/using-flask-with-vercel)

---

修复完成！现在推送代码后，Vercel 应该可以正确部署了。🚀
