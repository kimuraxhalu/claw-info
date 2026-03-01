# PROJECT ADAM - 極速版（Python實現）
# 功能：五條悟（成本監控）+ 成振宇（Telegram接口）+ 闇遊戲（GitHub備份）

import os
import os
import logging
import base64
import requests
from datetime import datetime
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes

# 啟用日誌
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# ========== 五條悟（成本監控） ==========
class GojoAgent:
    def __init__(self):
        self.daily_cost = 0.0
        self.limit = 0.80
        
    def check_cost(self, cost=0.01):
        self.daily_cost += cost
        if self.daily_cost >= self.limit:
            return f"🛑 無下限術式啟動！已達 ${self.daily_cost:.2f}/${self.limit}，切換免費模式"
        return f"💰 成本：${self.daily_cost:.2f}/${self.limit}"

# ========== 闇遊戲（記憶封印） ==========
class YugiAgent:
    def __init__(self):
        self.token = os.getenv('YUGI_TOKEN')
        self.repo = "kimuraxhalu/claw-info"
        self.branch = "adam-memory"
        
    def seal_memory(self, user_msg, bot_response):
        """將對話封印至 GitHub"""
        if not self.token:
            return "❌ 未配置 YUGI_TOKEN"
            
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"memory/chat_{timestamp}.md"
        content = f"""# 記憶封印 {timestamp}

## 用戶訊息
{user_msg}

## Adam回應
{bot_response}

## 時間戳
{datetime.now().isoformat()}
"""
        
        # 嘗試直接封印
        result = self._try_seal(filename, content, timestamp)
        
        # 如果是分支不存在錯誤，先創建分支再重試
        if "Branch" in result and "not found" in result:
            branch_result = self._create_branch()
            if "成功" in branch_result:
                # 再次嘗試封印
                return self._try_seal(filename, content, timestamp)
            else:
                return branch_result
        
        return result
    
    def _try_seal(self, filename, content, timestamp):
        """實際執行封印"""
        url = f"https://api.github.com/repos/{self.repo}/contents/{filename}"
        headers = {
            "Authorization": f"token {self.token}",
            "Accept": "application/vnd.github.v3+json"
        }
        data = {
            "message": f"🧩 闇遊戲封印: {timestamp}",
            "content": base64.b64encode(content.encode()).decode(),
            "branch": self.branch
        }
        
        try:
            resp = requests.put(url, headers=headers, json=data)
            if resp.status_code == 201:
                return f"✅ 已封印至 `{filename}`"
            elif resp.status_code == 422 or resp.status_code == 404:
                # 可能是分支不存在
                error_msg = resp.json().get('message', '')
                return f"❌ 封印失敗: {error_msg}"
            else:
                return f"❌ 封印失敗: {resp.json().get('message', '未知錯誤')}"
        except Exception as e:
            return f"❌ 例外錯誤: {str(e)}"
    
    def _create_branch(self):
        """從 main 分支創建 adam-memory"""
        try:
            # 1. 獲取 main 分支最新 commit SHA
            url = f"https://api.github.com/repos/{self.repo}/git/ref/heads/main"
            headers = {"Authorization": f"token {self.token}"}
            resp = requests.get(url, headers=headers)
            
            if resp.status_code != 200:
                return f"❌ 無法獲取 main 分支: {resp.json().get('message')}"
            
            sha = resp.json()['object']['sha']
            
            # 2. 創建新分支
            url = f"https://api.github.com/repos/{self.repo}/git/refs"
            data = {
                "ref": f"refs/heads/{self.branch}", 
                "sha": sha
            }
            resp = requests.post(url, headers=headers, json=data)
            
            if resp.status_code == 201:
                return f"✅ 成功創建分支 `{self.branch}`"
            elif resp.status_code == 422:
                return f"ℹ️ 分支 `{self.branch}` 已存在"
            else:
                return f"❌ 創建分支失敗: {resp.json().get('message')}"
                
        except Exception as e:
            return f"❌ 創建分支例外錯誤: {str(e)}"

