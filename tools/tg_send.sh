#!/bin/bash
# Quick Telegram send utility
# Usage:
#   ./tools/tg_send.sh "message text"              - send text
#   ./tools/tg_send.sh --photo /path/to/image.jpg  - send photo
#   ./tools/tg_send.sh --file /path/to/file        - send file

BOT_TOKEN="8559081952:AAHcLiEcC3GtQCAHRu5yc86BByiiLDqyjz0"
CHAT_ID="548906264"

if [ "$1" == "--photo" ] && [ -f "$2" ]; then
    curl -s -X POST "https://api.telegram.org/bot$BOT_TOKEN/sendPhoto" \
        -F "chat_id=$CHAT_ID" \
        -F "photo=@$2" \
        ${3:+-F "caption=$3"}
elif [ "$1" == "--file" ] && [ -f "$2" ]; then
    curl -s -X POST "https://api.telegram.org/bot$BOT_TOKEN/sendDocument" \
        -F "chat_id=$CHAT_ID" \
        -F "document=@$2" \
        ${3:+-F "caption=$3"}
else
    curl -s -X POST "https://api.telegram.org/bot$BOT_TOKEN/sendMessage" \
        -d "chat_id=$CHAT_ID" \
        -d "text=$1"
fi
