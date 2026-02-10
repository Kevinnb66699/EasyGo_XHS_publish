# 部署检查清单

## 🚀 部署前检查

- [ ] 代码已提交到 Git
- [ ] 所有依赖项已添加到 `requirements.txt`
- [ ] `vercel.json` 配置正确
- [ ] 本地测试通过

## 📝 部署步骤

### 1. 本地测试
```bash
# 安装依赖
pip install -r requirements.txt

# 启动服务
python app.py

# 在另一个终端运行测试
python test_logging.py
```

**预期结果**: 
- ✅ 终端显示详细日志
- ✅ 所有测试通过
- ✅ 可以看到请求/响应日志

### 2. 提交代码
```bash
git add .
git commit -m "修复: 改进日志配置以支持 Vercel 环境"
git push origin main
```

### 3. 部署到 Vercel
```bash
# 如果是第一次部署
vercel

# 生产环境部署
vercel --prod
```

### 4. 验证部署

#### 4.1 检查部署状态
```bash
vercel ls
```

#### 4.2 查看实时日志
```bash
vercel logs --follow
```

#### 4.3 测试 API
```bash
# 测试健康检查
curl https://your-app.vercel.app/api/health

# 测试错误处理 (应该返回 400 并有日志)
curl -X POST https://your-app.vercel.app/api/publish \
  -H "Content-Type: application/json" \
  -d '{"test": "data"}'
```

#### 4.4 修改测试脚本并运行
```python
# 编辑 test_logging.py
BASE_URL = "https://your-app.vercel.app"

# 运行测试
python test_logging.py
```

## 🔍 日志检查

### 在 Vercel 控制台
1. 访问 https://vercel.com/dashboard
2. 选择项目
3. 点击 "Logs" 或 "Functions"
4. 应该看到类似输出:

```
2026-02-10 10:00:00 - __main__ - INFO - ==================================================
2026-02-10 10:00:00 - __main__ - INFO - Flask 应用启动成功
2026-02-10 10:00:00 - __main__ - INFO - Python 版本: 3.9.x
2026-02-10 10:00:00 - __main__ - INFO - ==================================================
2026-02-10 10:00:05 - __main__ - INFO - 收到请求 [POST] /api/publish
2026-02-10 10:00:05 - __main__ - INFO - 来源 IP: xxx.xxx.xxx.xxx
```

### 使用命令行
```bash
# 持续监控
vercel logs --follow

# 查看最近 100 条
vercel logs -n 100

# 过滤错误
vercel logs | grep ERROR
```

## ✅ 验证清单

部署后验证以下内容:

### 基础功能
- [ ] 根路径 `/` 返回正常
- [ ] 健康检查 `/api/health` 返回 200
- [ ] 日志正常输出到 Vercel

### 错误处理
- [ ] 缺少 Cookie 返回 400 (带日志)
- [ ] 无效 Cookie 返回 401 (带日志)
- [ ] 缺少必填字段返回 400 (带日志)
- [ ] 404 错误有日志记录
- [ ] 500 错误有完整堆栈跟踪

### 日志完整性
- [ ] 每个请求都有开始日志
- [ ] 每个响应都有状态码日志
- [ ] 错误有详细的 traceback
- [ ] 日志包含时间戳和级别

## 🐛 常见问题排查

### 问题 1: 部署成功但访问 500
**排查步骤**:
```bash
# 1. 查看日志
vercel logs --follow

# 2. 检查环境变量
vercel env ls

# 3. 查看构建日志
vercel inspect [deployment-url]
```

### 问题 2: 日志不显示
**排查步骤**:
1. 确认代码已推送: `git log -1`
2. 确认部署成功: `vercel ls`
3. 等待 10-30 秒让日志同步
4. 尝试触发一个错误请求
5. 刷新 Vercel 控制台

### 问题 3: 依赖安装失败
**解决方案**:
```bash
# 检查 requirements.txt
cat requirements.txt

# 确保版本兼容
pip install -r requirements.txt --dry-run

# 如果有问题，锁定版本
pip freeze > requirements.txt
```

### 问题 4: 超时错误
**解决方案**:
- Vercel Hobby 计划: 10秒超时
- 优化图片下载逻辑
- 考虑使用异步处理

## 📊 监控建议

### 实时监控
```bash
# Terminal 1: 监控日志
vercel logs --follow

# Terminal 2: 发送测试请求
while true; do
  curl https://your-app.vercel.app/api/health
  sleep 5
done
```

### 定期检查
- 每天检查错误日志
- 每周查看性能指标
- 每月审查成本和使用量

## 🎯 性能优化 (可选)

1. **添加缓存**:
   - Cookie 验证结果
   - 图片下载

2. **优化日志**:
   - 生产环境使用 WARNING 级别
   - 采样高频日志

3. **错误追踪**:
   - 集成 Sentry
   - 设置告警规则

## 📞 获取帮助

如果遇到问题:
1. ✅ 查看 `TROUBLESHOOTING.md`
2. ✅ 检查 Vercel 文档: https://vercel.com/docs
3. ✅ 查看项目 Issues
4. ✅ Vercel 状态: https://www.vercel-status.com/

---

**最后更新**: 2026-02-10
**版本**: 1.0.0
