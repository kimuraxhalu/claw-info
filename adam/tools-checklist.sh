#!/bin/bash
# ~/adam/tools-checklist.sh
# Genesis 3.0 基礎設施驗證腳本

echo "🔧 Genesis 3.0 工具鏈檢查"
echo "========================"

# 1. OpenClaw 狀態
echo -n "OpenClaw CLI: "
VER=$(openclaw --version 2>/dev/null)
if [ -n "$VER" ]; then echo "✅ $VER"; else echo "❌ 未安裝"; fi

# 2. Gateway 狀態
echo -n "Gateway: "
openclaw gateway health >/dev/null 2>&1 && echo "✅ 運行中" || echo "❌ 未啟動"

# 3. Dashboard 狀態
echo -n "Dashboard: "
curl -s -o /dev/null -w "" http://localhost:7000 2>/dev/null && echo "✅ 運行中 (http://localhost:7000)" || echo "❌ 未啟動"

# 4. Telegram Bot
echo -n "Telegram Bot: "
if [ -n "$TELEGRAM_BOT_TOKEN" ]; then
    RESULT=$(curl -s "https://api.telegram.org/bot${TELEGRAM_BOT_TOKEN}/getMe" 2>/dev/null)
    if echo "$RESULT" | grep -q '"ok":true'; then
        BOT_NAME=$(echo "$RESULT" | grep -o '"username":"[^"]*"' | cut -d'"' -f4)
        echo "✅ 在線 (@$BOT_NAME)"
    else
        echo "❌ Token 無效"
    fi
else
    echo "❌ TELEGRAM_BOT_TOKEN 未設定"
fi

# 5. AWS 連接
echo -n "AWS 權限: "
if [ -n "$AWS_ACCESS_KEY_ID" ]; then
    AWS_ID=$(aws sts get-caller-identity --query 'Account' --output text 2>/dev/null)
    if [ -n "$AWS_ID" ]; then
        echo "✅ 帳號 $AWS_ID"
    else
        echo "⚠️  Key 已設但無法驗證 (需安裝 aws-cli)"
    fi
else
    echo "❌ AWS_ACCESS_KEY_ID 未設定"
fi

# 6. GitHub 記憶庫
echo -n "GitHub Token: "
if [ -n "$GH_TOKEN" ]; then
    echo "✅ 已設定 (${GH_TOKEN:0:10}...)"
else
    echo "❌ GH_TOKEN 未設定"
fi

# 7. Ollama（本地或遠端）
echo -n "Ollama: "
if command -v ollama &>/dev/null; then
    echo "✅ 本地已安裝 ($(ollama --version 2>/dev/null))"
elif [ -n "$OLLAMA_HOST" ] && [ "$OLLAMA_HOST" != "http://placeholder:11434" ]; then
    echo "✅ 遠端 ($OLLAMA_HOST)"
else
    echo "⚠️  未連接（等待 Phase 1 AWS EC2 部署）"
fi

# 8. Secrets 完整性
echo ""
echo "--- Secrets 狀態 ---"
for VAR in AWS_ACCESS_KEY_ID AWS_SECRET_ACCESS_KEY TELEGRAM_BOT_TOKEN TELEGRAM_USER_ID GH_TOKEN; do
    VAL=$(eval echo \$$VAR)
    if [ -n "$VAL" ]; then
        echo "  $VAR: ✅"
    else
        echo "  $VAR: ❌ 缺失"
    fi
done

echo ""
echo "========================"
echo "📋 下一步："
echo "  1. Dashboard: http://localhost:7000"
echo "  2. 平台申請清單: ~/adam/platform-checklist.md"
echo "  3. Phase 1 (AWS 軍營): 部署 EC2 + Ollama"
