@echo off
REM 快速部署脚本 - 适用于 Windows

echo 🚀 开始部署到 Vercel...
echo.

REM 检查是否有未提交的更改
git status --short > nul 2>&1
if errorlevel 1 (
    echo ❌ Git 仓库未初始化，请先运行: git init
    pause
    exit /b 1
)

REM 添加所有更改
echo 📝 添加所有更改...
git add .

REM 提交更改
set /p commit_msg="请输入提交信息 (直接回车使用默认 'Update'): "
if "%commit_msg%"=="" set commit_msg=Update

git commit -m "%commit_msg%"
if errorlevel 1 (
    echo ℹ️  没有需要提交的更改
) else (
    echo ✅ 代码已提交
)
echo.

REM 推送到远程仓库
echo 📤 推送代码到 GitHub...
git push
if errorlevel 1 (
    echo ❌ 推送失败，请检查：
    echo    1. 是否已添加远程仓库: git remote add origin YOUR_REPO_URL
    echo    2. 是否已设置上游分支: git push -u origin main
    pause
    exit /b 1
)
echo ✅ 代码已推送
echo.

echo ⏳ Vercel 正在自动部署（大约需要 1-2 分钟）...
echo.
echo 📍 部署完成后访问：
echo    健康检查: https://easygo-xhs-publish.vercel.app/api/health
echo    发布接口: https://easygo-xhs-publish.vercel.app/api/publish
echo.
echo 💡 提示: 你可以在 Vercel 控制台查看部署进度
echo    https://vercel.com/dashboard
echo.
echo 🎉 部署脚本执行完成！
echo.
pause
