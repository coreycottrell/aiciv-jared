#!/bin/bash
# Send a message to Aether without attaching
# Usage: ./msg_aether.sh "your message here"

if [ -z "$1" ]; then
    echo "Usage: ./msg_aether.sh 'your message'"
    exit 1
fi

tmux send-keys -t user-jared-onboard "$1"
for i in 1 2 3 4 5; do
    sleep 0.5
    tmux send-keys -t user-jared-onboard Enter
done
echo "Message sent to Aether"
