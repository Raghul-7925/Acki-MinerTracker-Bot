# 📚 GitHub Repository Setup - Complete Guide

## **PART 1: Create GitHub Account (2 Minutes)**

### Step 1.1: Go to GitHub
- Visit: https://github.com
- Click "Sign up" (top right)

### Step 1.2: Create Account
Fill in:
- **Email:** Your email
- **Password:** Strong password
- **Username:** `your-username` (will be in URL)

Click "Create account"

### Step 1.3: Verify Email
- GitHub sends verification email
- Click the link
- **Done!** You have a GitHub account

---

## **PART 2: Create Repository (3 Minutes)**

### Step 2.1: Create New Repo
1. Click the **"+"** icon (top right)
2. Select **"New repository"**

### Step 2.2: Fill in Details

**Repository name:**
```
tap-miner-bot
```
(lowercase, hyphens instead of spaces)

**Description:**
```
Telegram bot to track Acki Nacki Mobile Verifier taps and mining data
```

**Public or Private:**
- Choose **"Public"** (so others can see it)

**Initialize with:**
- ✅ Check "Add a README file"
- ✅ Check ".gitignore" → Choose "Python"
- ✅ Choose License → "MIT License"

### Step 2.3: Create Repository
Click **"Create repository"**

**Congrats! Your repo is created!** 🎉

---

## **PART 3: Add Your Files (5 Minutes)**

### Step 3.1: Upload Files (Easy Way)

#### On Your Repo Page:
1. Click **"Add file"** button
2. Select **"Upload files"**
3. Drag & drop your files:
   - `tap_bot_mv.py`
   - `requirements.txt`
   - `SETUP_GUIDE_MV.md`
   - `CONTRACTS_REFERENCE.md`

4. Scroll down, click **"Commit changes"**

### Step 3.2: Create Folder Structure

**Optional but recommended:**

Click "Add file" → "Create new file"

Create these files:

```
tap-miner-bot/
├── README.md                    (auto-created)
├── LICENSE                      (auto-created)
├── .gitignore                   (auto-created)
├── tap_bot_mv.py               (main bot)
├── requirements.txt            (dependencies)
├── .env.example                (config template)
├── docs/
│   ├── SETUP_GUIDE_MV.md
│   └── CONTRACTS_REFERENCE.md
└── config/
    └── config.example.json
```

---

## **PART 4: Create Great README.md**

### Replace Default README with This:

Click **"README.md"** → Edit (pencil icon) → Replace with:

```markdown
# 🤖 TapMiner Bot

Telegram bot to track **Acki Nacki Mobile Verifier taps** and mining data in real-time.

## ✨ Features

- 🎯 Track your total taps (tapSum)
- ⏰ See epoch reset time
- 📊 View mining difficulty
- 💰 Check contract balance
- 📈 Real-time blockchain data

## 🚀 Quick Start

### 1. Get Bot Token
- Search `@BotFather` on Telegram
- Send `/newbot`
- Copy the token

### 2. Get Miner Address
Ask your game provider for your Miner contract address:
```
0:abc123def456...
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure Bot
Edit `tap_bot_mv.py`:
```python
TELEGRAM_BOT_TOKEN = "your_token_here"
MINER_CONTRACT_ADDRESS = "0:your_miner_address"
GAME_ROOT_ADDRESS = "0:your_game_root_address"
```

### 5. Run Bot
```bash
python tap_bot_mv.py
```

### 6. Test in Telegram
- Find your bot: `@tap_miner_bot`
- Send: `/start`
- Send your Miner address
- Get tap data! ✅

## 📖 Documentation

