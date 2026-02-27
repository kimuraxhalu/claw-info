# PROJECT ADAM - 極速版（Python實現）
# 功能：五條悟（成本監控）+ 成振宇（Telegram接口）+ 闇遊戲（GitHub備份）

import os
import json
import time
from datetime import datetime
from telegram.ext import MessageHandler, filters
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
import requests

# 設定（從環境變數讀取，下面會教你點設）
TELEGRAM_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
OPENAI_KEY = os.getenv('OPENAI_API_KEY')
GITHUB_TOKEN = os.getenv('GITHUB_TOKEN')
REPO_NAME = "kimuraxhalu/claw-info"

# 五條悟 - 成本守衛
class Gojo:
    def __init__(self):
        self.daily_budget = 0.80  # USD
        self.today_cost = 0.0
        self.last_reset = datetime.now().day
        
    def check_budget(self, cost=0):
        if datetime.now().day != self.last_reset:
            self.today_cost = 0
            self.last_reset = datetime.now().day
        
        self.today_cost += cost
        remaining = self.daily_budget - self.today_cost
        percentage = (self.today_cost / self.daily_budget) * 100
        
        if percentage >= 100:
            return f"🚨 熔斷啟動！已達 ${self.today_cost:.2f}/{self.daily_budget}，切換到免費模式"
        elif percentage >= 80:
            return f"⚠️ 警告：已用 {percentage:.0f}% (${self.today_cost:.2f})"
        else:
            return f"✅ 成本正常：{percentage:.0f}% (${self.today_cost:.2f}/{self.daily_budget})"

# 成振宇 - 命令處理
class SungJinWoo:
    def __init__(self):
        self.gojo = Gojo()
        
    async def status(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        report = self.gojo.check_budget()
        await update.message.reply_text(
            f"🦞 Adam 狀態報告\n"
            f"五條悟：{report}\n"
            f"成振宇：在線\n"
            f"闇遊戲：待同步\n"
            f"利姆路：休眠（Phase 3先開）"
        )
    
    async def cost(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        report = self.gojo.check_budget()
        await update.message.reply_text(report)
    
    async def evolve(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        await update.message.reply_text(
            "🧬 利姆路進化功能（Phase 3）\n"
            "現在係 Phase 1，請一週後再試\n"
            "或者手動觸發：去 GitHub Actions 撳「Weekly Mutation」"
        )

# 闇遊戲 - GitHub同步（簡易版）
class Yugi:
    def seal_memory(self, content):
        """將對話備份到GitHub Issue（簡易版，之後可改Commit）"""
        url = f"https://api.github.com/repos/{REPO_NAME}/issues"
        headers = {
            "Authorization": f"token {GITHUB_TOKEN}",
            "Accept": "application/vnd.github.v3+json"
        }
        data = {
            "title": f"Memory Seal {datetime.now().strftime('%Y-%m-%d %H:%M')}",
            "body": content,
            "labels": ["memory", "auto"]
        }
        try:
            r = requests.post(url, headers=headers, json=data)
            return r.status_code == 201
        except:
            return False

# 主程序
def main():
    print("🦞 Adam 啟動中...")
    
    # 檢查設定
    if not TELEGRAM_TOKEN:
        print("❌ 錯誤：請設定 TELEGRAM_BOT_TOKEN")
        return
    
    # 創建 Application
    application = Application.builder().token(TELEGRAM_TOKEN).build()
    
    # 註冊指令
    sung = SungJinWoo()
    application.add_handler(CommandHandler("status", sung.status))
    application.add_handler(CommandHandler("cost", sung.cost))
    application.add_handler(CommandHandler("evolve", sung.evolve))
    # 註冊 Echo Handler（處理所有非指令文字訊息）
    async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """處理普通文字（Phase 1 暫時回應，Phase 2 改由 AI 處理）"""
        text = update.message.text
        await update.message.reply_text(f"🦞 Adam 聽到：{text}\n（Phase 1 暫時複述，Phase 2 將理解內容）")
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))
    
    # 啟動
    print("✅ Adam 已上線！ Telegram Bot 正在監聽...")
    application.run_polling()

if __name__ == '__main__':
    main()