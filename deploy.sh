#!/bin/bash
# 快速部署脚本 - 适用于 Mac/Linux

echo "🚀 开始部署到 Vercel..."
echo ""

# 检查是否有未提交的更改
if [[ -n $(git status -s) ]]; then
    echo "📝 检测到未提交的更改，准备提交..."
    git add .
    
    # 提示输入提交信息
    read -p "请输入提交信息 (默认: Update): " commit_msg
    commit_msg=${commit_msg:-"Update"}
    
    git commit -m "$commit_msg"
    echo "✅ 代码已提交"
    echo ""
else
    echo "✅ 没有未提交的更改"
    echo ""
fi

# 推送到远程仓库
echo "📤 推送代码到 GitHub..."
git push
echo "✅ 代码已推送"
echo ""

echo "⏳ Vercel 正在自动部署（大约需要 1-2 分钟）..."
echo ""
echo "📍 部署完成后访问："
echo "   健康检查: https://easygo-xhs-publish.vercel.app/api/health"
echo "   发布接口: https://easygo-xhs-publish.vercel.app/api/publish"
echo ""
echo "💡 提示: 你可以在 Vercel 控制台查看部署进度"
echo "   https://vercel.com/dashboard"
echo ""
echo "🎉 部署脚本执行完成！"
