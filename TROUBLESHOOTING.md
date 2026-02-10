# 问题排查指南

## 问题描述
发布后后端出现 500 错误，但日志没有输出。

## 根本原因
在 Vercel 这样的无服务器环境中，日志配置需要特别处理：

1. **日志缓冲问题**: 标准的 `logging.basicConfig()` 在无服务器环境中可能不会立即输出
2. **缺少全局错误处理**: 某些异常可能在 Flask 路由处理之外发生
3. **日志没有强制刷新**: 在 Lambda 函数结束前，日志可能被缓冲而不输出

## 修复方案

### 1. 改进日志配置
✅ 使用 `StreamHandler` 直接输出到 `stdout`
✅ 在关键位置添加 `sys.stdout.flush()` 强制刷新
✅ 设置详细的日志格式

### 2. 添加全局错误处理器
✅ 捕获所有未处理的异常
✅ 记录请求和响应日志
✅ 处理 400、404、500 等错误

### 3. 增强错误追踪
✅ 在所有 try-except 块中添加 `exc_info=True`
✅ 在错误日志后立即刷新输出
✅ 记录更详细的上下文信息

## 测试步骤

### 本地测试

1. **启动本地服务器**:
   ```bash
   python app.py
   ```

2. **运行测试脚本**:
   ```bash
   python test_logging.py
   ```

3. **检查输出**:
   - 终端应该显示详细的请求/响应日志
   - 每个测试都应该有对应的日志输出
   - 错误信息应该包含完整的堆栈跟踪

### Vercel 部署测试

1. **部署到 Vercel**:
   ```bash
   vercel --prod
   ```

2. **查看实时日志**:
   ```bash
   vercel logs --follow
   ```
   或访问 Vercel 控制台: https://vercel.com/dashboard

3. **发送测试请求**:
   ```bash
   # 修改 test_logging.py 中的 BASE_URL
   BASE_URL = "https://your-app.vercel.app"
   
   # 运行测试
   python test_logging.py
   ```

4. **在 Vercel 控制台查看日志**:
   - 进入项目 → Functions 标签
   - 点击具体的函数调用
   - 查看完整的日志输出

## 如何查看 Vercel 日志

### 方法 1: 命令行 (推荐)
```bash
# 实时查看日志
vercel logs --follow

# 查看最近的日志
vercel logs

# 查看特定部署的日志
vercel logs [deployment-url]
```

### 方法 2: Web 控制台
1. 访问 https://vercel.com/dashboard
2. 选择你的项目
3. 点击 "Logs" 或 "Functions" 标签
4. 选择具体的函数调用查看详细日志

### 方法 3: 使用 Vercel API
```bash
curl -H "Authorization: Bearer YOUR_TOKEN" \
  "https://api.vercel.com/v2/deployments/DEPLOYMENT_ID/events"
```

## 常见问题

### Q1: 日志在本地正常，但 Vercel 上没有
**A**: 确保代码已经推送到 Git 并重新部署：
```bash
git add .
git commit -m "修复日志配置"
git push
vercel --prod
```

### Q2: 仍然看不到日志
**A**: 检查以下几点：
1. 确认部署成功: `vercel ls`
2. 等待几秒让日志系统同步
3. 使用 `vercel logs --follow` 实时监控
4. 检查 Vercel 项目设置中的日志级别

### Q3: 500 错误但没有错误详情
**A**: 现在全局错误处理器会捕获所有异常，返回结构应该包含：
```json
{
  "success": false,
  "error": "错误信息",
  "error_type": "异常类型"
}
```

### Q4: 日志显示乱码
**A**: 已在日志格式化器中使用 UTF-8 编码，如果仍有问题：
```python
# 在 app.py 顶部添加
import sys
sys.stdout.reconfigure(encoding='utf-8')
```

## 调试技巧

### 1. 添加更多日志点
在关键位置添加日志：
```python
logger.info(f"当前状态: {some_variable}")
sys.stdout.flush()
```

### 2. 使用 Vercel 环境变量
在 Vercel 设置中添加：
```
LOG_LEVEL=DEBUG
```

然后在代码中使用：
```python
import os
log_level = os.getenv('LOG_LEVEL', 'INFO')
logger.setLevel(getattr(logging, log_level))
```

### 3. 监控性能
查看函数执行时间：
```bash
vercel logs --follow | grep "Duration"
```

### 4. 测试特定错误场景
创建专门的测试端点：
```python
@app.get('/test/error')
def test_error():
    logger.info("测试错误处理")
    sys.stdout.flush()
    raise Exception("这是一个测试错误")
```

## 下一步优化建议

1. **集成错误追踪服务**: 
   - Sentry: 自动捕获和报告错误
   - Datadog: 全面的日志聚合和分析

2. **结构化日志**:
   - 使用 JSON 格式日志
   - 便于后续分析和告警

3. **性能监控**:
   - 添加请求耗时统计
   - 监控外部 API 调用延迟

4. **日志采样**:
   - 在高流量场景下采样日志
   - 避免日志成本过高

## 联系支持

如果问题仍然存在：
1. 收集完整的错误信息和日志
2. 记录重现步骤
3. 检查 Vercel 状态页: https://www.vercel-status.com/
