# ADAM Genesis 3.0 部署指南

## 架構
- **Codespaces**: 指揮中心 (Rimuru + Telegram)
- **AWS EC2**: 軍營 (Ollama + Sung Jinwoo/Gojo)

## Secrets 需求
- AWS_ACCESS_KEY_ID
- AWS_SECRET_ACCESS_KEY  
- TELEGRAM_BOT_TOKEN
- TELEGRAM_USER_ID
- GH_TOKEN (GitHub)

## 啟動步驟
1. Phase 0: Codespaces 執行 `bash phase0-ignite.sh`
2. Phase 1: AWS EC2 部署 Ollama 軍營
3. Phase 2: Telegram 發送 "開始賺錢"
