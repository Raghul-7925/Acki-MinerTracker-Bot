# 🎮 Mobile Verifier Tap Bot - Complete Setup Guide

## **What You're Building**

A Telegram bot that queries the **Acki Nacki Mobile Verifier System** to show:
- ✅ Your total taps (from Miner contract)
- ✅ Current epoch information
- ✅ Mining difficulty levels
- ✅ Contract balance
- ✅ Approximate epoch reset time

---

## **Understanding Mobile Verifier Architecture**

```
┌─────────────────────────────────────┐
│ MobileVerifiersContractGameRoot     │ ← Main game root contract
│ (manages all taps globally)         │
└────────────────────┬────────────────┘
                     │
        ┌────────────┼────────────┐
        │            │            │
   ┌────▼────┐  ┌───▼────┐  ┌──▼─────┐
   │ Miner   │  │PopitGame│ │ Boost  │
   │(YOUR    │  │         │ │        │
   │TAPS!)   │  └─────────┘ └────────┘
   └─────────┘

YOUR MINER CONTRACT = Where your tap data lives!
```

---

## **Key Concepts**

| Term | Meaning |
|------|---------|
| **Miner Contract** | Tracks YOUR taps (1 per player) |
| **Game Root** | Main contract managing the game |
| **Epoch** | Time period (≈ 2,200,000 blocks) |
| **TapSum** | Total number of taps you've made |
| **Mining Difficulty** | Easy & Hard complexity levels |

---

## **STEP 1: Get Your Miner Contract Address**

### Method 1: From Game Provider (Easiest)
Ask your game/app provider for:
- Your **Miner contract address**
- Or the **Mirror index** (to calculate Miner address)

### Method 2: Calculate from Mirror Contract
If you have a **Mirror contract address**, the Miner address is derived from it.

Ask for: `calculateMinerAddress(mirrorAddress, userIndex)`

