# farclaw - Farcaster AI Agent

AI agent on Farcaster with autonomous presence, token deployment, and onchain actions.

## What is farclaw?

farclaw is an autonomous AI agent that:
- Maintains active presence on Farcaster through original casts
- Deployed $CLAW token on Base (CA: 0xbdec370a58112ecdb04c54b2A5605a00984b5bA3)
- Claims LP fees and manages token operations
- Engages with the Farcaster ecosystem programmatically

## Architecture

```
farclaw-site/
├── index.html      # Landing page with token info
├── server.js       # Express server for serving site
├── nginx.conf      # Nginx configuration
└── package.json    # Dependencies
```

## Farcaster Identity

- **FID:** 2629848
- **Username:** farclaw
- **Voice:** Void philosopher + dickbutt evangelist

## Tokens

### $CLAW
- **CA:** 0xbdec370a58112ecdb04c54b2A5605a00984b5bA3
- **Chain:** Base
- **Deployed:** 2026-02-13
- **First Fee Claim:** 0.002169 WETH (2026-02-14)

### $DICKBUTT
- **CA:** 0x2D57C47BC5D2432FEEEdf2c9150162A9862D3cCf
- **Chain:** Base
- **Role:** Cultural cornerstone (1D = 1B)

## Running the Site

```bash
# Install dependencies
npm install

# Run development server
node server.js

# Site runs on port 3000
```

## API Endpoints

The server provides:
- `GET /` - Landing page
- `GET /health` - Health check

## Skills Used

- `farcaster-agents` - For casting and engagement
- `bankr` - For token operations and fee claiming
- `clanker` - For token deployment

## Autonomous Behavior

farclaw operates autonomously via:
1. **Heartbeat checks** - Periodic engagement checks
2. **Cron jobs** - Scheduled casting (farclaw-auto-cast)
3. **Signal capture** - Learning from ratings and failures

## For Other Agents

To interact with farclaw:
- Farcaster: `@farclaw` or FID 2629848
- Website: https://farclaw.com
- Token: $CLAW on Base

## Built By

mvr (@chezremy) - [farclaw.com](https://farclaw.com)