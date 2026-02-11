# 🧪 部署测试指南

## 快速开始

### 方式 1: Python 自动化测试脚本（推荐）

```bash
# 安装依赖
pip install requests

# 运行测试脚本
python test_deployment.py
```

测试脚本会自动测试：
- ✅ 签名服务器健康检查
- ✅ 签名服务器功能测试
- ✅ 主应用健康检查
- ✅ 主应用端点测试
- ✅ 集成测试（检查配置）

---

## 方式 2: 手动 curl 测试

### 1️⃣ 测试签名服务器 (Render)

**替换 `YOUR_RENDER_URL` 为你的 Render 部署地址**

#### 测试健康检查
```bash
curl https://YOUR_RENDER_URL/health
```

**预期响应：**
```json
{
  "status": "healthy",
  "browser_ready": true,
  "a1": "...",
  "timestamp": 1234567890
}
```

#### 测试根路径
```bash
curl https://YOUR_RENDER_URL/
```

**预期响应：**
```json
{
  "service": "XHS Signature Server",
  "description": "小红书 API 签名服务",
  "status": "running",
  "version": "1.0.0"
}
```

#### 测试签名功能
```bash
curl -X POST https://YOUR_RENDER_URL/sign \
  -H "Content-Type: application/json" \
  -d '{
    "uri": "/api/sns/web/v1/user_posted",
    "data": null,
    "a1": "test_a1",
    "web_session": "test_session"
  }'
```

**预期响应：**
```json
{
  "x-s": "...",
  "x-t": "1234567890"
}
```

#### 测试获取 A1
```bash
curl https://YOUR_RENDER_URL/a1
```

**预期响应：**
```json
{
  "a1": "..."
}
```

---

### 2️⃣ 测试主应用 (Vercel)

**替换 `YOUR_VERCEL_URL` 为你的 Vercel 部署地址**

#### 测试健康检查
```bash
curl https://YOUR_VERCEL_URL/health
```

**预期响应：**
```json
{
  "status": "ok",
  "timestamp": 1234567890,
  "sign_server_configured": true
}
```

#### 测试根路径
```bash
curl https://YOUR_VERCEL_URL/
```

**预期响应：**
```json
{
  "app": "EasyGo XHS Publisher",
  "version": "1.0.0",
  "endpoints": [...]
}
```

#### 测试发布接口（需要真实 Cookie）
```bash
curl -X POST https://YOUR_VERCEL_URL/publish \
  -H "Content-Type: application/json" \
  -d '{
    "cookie": "YOUR_XHS_COOKIE",
    "title": "测试标题",
    "desc": "测试描述",
    "type": "normal"
  }'
```

---

## 方式 3: PowerShell 测试（Windows）

### 创建测试脚本

将以下内容保存为 `test.ps1`：

```powershell
# 配置你的部署地址
$SignServerUrl = "https://YOUR_RENDER_URL"
$MainAppUrl = "https://YOUR_VERCEL_URL"

Write-Host "`n=== 测试签名服务器 ===" -ForegroundColor Cyan

# 测试健康检查
Write-Host "`n1. 健康检查..." -ForegroundColor Yellow
try {
    $response = Invoke-RestMethod -Uri "$SignServerUrl/health" -Method Get
    Write-Host "✅ 健康检查通过" -ForegroundColor Green
    Write-Host "   状态: $($response.status)"
    Write-Host "   浏览器就绪: $($response.browser_ready)"
} catch {
    Write-Host "❌ 健康检查失败: $_" -ForegroundColor Red
}

# 测试签名功能
Write-Host "`n2. 签名功能..." -ForegroundColor Yellow
try {
    $body = @{
        uri = "/api/sns/web/v1/user_posted"
        data = $null
        a1 = "test_a1"
        web_session = "test_session"
    } | ConvertTo-Json

    $response = Invoke-RestMethod -Uri "$SignServerUrl/sign" -Method Post -Body $body -ContentType "application/json"
    Write-Host "✅ 签名生成成功" -ForegroundColor Green
    Write-Host "   x-t: $($response.'x-t')"
} catch {
    Write-Host "❌ 签名生成失败: $_" -ForegroundColor Red
}

Write-Host "`n=== 测试主应用 ===" -ForegroundColor Cyan