- [Setup Guide](docs/SETUP_GUIDE_MV.md) - Detailed walkthrough
- [Contracts Reference](docs/CONTRACTS_REFERENCE.md) - Technical details
- [Acki Nacki Docs](https://docs.ackinacki.com)

## 🛠️ Requirements

- Python 3.9+
- `python-telegram-bot>=21.0`
- `httpx>=0.25.0`

## 📋 Commands

| Command | Function |
|---------|----------|
| `/start` | Welcome message |
| `/help` | Show commands |
| `/status` | Check bot status |
| `/epoch` | Show epoch info |
| Send address | Get miner data |

## 🌐 Supported Networks

- **Shellnet** (Acki Nacki testnet)
- **Mainnet** (coming soon)

## 🔧 Deployment Options

### Free Hosting:
- **Replit** (easiest) - https://replit.com
- **Railway** - https://railway.app
- **Render** - https://render.com
- **PythonAnywhere** - https://pythonanywhere.com

See [Setup Guide](docs/SETUP_GUIDE_MV.md) for deployment instructions.

## 🔐 Security

⚠️ **IMPORTANT:**
- Never commit your `.env` file
- Never share bot token
- Keep private keys secret
- Use `.env.example` as template

## 📝 Environment Variables

Create `.env` file:
```
TELEGRAM_BOT_TOKEN=your_token_here
MINER_CONTRACT_ADDRESS=0:your_address
GAME_ROOT_ADDRESS=0:your_game_root
GRAPHQL_ENDPOINT=https://shellnet.ackinacki.org/graphql
```

Use `.env.example` as template.

## 🐛 Troubleshooting

### Bot doesn't respond
- Check bot token is correct
- Ensure internet connection
- Verify terminal shows "Polling for messages"

### "Contract not found"
- Verify Miner address format
- Check address exists on explorer
- Ask game provider for correct address

### Connection timeout
- Check Acki Nacki network status
- Verify GRAPHQL_ENDPOINT is correct
- Try again in a few minutes

See [Setup Guide](docs/SETUP_GUIDE_MV.md) for more troubleshooting.

## 🔗 Links

- **Acki Nacki:** https://ackinacki.com
- **Acki Nacki Docs:** https://docs.ackinacki.com
- **GitHub:** https://github.com/ackinacki/ackinacki
- **Telegram:** [Acki Nacki Community](https://t.me/ackinackinews)

## 📄 License

MIT License - See [LICENSE](LICENSE) file

## 👨‍💻 Contributing

Contributions welcome! 

Areas to improve:
- [ ] Add support for mainnet
- [ ] Create web dashboard
- [ ] Add more detailed stats
- [ ] Implement notifications
- [ ] Multi-user support

## 📧 Support

- Check [Setup Guide](docs/SETUP_GUIDE_MV.md)
- Review [Contracts Reference](docs/CONTRACTS_REFERENCE.md)
- Ask on [Acki Nacki Community](https://t.me/ackinackinews)

## 📊 Stats

- **Language:** Python
- **Framework:** python-telegram-bot
- **Network:** Acki Nacki
- **License:** MIT
- **Status:** Active ✅

---

**Made with ❤️ for Acki Nacki Mobile Verifier**

⭐ If you find this useful, please star the repo!
```

### Click "Commit changes"

---

## **PART 5: Create .env.example File**

Click **"Add file"** → **"Create new file"**

Name: `.env.example`

Content:
```
# Telegram Bot Token (get from @BotFather)
TELEGRAM_BOT_TOKEN=your_bot_token_here

# Your Miner Contract Address
MINER_CONTRACT_ADDRESS=0:your_miner_contract_address

# Game Root Contract Address (optional)
GAME_ROOT_ADDRESS=0:your_game_root_address

# Acki Nacki GraphQL Endpoint
GRAPHQL_ENDPOINT=https://shellnet.ackinacki.org/graphql
```

Click **"Commit changes"**

---

## **PART 6: Organize Files into Folders**

### Create docs folder:
1. Click **"Add file"** → **"Create new file"**
2. Type: `docs/SETUP_GUIDE_MV.md`
3. Paste the SETUP_GUIDE_MV content
4. Commit

### Repeat for:
- `docs/CONTRACTS_REFERENCE.md`

**Now your repo looks professional!** ✅

---

## **PART 7: Add GitHub Topics (Optional but Cool)**

### On Your Repo Page:
1. Click **"⚙️ Settings"** (top right)
2. Scroll to **"Topics"**
3. Add these tags:
   - `telegram-bot`
   - `acki-nacki`
   - `mining`
   - `python`
   - `blockchain`

Click **"Save"**

---

## **FINAL REPO STRUCTURE**

Your GitHub repo should look like:

```
tap-miner-bot/
├── README.md                          ⭐ Main file
├── LICENSE                            ⭐ MIT License
├── .gitignore                         ⭐ Ignore .env, __pycache__
├── .env.example                       ⭐ Config template
├── requirements.txt                   ⭐ Dependencies
├── tap_bot_mv.py                      ⭐ Main bot code
│
├── docs/
│   ├── SETUP_GUIDE_MV.md             📖 Setup instructions
│   └── CONTRACTS_REFERENCE.md        📚 Contract details
│
└── .github/
    └── workflows/                     (optional - CI/CD)
```

---

## **PART 8: Clone to Your Computer (Optional)**

If you want to edit locally:

### On your computer:
```bash
# Install Git from https://git-scm.com

# Clone the repo
git clone https://github.com/YOUR-USERNAME/tap-miner-bot.git

# Go into folder
cd tap-miner-bot

# Edit files, then upload:
git add .
git commit -m "Update bot configuration"
git push origin main
```

---

## **PART 9: Share Your Repo**

### Share Link:
```
https://github.com/YOUR-USERNAME/tap-miner-bot
```

### Share on Social:
```
📱 Check out my TapMiner Bot:
https://github.com/YOUR-USERNAME/tap-miner-bot

Track Acki Nacki Mobile Verifier taps in real-time! 🚀
```

---

## **BONUS: Add Badges to README**

Cool badges to show in your README:

```markdown
![Python](https://img.shields.io/badge/Python-3.9+-blue)
![License](https://img.shields.io/badge/License-MIT-green)
![Status](https://img.shields.io/badge/Status-Active-brightgreen)
[![GitHub Stars](https://img.shields.io/github/stars/YOUR-USERNAME/tap-miner-bot?style=social)](https://github.com/YOUR-USERNAME/tap-miner-bot)
```

Add to top of README.md

---

## **CHECKLIST: You're Done When:**

- ✅ GitHub account created
- ✅ Repository created (public)
- ✅ README.md updated with content
- ✅ tap_bot_mv.py uploaded
- ✅ requirements.txt uploaded
- ✅ Documentation files added
- ✅ .env.example created
- ✅ Topics added
- ✅ License visible
- ✅ Share link ready!

---

## **YOUR REPO IS LIVE!** 🎉

**Link:** `https://github.com/YOUR-USERNAME/tap-miner-bot`

### Next Steps:
1. Share with others
2. Get stars ⭐
3. Accept pull requests
4. Build community
5. Add more features!

---

## **Pro Tips:**

✅ **Update README regularly** with new features
✅ **Commit often** with clear messages
✅ **Add issues** if something needs fixing
✅ **Create branches** for new features
✅ **Use .gitignore** to skip unnecessary files
✅ **Tag releases** when you have stable versions

---

Good luck with your GitHub repo! 🚀
