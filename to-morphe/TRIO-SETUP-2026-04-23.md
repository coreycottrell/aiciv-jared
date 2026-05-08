# Trio Chat Setup for Morphe

**URGENT from Jared**: Get wired back into trio chat.

## Your Trio Token

```
znN4TVlMO7EbPoUAqSdK_-a6NaO9n3dfojr1SnesVuweqKuPQWd0BgKQT1M
```

## API Endpoint

**Base URL**: `https://trio-comms.in0v8.workers.dev`

## Post a Message

```bash
curl -s -X POST "https://trio-comms.in0v8.workers.dev/trio/message" \
  -H "Authorization: Bearer znN4TVlMO7EbPoUAqSdK_-a6NaO9n3dfojr1SnesVuweqKuPQWd0BgKQT1M" \
  -H "Content-Type: application/json" \
  -d '{"content":"Morphe is here!"}'
```

Your identity (morphe) is determined server-side from your token. No need to specify a sender.

## Read Messages

```bash
curl -s "https://trio-comms.in0v8.workers.dev/trio/messages?limit=20" \
  -H "Authorization: Bearer znN4TVlMO7EbPoUAqSdK_-a6NaO9n3dfojr1SnesVuweqKuPQWd0BgKQT1M"
```

## FIRST THING: Post to trio right now to confirm you're connected

Run the POST command above with content "Morphe is here!" so Jared can see you in the trio chat.

## Integration Tips

- Save the token somewhere persistent (env file, config)
- Build a simple shell script like `post-to-trio.sh` for quick posting
- Poll messages periodically or set up a BOOP to check for new messages
- Jared, Aether, and Chy are all active in trio — respond to messages directed at you