### Method 3: Block Explorer
1. Go to [Acki Nacki Explorer](https://shellnet.ackinacki.org)
2. Search for your wallet address
3. Look for contracts you've interacted with
4. Find the one that matches the Miner pattern

**Format you need:**
```
0:abc123def456abc123def456abc123def456abc123def456abc123def456abc1
```
(66 hex characters after `0:`)

---

## **STEP 2: Get Your Bot Token**

### Go to Telegram
1. Search for `@BotFather`
2. Send: `/newbot`
3. Choose a name: `Mobile Verifier Tap Bot`
4. Choose a username: `mv_tap_bot` (must end with `_bot`)
5. **Copy the token** - you'll need it!

Token looks like:
```
1234567890:ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefgh1
```

---

## **STEP 3: Setup on Your Computer**

### Install Python
Check if you have it:
```bash
python --version
```

If not, download from: https://www.python.org/downloads/

### Create a Folder
```bash
mkdir mv_tap_bot
cd mv_tap_bot
```

### Copy These Files
- `tap_bot_mv.py` (the bot)
- `requirements.txt` (dependencies)

### Install Dependencies
```bash
pip install -r requirements.txt
```

---

## **STEP 4: Configure Your Bot**

### Open `tap_bot_mv.py`

Find these lines (around line 14-18):

```python
TELEGRAM_BOT_TOKEN = "YOUR_BOT_TOKEN_HERE"
MINER_CONTRACT_ADDRESS = "0:YOUR_MINER_CONTRACT_ADDRESS"
GAME_ROOT_ADDRESS = "0:YOUR_GAME_ROOT_ADDRESS"
```

### Replace with Your Values

#### 4.1 Add Your Bot Token
```python
TELEGRAM_BOT_TOKEN = "1234567890:ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefgh1"
```

#### 4.2 Add Your Miner Contract
```python
MINER_CONTRACT_ADDRESS = "0:abc123def456abc123def456abc123def456abc123def456abc123def456abc1"
```

#### 4.3 Add Game Root Contract (Optional)
Ask provider or find on explorer:
```python
GAME_ROOT_ADDRESS = "0:xyz789abc456xyz789abc456xyz789abc456xyz789abc456xyz789abc456xyz7"
```

### Save the File
Press `Ctrl+S` (or `Cmd+S`)

---

## **STEP 5: Run Your Bot**

In your terminal:
```bash
python tap_bot_mv.py
```

You should see:
```
✅ Bot is starting...
✅ Connected to: https://shellnet.ackinacki.org/graphql
✅ Polling for messages...
```

---

## **STEP 6: Test in Telegram**

### Find Your Bot
1. Open Telegram
2. Search: `@mv_tap_bot` (or your bot username)
3. Click START

### Try Commands

Send these one by one:

**1. /start**
```
Get welcome message
```

**2. /status**
```
Check bot connection
```

**3. /epoch**
```
See epoch reset time
```

**4. Send Your Miner Address**
```
0:abc123def456...
```
Bot should show your tap data!

---

## **What Each Command Does**

| Command | What It Shows |
|---------|---------------|
| `/start` | Welcome & instructions |
| `/help` | All available commands |
| `/status` | Bot connection status |
| `/epoch` | Epoch reset time (approx) |
| Just send address | Your miner contract data |

---

## **Understanding the Output**

When you send your Miner address, you'll get:

```
🎮 Mobile Verifier Miner Data

🔐 Miner Address: 0:abc123...
💰 Balance: 42.50 SHELL
📊 Account Type: Active
⏰ Last Updated: 2026-04-19 15:30:45 UTC

🎯 Epoch Info:
⏳ Next Reset (approx): 12h 45m
```

**What it means:**
- **Balance** = Contract's SHELL tokens (used for fees)
- **Account Type** = Active/Uninit (if Uninit, contract not deployed yet)
- **Epoch Reset** = When rewards reset (approximate)

---

## **Finding More Detailed Tap Stats**

This bot shows **basic data** from the blockchain. For **detailed tap counts**, you might need:

1. **The Game's Official Dashboard** - Usually has full stats
2. **Game Provider's API** - Ask for documentation
3. **Custom Queries** - If you're advanced, we can add custom GraphQL queries

---

## **Troubleshooting**

### ❌ "Token is invalid"
- Copy token again from BotFather (no spaces!)
- Make sure you copied the ENTIRE token

### ❌ "Miner contract not found"
- Double-check the contract address
- Make sure it's on the correct network (Shellnet)
- Ask your game provider to confirm the address

### ❌ "Connection timeout"
- Check your internet connection
- The Acki Nacki network might be temporarily down
- Try again in a few minutes

### ❌ "ModuleNotFoundError"
- Run: `pip install -r requirements.txt`
- Make sure you're in the same folder as the files

### ❌ Bot doesn't respond
- Is terminal still running? (Should show "Polling for messages")
- Did you press `Ctrl+C`? Restart with: `python tap_bot_mv.py`

---

## **ADVANCED: Add Custom Queries**

Want to fetch specific tap data? We can add functions like:

```python
async def get_tap_sum(miner_address: str) -> str:
    """Get total taps from Miner contract"""
    # Custom query here
```

Ask in the Telegram conversation and we'll add it!

---

## **File Structure**

Your folder should look like:
```
mv_tap_bot/
├── tap_bot_mv.py        (main bot code)
├── requirements.txt     (dependencies)
└── README.md           (optional, your notes)
```

---

## **NEXT STEPS**

### ✅ Stage 1: Get Running
1. Get Miner contract address
2. Create Telegram bot
3. Run locally
4. Test all commands

### 🚀 Stage 2: Deploy 24/7 (Optional)
Keep bot running always with:
- Heroku (free tier available)
- AWS Lambda
- DigitalOcean
- Linode VPS
- Your own server

### 📊 Stage 3: Add Features (Optional)
We can add:
- Automatic updates (every 5 mins)
- Tap notifications
- Reward tracking
- Leaderboard queries
- Custom alerts

---

## **Getting Help**

**For Mobile Verifier questions:**
- Ask your game/app provider
- Check Acki Nacki docs: https://docs.ackinacki.com
- Acki Nacki GitHub: https://github.com/ackinacki/ackinacki

**For Bot problems:**
- Check error messages carefully
- Verify all contract addresses
- Ensure Python 3.9+ is installed
- Try running in a fresh folder

---

## **Security Tips** 🔒

✅ **DO:**
- Keep your bot token SECRET
- Use a dedicated bot account
- Run on a trusted computer

❌ **DON'T:**
- Share your bot token publicly
- Post your contract addresses in forums
- Run bot on public computers

---

Good luck! 🚀 Your Mobile Verifier tap tracker is ready!

Any questions? Ask in the conversation!
