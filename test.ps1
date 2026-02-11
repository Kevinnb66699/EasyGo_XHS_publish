# 🧪 EasyGo XHS 部署测试脚本 (PowerShell)
# 使用方法: .\test.ps1

param(
    [Parameter(Mandatory=$false)]
    [string]$SignServerUrl = "",
    
    [Parameter(Mandatory=$false)]
    [string]$MainAppUrl = ""
)

# 颜色输出函数
function Write-Success {
    param([string]$Message)
    Write-Host "✅ $Message" -ForegroundColor Green
}

function Write-Error-Custom {
    param([string]$Message)
    Write-Host "❌ $Message" -ForegroundColor Red
}

function Write-Warning-Custom {
    param([string]$Message)
    Write-Host "⚠️  $Message" -ForegroundColor Yellow
}

function Write-Info {
    param([string]$Message)
    Write-Host "ℹ️  $Message" -ForegroundColor Cyan
}

function Write-Header {
    param([string]$Message)
    Write-Host "`n============================================================" -ForegroundColor White
    Write-Host $Message -ForegroundColor White
    Write-Host "============================================================`n" -ForegroundColor White
}

# 如果没有提供参数，则提示输入
if (-not $SignServerUrl) {
    Write-Host "请输入部署的 URL：`n" -ForegroundColor White
    $SignServerUrl = Read-Host "1️⃣  签名服务器 URL (Render)`n   例如: https://xhs-sign-server.onrender.com`n   > "
    $MainAppUrl = Read-Host "`n2️⃣  主应用 URL (Vercel)`n   例如: https://your-app.vercel.app`n   > "
}

# 移除末尾的斜杠
$SignServerUrl = $SignServerUrl.TrimEnd('/')
$MainAppUrl = $MainAppUrl.TrimEnd('/')

Write-Host "`n开始测试...`n" -ForegroundColor White
Start-Sleep -Seconds 1

# ====================================
# 测试 1: 签名服务器
# ====================================
Write-Header "测试 1: 签名服务器 (Render)"

$signServerResults = @{
    HealthCheck = $false
    RootEndpoint = $false
    SignFunction = $false
    A1Endpoint = $false
}

# 1.1 健康检查
Write-Info "测试健康检查接口: $SignServerUrl/health"
try {
    $response = Invoke-RestMethod -Uri "$SignServerUrl/health" -Method Get -TimeoutSec 10
    Write-Success "健康检查通过"
    Write-Host "   状态: $($response.status)"
    Write-Host "   浏览器就绪: $($response.browser_ready)"
    Write-Host "   A1: $($response.a1.Substring(0, [Math]::Min(30, $response.a1.Length)))..."
    $signServerResults.HealthCheck = $true
} catch {
    Write-Error-Custom "健康检查失败: $_"
}

# 1.2 根路径
Write-Info "测试根路径: $SignServerUrl/"
try {
    $response = Invoke-RestMethod -Uri "$SignServerUrl/" -Method Get -TimeoutSec 10
    Write-Success "根路径访问成功"
    Write-Host "   服务: $($response.service)"
    Write-Host "   版本: $($response.version)"
    $signServerResults.RootEndpoint = $true
} catch {
    Write-Error-Custom "根路径访问失败: $_"
}

# 1.3 A1 端点
Write-Info "测试 A1 端点: $SignServerUrl/a1"
try {
    $response = Invoke-RestMethod -Uri "$SignServerUrl/a1" -Method Get -TimeoutSec 10
    Write-Success "A1 获取成功"
    Write-Host "   A1: $($response.a1.Substring(0, [Math]::Min(50, $response.a1.Length)))..."
    $signServerResults.A1Endpoint = $true
} catch {
    Write-Error-Custom "A1 获取失败: $_"
}

# 1.4 签名功能
Write-Info "测试签名功能: $SignServerUrl/sign"
try {
    $body = @{
        uri = "/api/sns/web/v1/user_posted"
        data = $null
        a1 = "test_a1"
        web_session = "test_session"
    } | ConvertTo-Json

    $response = Invoke-RestMethod -Uri "$SignServerUrl/sign" -Method Post -Body $body -ContentType "application/json" -TimeoutSec 30
    Write-Success "签名生成成功"
    
    # 显示完整响应
    Write-Host "   完整响应: $($response | ConvertTo-Json -Depth 10)"
    
    # 检查字段
    $xs = $response.'x-s'
    $xt = $response.'x-t'
    
    if ($xs) {
        $xsDisplay = if ($xs.Length -gt 50) { $xs.Substring(0, 50) + "..." } else { $xs }
        Write-Host "   ✅ x-s: $xsDisplay" -ForegroundColor Green
    } else {
        Write-Warning-Custom "   x-s 字段为空或不存在"
    }
    
    if ($xt) {
        Write-Host "   ✅ x-t: $xt" -ForegroundColor Green
    } else {
        Write-Warning-Custom "   x-t 字段为空或不存在"
    }
    
    # 只有两个字段都存在才算成功
    if ($xs -and $xt) {
        $signServerResults.SignFunction = $true
    } else {
        Write-Error-Custom "   签名不完整，缺少必要字段"
    }
} catch {
    Write-Error-Custom "签名生成失败: $_"
}

# 签名服务器测试总结
Write-Host "`n------------------------------------------------------------"
$signServerAllPassed = ($signServerResults.Values | Where-Object { $_ -eq $false }).Count -eq 0
if ($signServerAllPassed) {
    Write-Success "签名服务器所有测试通过！"
} else {
    Write-Warning-Custom "签名服务器部分测试失败"
    foreach ($test in $signServerResults.GetEnumerator()) {
        $status = if ($test.Value) { "✅" } else { "❌" }
        Write-Host "   $status $($test.Key)"
    }
}

