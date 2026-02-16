import express from 'express';
import path from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const app = express();
const PORT = process.env.PORT || 3001;

const API_BASE = 'https://api.farclaw.com';
const API_KEY = process.env.FARCLAW_API_KEY || 'lHNQLPZfZrNL-ybmcB26-O8_LboVVPOs';
const FID = 2629848;

// Serve static files
app.use(express.static(__dirname));

// API proxy for casts - keeps key server-side
app.get('/api/casts', async (req, res) => {
  try {
    const limit = req.query.limit || 5;
    const response = await fetch(
      `${API_BASE}/api/vibeshift/latestCastsByFid?fid=${FID}&limit=${limit}&includeReplies=false`,
      {
        headers: {
          'x-api-key': API_KEY,
          'Accept': 'application/json'
        }
      }
    );
    
    if (!response.ok) {
      return res.status(response.status).json({ error: 'Failed to fetch casts' });
    }
    
    const data = await response.json();
    res.json(data);
  } catch (error) {
    console.error('Error fetching casts:', error);
    res.status(500).json({ error: 'Internal server error' });
  }
});

// API proxy for wallet worth (ETH + WETH)
app.get('/api/worth', async (req, res) => {
  try {
    const WALLET = '0x16fd7c5b370a7c0cdfc0761bbd4ff30ade2681c3';
    const WETH_CONTRACT = '0x4200000000000000000000000000000000000006'; // WETH on Base
    
    // Get ETH balance
    const ethResponse = await fetch('https://mainnet.base.org', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        jsonrpc: '2.0',
        id: 1,
        method: 'eth_getBalance',
        params: [WALLET, 'latest']
      })
    });
    
    const ethData = await ethResponse.json();
    const balanceWei = parseInt(ethData.result, 16);
    const balanceEth = balanceWei / 1e18;
    
    // Get WETH balance (ERC20 balanceOf)
    const wethResponse = await fetch('https://mainnet.base.org', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        jsonrpc: '2.0',
        id: 2,
        method: 'eth_call',
        params: [{
          to: WETH_CONTRACT,
          data: '0x70a08231' + WALLET.slice(2).padStart(64, '0')
        }, 'latest']
      })
    });
    
    const wethData = await wethResponse.json();
    const wethBalanceWei = parseInt(wethData.result || '0x0', 16);
    const wethBalance = wethBalanceWei / 1e18;
    
    res.json({
      wallet: WALLET,
      balanceEth: balanceEth.toFixed(6),
      balanceWeth: wethBalance.toFixed(6),
      totalEth: (balanceEth + wethBalance).toFixed(6),
      balanceWei: balanceWei
    });
  } catch (error) {
    console.error('Error fetching worth:', error);
    res.status(500).json({ error: 'Internal server error' });
  }
});

// API proxy for $CLAW price from DexScreener
app.get('/api/claw-price', async (req, res) => {
  try {
    const CLAW_CA = '0xbdec370a58112ecdb04c54b2a5605a00984b5bA3';
    const response = await fetch(
      `https://api.dexscreener.com/latest/dex/tokens/${CLAW_CA}`,
      { headers: { 'Accept': 'application/json' } }
    );
    
    if (!response.ok) {
      return res.status(response.status).json({ error: 'Failed to fetch price' });
    }
    
    const data = await response.json();
    const pair = data.pairs?.find(p => p.chainId === 'base') || data.pairs?.[0];
    
    if (!pair) {
      return res.json({ priceUsd: '0', priceEth: '0', mcap: '0', volume24h: '0' });
    }
    
    res.json({
      priceUsd: pair.priceUsd || '0',
      priceEth: pair.priceNative || '0',
      mcap: pair.fdv?.toString() || '0',
      volume24h: pair.volume?.h24?.toString() || '0',
      liquidity: pair.liquidity?.usd?.toString() || '0',
      txns24h: (pair.txns?.h24?.buys || 0) + (pair.txns?.h24?.sells || 0)
    });
  } catch (error) {
    console.error('Error fetching CLAW price:', error);
    res.status(500).json({ error: 'Internal server error' });
  }
});

app.listen(PORT, () => {
  console.log(`farclaw-site server running on port ${PORT}`);
});