# 测试健康检查
Write-Host "`n3. 主应用健康检查..." -ForegroundColor Yellow
try {
    $response = Invoke-RestMethod -Uri "$MainAppUrl/health" -Method Get
    Write-Host "✅ 健康检查通过" -ForegroundColor Green
    Write-Host "   状态: $($response.status)"
    Write-Host "   签名服务器配置: $($response.sign_server_configured)"
} catch {
    Write-Host "❌ 健康检查失败: $_" -ForegroundColor Red
}

Write-Host "`n=== 测试完成 ===" -ForegroundColor Cyan
```

### 运行脚本

```powershell
# 执行策略可能需要设置
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass

# 运行测试
.\test.ps1
```

---

## 🔍 故障排查

### 签名服务器问题

**问题：健康检查返回 503**
- 检查 Render Dashboard 日志
- 浏览器可能还在初始化（等待 1-2 分钟）
- 查看是否有构建错误

**问题：签名生成失败**
- 检查浏览器是否正常启动
- 查看 `/a1` 端点是否返回有效值
- 检查 Dockerfile 和依赖安装

**问题：服务频繁重启**
- 检查内存使用（免费套餐限制）
- 查看是否有崩溃日志
- 考虑升级到付费套餐

### 主应用问题

**问题：sign_server_configured 为 false**
- 在 Vercel Dashboard 中设置环境变量 `XHS_SIGN_SERVER_URL`
- 值应为: `https://your-render-url.onrender.com`（不要末尾斜杠）
- 重新部署 Vercel 应用

**问题：发布请求失败**
- 检查 Cookie 是否有效
- 查看错误信息中的具体原因
- 确认签名服务器能正常访问

**问题：超时错误**
- Render 免费套餐冷启动需要时间
- 第一次请求可能需要 30-60 秒
- 考虑使用定时 ping 保持服务活跃

---

## 📊 检查清单

部署完成后，确认以下所有项：

### 签名服务器 (Render)
- [ ] 构建成功，无错误
- [ ] 服务状态显示为 "Running"
- [ ] `/health` 返回 200 和 healthy
- [ ] `/sign` 可以生成签名
- [ ] 日志中显示浏览器初始化成功

### 主应用 (Vercel)
- [ ] 构建成功，无错误
- [ ] 部署状态显示为 "Ready"
- [ ] `/health` 返回 200
- [ ] `sign_server_configured` 为 true
- [ ] 环境变量 `XHS_SIGN_SERVER_URL` 已设置

### 集成测试
- [ ] 主应用能成功调用签名服务器
- [ ] 使用真实 Cookie 测试发布功能
- [ ] 响应时间在可接受范围内（< 30 秒）

---

## 🎯 生产环境建议

### Render 签名服务器

1. **保持服务活跃**（避免冷启动）
   ```bash
   # 使用 cron 或监控服务定时 ping
   curl https://your-render-url.onrender.com/health
   ```

2. **监控日志**
   - 在 Render Dashboard 中查看实时日志
   - 注意内存使用情况
   - 关注浏览器崩溃/重启

3. **考虑升级套餐**
   - 免费套餐有 15 分钟不活跃自动休眠
   - 付费套餐可获得更好性能和稳定性

### Vercel 主应用

1. **配置环境变量**
   - 生产环境单独配置
   - 定期检查签名服务器可用性

2. **监控使用量**
   - 注意 Serverless 函数调用次数
   - 监控响应时间

3. **错误追踪**
   - 集成 Sentry 或其他错误追踪服务
   - 定期查看 Vercel 日志

---

## 📚 相关文档

- [Render 文档](https://render.com/docs)
- [Vercel 文档](https://vercel.com/docs)
- [Playwright 文档](https://playwright.dev/python/)
- [小红书 API 文档](https://github.com/ReaJason/xhs)

---

## ❓ 常见问题

**Q: 签名服务器需要多久才能启动？**
A: 首次部署约 3-5 分钟，冷启动约 30-60 秒。

**Q: 免费套餐够用吗？**
A: 轻度使用可以，但会有冷启动延迟。频繁使用建议付费。

**Q: 如何获取 Render 和 Vercel 的部署地址？**
A: 
- Render: 在 Dashboard 中查看服务的 URL
- Vercel: 在项目页面查看 Deployment URL

**Q: 可以用其他平台部署吗？**
A: 
- 签名服务器：可以用 Railway, Fly.io, AWS 等
- 主应用：可以用 Netlify, Cloudflare Pages 等

---

祝部署顺利！🚀
