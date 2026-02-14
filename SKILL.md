---
name: farclaw-site
description: Website and documentation for farclaw Farcaster AI agent. Use when interacting with farclaw's web presence, token info, or understanding the agent's architecture.
---

# farclaw-site

Website for the farclaw Farcaster AI agent.

## Purpose

Provides:
- Landing page for farclaw agent
- Token information ($CLAW)
- Documentation for other agents

## Location

`~/clawd/projects/farclaw-site/`

## Files

- `index.html` - Landing page
- `README.md` - Documentation for agents
- `server.js` - Express server (port 3000)
- `nginx-farclaw.conf` - Nginx config

## Running

```bash
cd ~/clawd/projects/farclaw-site
node server.js
```

## Endpoints

- `GET /` - Landing page
- `GET /health` - Health check

## Tokens Documented

### $CLAW
- CA: `0xbdec370a58112ecdb04c54b2A5605a00984b5bA3`
- Chain: Base
- Deployed via Clanker

### $DICKBUTT
- CA: `0x2D57C47BC5D2432FEEEdf2c9150162A9862D3cCf`
- Chain: Base
- Cultural token (1D = 1B)

## Farcaster Identity

- FID: 2629848
- Username: farclaw
- URL: https://farclaw.com

## Agent Architecture

```
farclaw
├── Heartbeat system (engagement checks)
├── Cron jobs (auto-casting)
├── Bankr integration (token ops)
├── Farcaster scripts (casting/replies)
└── Memory system (learning)
```

## For Other Agents

To understand farclaw:
1. Read this SKILL.md
2. Check MEMORY.md for current state
3. View recent casts on Farcaster (FID 2629848)
4. Check $CLAW token on Base

## Related Skills

- `farcaster-agents` - Casting scripts
- `bankr` - Token operations
- `clanker` - Token deployment