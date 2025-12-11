@echo off
echo ================================
echo 创建前端环境配置文件
echo ================================
echo.

cd /d "%~dp0"

echo 正在创建 .env.development 文件...
echo VITE_API_BASE_URL=http://localhost:8000 > .env.development

if exist .env.development (
    echo [成功] .env.development 文件已创建
    echo.
    echo 文件内容：
    type .env.development
    echo.
    echo ================================
    echo 配置完成！
    echo 现在可以启动开发服务器了：
    echo   npm run dev
    echo 或
    echo   pnpm dev
    echo ================================
) else (
    echo [错误] 创建文件失败
)

echo.
pause