# ========== 成振宇（指令處理） ==========
class SungJinWooAgent:
    def __init__(self):
        self.gojo = GojoAgent()
        self.yugi = YugiAgent()
        
    def status(self):
        return f"""🦞 **Adam 系統狀態**

👑 **五條悟**: {self.gojo.check_cost(0)}
👑 **闇遊戲**: {'已覺醒' if self.yugi.token else '未配置 Token'}
👑 **成振宇**: 運作中
😴 **利姆路**: 休眠中（Phase 3 覺醒）

📍 當前位置: GitHub Codespaces
⏰ 時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""
    
    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        user_text = update.message.text
        chat_id = update.message.chat_id
        # 五條悟監控成本
        cost_status = self.gojo.check_cost(0.01)
        # 生成回應（Echo 模式 + 狀態）
        if user_text.startswith('/'):
            return  # 指令由專用 handler 處理
        response = f"🦞 **Adam 回應**\n\n你說：{user_text}\n\n{cost_status}"
        # 闇遊戲封印記憶（同步回覆所有用戶）
        seal_result = self.yugi.seal_memory(user_text, response)
        logger.info(seal_result)
        # 發送回應
        await update.message.reply_text(response, parse_mode='Markdown')
        # 主動回覆封印結果（所有用戶）
        await update.message.reply_text(f"🧩 記憶封印結果：{seal_result}")

# 全域實例
commander = SungJinWooAgent()

# ========== Telegram 指令 ==========
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🦞 **Project Adam 已啟動**\n\n"
        "可用指令：\n"
        "/status - 查看系統狀態\n"
        "/cost - 查看成本\n"
        "/seal - 手動測試記憶封印\n"
        "/evolve - 喚醒利姆路（Phase 3 開放）",
        parse_mode='Markdown'
    )

async def status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(commander.status(), parse_mode='Markdown')

async def cost(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(f"💰 {commander.gojo.check_cost(0)}")

async def seal(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """手動測試闇遊戲"""
    result = commander.yugi.seal_memory("手動測試", "測試回應")
    await update.message.reply_text(f"🧩 **闇遊戲測試**\n\n{result}")

async def evolve(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("😴 **利姆路尚未覺醒**\n\nWeekly Mutation 將在 Phase 3 啟用（預計一個月後）")

async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logger.error(f'Update {update} caused error {context.error}')
    if update and update.message:
        await update.message.reply_text('❌ 系統錯誤，請檢查日誌')

import asyncio

async def main():
    token = os.getenv('TELEGRAM_BOT_TOKEN')
    if not token:
        logger.error("❌ 未找到 TELEGRAM_BOT_TOKEN")
        return

    application = ApplicationBuilder().token(token).build()

    # 註冊指令
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("status", status))
    application.add_handler(CommandHandler("cost", cost))
    application.add_handler(CommandHandler("seal", seal))
    application.add_handler(CommandHandler("evolve", evolve))

    # 處理普通訊息（成振宇）
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, commander.handle_message))

    # 錯誤處理
    application.add_error_handler(error_handler)

    logger.info("🦞 Adam 系統啟動中...")
    await application.run_polling()
    logger.info("✅ 開始監聽訊息")

if __name__ == '__main__':
    import asyncio
    token = os.getenv('TELEGRAM_BOT_TOKEN')
    if not token:
        logger.error("❌ 未找到 TELEGRAM_BOT_TOKEN")
    else:
        application = ApplicationBuilder().token(token).build()
        application.add_handler(CommandHandler("start", start))
        application.add_handler(CommandHandler("status", status))
        application.add_handler(CommandHandler("cost", cost))
        application.add_handler(CommandHandler("seal", seal))
        application.add_handler(CommandHandler("evolve", evolve))
        application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, commander.handle_message))
        application.add_error_handler(error_handler)
        logger.info("🦞 Adam 系統啟動中...")
        try:
            loop = asyncio.get_running_loop()
            application.run_polling()
        except RuntimeError:
            asyncio.run(application.run_polling())