Start-Sleep -Seconds 1

# ====================================
# 测试 2: 主应用
# ====================================
Write-Header "测试 2: 主应用 (Vercel)"

$mainAppResults = @{
    HealthCheck = $false
    RootEndpoint = $false
    PublishEndpoint = $false
}

# 2.1 健康检查
Write-Info "测试健康检查接口: $MainAppUrl/health"
try {
    $response = Invoke-RestMethod -Uri "$MainAppUrl/health" -Method Get -TimeoutSec 10
    Write-Success "健康检查通过"
    Write-Host "   状态: $($response.status)"
    Write-Host "   签名服务器: $($response.sign_server_configured)"
    $mainAppResults.HealthCheck = $true
} catch {
    Write-Error-Custom "健康检查失败: $_"
}

# 2.2 根路径
Write-Info "测试根路径: $MainAppUrl/"
try {
    $response = Invoke-RestMethod -Uri "$MainAppUrl/" -Method Get -TimeoutSec 10
    Write-Success "根路径访问成功"
    Write-Host "   应用: $($response.app)"
    Write-Host "   版本: $($response.version)"
    $mainAppResults.RootEndpoint = $true
} catch {
    Write-Error-Custom "根路径访问失败: $_"
}

# 2.3 发布端点
Write-Info "测试发布端点: $MainAppUrl/publish"
Write-Warning-Custom "注意：发布端点需要有效的 Cookie，这里只测试端点是否可访问"
try {
    $body = @{
        cookie = "test_cookie"
        title = "测试标题"
        desc = "测试描述"
        type = "normal"
    } | ConvertTo-Json

    $response = Invoke-RestMethod -Uri "$MainAppUrl/publish" -Method Post -Body $body -ContentType "application/json" -TimeoutSec 30
    Write-Success "发布端点可访问"
    Write-Host "   响应: OK"
    $mainAppResults.PublishEndpoint = $true
} catch {
    # 400 或 500 也说明端点可访问
    if ($_.Exception.Response.StatusCode -in @(400, 401, 500)) {
        Write-Success "发布端点可访问"
        Write-Host "   状态码: $($_.Exception.Response.StatusCode)"
        $mainAppResults.PublishEndpoint = $true
    } else {
        Write-Error-Custom "发布端点不可访问: $_"
    }
}

# 主应用测试总结
Write-Host "`n------------------------------------------------------------"
$mainAppAllPassed = ($mainAppResults.Values | Where-Object { $_ -eq $false }).Count -eq 0
if ($mainAppAllPassed) {
    Write-Success "主应用所有测试通过！"
} else {
    Write-Warning-Custom "主应用部分测试失败"
    foreach ($test in $mainAppResults.GetEnumerator()) {
        $status = if ($test.Value) { "✅" } else { "❌" }
        Write-Host "   $status $($test.Key)"
    }
}

Start-Sleep -Seconds 1

# ====================================
# 测试 3: 集成测试
# ====================================
Write-Header "测试 3: 集成测试"

Write-Info "检查主应用的健康状态中签名服务器配置..."

$integrationOk = $false
try {
    $response = Invoke-RestMethod -Uri "$MainAppUrl/health" -Method Get -TimeoutSec 10
    $signServerConfigured = $response.sign_server_configured
    
    if ($signServerConfigured) {
        Write-Success "主应用已正确配置签名服务器"
        $integrationOk = $true
    } else {
        Write-Error-Custom "主应用未配置签名服务器"
        Write-Warning-Custom "请在 Vercel 环境变量中设置 XHS_SIGN_SERVER_URL"
        Write-Info "值应为: $SignServerUrl"
    }
} catch {
    Write-Error-Custom "集成测试异常: $_"
}

# ====================================
# 最终总结
# ====================================
Write-Header "📊 测试总结"

Write-Host "`n============================================================"
Write-Host "测试结果：`n" -ForegroundColor White

$signStatus = if ($signServerAllPassed) { "✅ 通过" } else { "❌ 失败" }
$mainStatus = if ($mainAppAllPassed) { "✅ 通过" } else { "❌ 失败" }
$integrationStatus = if ($integrationOk) { "✅ 通过" } else { "❌ 失败" }

Write-Host "签名服务器 (Render): $signStatus"
Write-Host "主应用 (Vercel):     $mainStatus"
Write-Host "集成测试:           $integrationStatus"

Write-Host "`n============================================================`n"

if ($signServerAllPassed -and $mainAppAllPassed -and $integrationOk) {
    Write-Success "🎉 所有测试通过！部署成功！"
    Write-Host "`n下一步：" -ForegroundColor White
    Write-Host "1. 使用真实的小红书 Cookie 测试发布功能"
    Write-Host "2. 监控 Render 和 Vercel 的日志"
    Write-Host "3. 查看 Render Dashboard 确认服务运行正常"
} else {
    Write-Error-Custom "部分测试失败，请检查："
    if (-not $signServerAllPassed) {
        Write-Host "  • 签名服务器部署状态"
        Write-Host "  • Render 构建日志"
        Write-Host "  • Docker 镜像是否正确"
    }
    if (-not $mainAppAllPassed) {
        Write-Host "  • 主应用部署状态"
        Write-Host "  • Vercel 构建日志"
    }
    if (-not $integrationOk) {
        Write-Host "  • Vercel 环境变量配置"
        Write-Host "  • XHS_SIGN_SERVER_URL 应设置为: $SignServerUrl"
    }
}

Write-Host ""
