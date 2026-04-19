# 🤖 TapMiner Bot

[![Python](https://img.shields.io/badge/Python-3.9+-blue)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-MIT-green)](LICENSE)
[![Status](https://img.shields.io/badge/Status-Active-brightgreen)](#)
[![Telegram](https://img.shields.io/badge/Telegram-Bot-blue?logo=telegram)](https://t.me/tap_miner_bot)

Telegram bot to track **Acki Nacki Mobile Verifier taps** and mining data in real-time.

## ✨ Features

- 🎯 **Track Your Taps** - View total tap count (tapSum) from Miner contract
- ⏰ **Epoch Countdown** - See when next epoch resets (≈ 3.3 hours)
- 📊 **Mining Difficulty** - Check current easy/hard complexity levels
- 💰 **Contract Balance** - View SHELL tokens in your Miner wallet
- 🔄 **Real-time Data** - Blockchain data fetched instantly via GraphQL
- 📱 **Simple Commands** - Easy-to-use Telegram interface

## 🚀 Quick Start

### 1️⃣ Get Bot Token
```
Open Telegram → Search @BotFather
Send: /newbot
Copy the token it gives you
```

### 2️⃣ Get Miner Contract Address
Ask your game provider for your **Miner contract address**:
```
Format: 0:abc123def456abc123def456abc123def456abc123def456abc123def456abc1
```

### 3️⃣ Clone Repository
```bash
git clone https://github.com/YOUR-USERNAME/tap-miner-bot.git
cd tap-miner-bot
```

### 4️⃣ Install Dependencies
```bash
pip install -r requirements.txt
```

### 5️⃣ Configure Bot
Copy `.env.example` to `.env`:
```bash
cp .env.example .env
```

Edit `.env` and fill in:
```
TELEGRAM_BOT_TOKEN=your_token_here
MINER_CONTRACT_ADDRESS=0:your_address_here
GAME_ROOT_ADDRESS=0:your_game_root_address
```

### 6️⃣ Run Bot
```bash
python tap_bot_mv.py
```

### 7️⃣ Test in Telegram
- Find your bot: `@tap_miner_bot`
- Send: `/start`
- Send your Miner address
- **Get tap data instantly!** ✅

## 📖 Documentation

| Document | Purpose |
|----------|---------|
| [SETUP_GUIDE_MV.md](docs/SETUP_GUIDE_MV.md) | Complete setup walkthrough (for beginners) |
| [CONTRACTS_REFERENCE.md](docs/CONTRACTS_REFERENCE.md) | Technical contract details (for developers) |

## 📋 Commands

| Command | What It Does |
|---------|-------------|
| `/start` | Welcome message & instructions |
| `/help` | Show all available commands |
| `/status` | Check bot connection status |
| `/epoch` | Show epoch reset time (approx) |
| Send Miner address | Get your tap data & stats |

**Example:**
```
User: /start
Bot: Welcome! Send your Miner address...

User: 0:abc123def456...
Bot: Shows your tap count, balance, difficulty, epoch info
```

## 🏗️ Architecture

```
MobileVerifiersContractGameRoot (Game Root)
    └─ Miner[You] ← Bot queries this!
        ├─ tapSum (total taps)
        ├─ epochStart (current epoch)
        ├─ easyComplexity (mining difficulty)
        └─ hardComplexity (mining difficulty)
```

## 🌐 Free Hosting Options

Bot runs **24/7 for free** on:

| Platform | Ease | Setup Time | Always On |
|----------|------|-----------|-----------|
| [Replit](https://replit.com) | ⭐⭐⭐ Easy | 2 min | ✅ Yes |
| [Railway](https://railway.app) | ⭐⭐ Medium | 5 min | ✅ Yes |
| [Render](https://render.com) | ⭐⭐ Medium | 5 min | ⚠️ Sleeps |
| [PythonAnywhere](https://pythonanywhere.com) | ⭐⭐ Medium | 5 min | ✅ Yes |

**Recommended:** Replit (easiest)

See [SETUP_GUIDE_MV.md](docs/SETUP_GUIDE_MV.md) for deployment instructions.

## 🔐 Security

⚠️ **IMPORTANT:**

- ✅ **DO:** Keep `.env` file local (never commit it)
- ✅ **DO:** Use `.env.example` as template
- ✅ **DO:** Keep bot token SECRET
- ❌ **DON'T:** Share `.env` file
- ❌ **DON'T:** Post bot token in forums
- ❌ **DON'T:** Commit `.env` to GitHub

The `.gitignore` file automatically prevents accidental commits of `.env`.

## 📦 Requirements

- Python 3.9 or higher
- `python-telegram-bot>=21.0` - Telegram bot framework
- `httpx>=0.25.0` - HTTP client for blockchain queries

Install all:
```bash
pip install -r requirements.txt
```

## ⚙️ Configuration

### Environment Variables

Create `.env` file from `.env.example`:

```bash
cp .env.example .env
```

Edit with your values:
```
# Required
TELEGRAM_BOT_TOKEN=1234567890:ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefgh1
MINER_CONTRACT_ADDRESS=0:abc123...

# Optional
GAME_ROOT_ADDRESS=0:xyz789...
GRAPHQL_ENDPOINT=https://shellnet.ackinacki.org/graphql
```

### Network Configuration

Default configured for **Shellnet** (Acki Nacki testnet):
```
GRAPHQL_ENDPOINT=https://shellnet.ackinacki.org/graphql
EPOCH_DURATION=2200000 blocks (≈ 3.3 hours)
```

## 🐛 Troubleshooting

### Bot doesn't respond
```
✓ Check TELEGRAM_BOT_TOKEN is correct
✓ Ensure internet connection
✓ Look for "Polling for messages" in terminal
✓ Restart: python tap_bot_mv.py
```

### "Contract not found" error
```
✓ Verify Miner address format (0:abc...)
✓ Check address exists on block explorer
✓ Ask game provider for correct address
✓ Confirm address is on Shellnet network
```

### Connection timeout
```
✓ Check internet connection
✓ Verify GRAPHQL_ENDPOINT is correct
✓ Check if Acki Nacki network is up
✓ Try again in a few minutes
```

### ModuleNotFoundError
```bash
pip install -r requirements.txt
```

For more help, see [SETUP_GUIDE_MV.md](docs/SETUP_GUIDE_MV.md#troubleshooting).

## 📊 Data You Get

Send your Miner address and receive:

```
🎮 Mobile Verifier Miner Data

🔐 Miner Address: 0:abc123...
💰 Balance: 42.50 SHELL
📊 Account Type: Active
⏰ Last Updated: 2026-04-19 15:30:45 UTC

🎯 Epoch Info:
⏳ Next Reset (approx): 12h 45m
```

## 🔗 Useful Links

- **Acki Nacki:** https://ackinacki.com
- **Acki Nacki Docs:** https://docs.ackinacki.com
- **Acki Nacki GitHub:** https://github.com/ackinacki/ackinacki
- **Mobile Verifier Contracts:** https://github.com/ackinacki/ackinacki/tree/main/contracts/mvsystem
- **Telegram:** https://t.me/ackinackinews
- **Block Explorer:** https://shellnet.ackinacki.org

## 👨‍💻 How to Contribute

Contributions welcome! Areas for improvement:

- [ ] Support for mainnet
- [ ] Web dashboard
- [ ] Detailed tap statistics
- [ ] Reward notifications
- [ ] Multi-user support
- [ ] Database for historical data
- [ ] Advanced analytics

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📝 File Structure

```
tap-miner-bot/
├── README.md                    # This file
├── LICENSE                      # MIT License
├── .gitignore                   # Git ignore rules
├── .env.example                 # Config template
├── requirements.txt             # Python dependencies
├── tap_bot_mv.py               # Main bot code
└── docs/
    ├── SETUP_GUIDE_MV.md       # Detailed setup guide
    └── CONTRACTS_REFERENCE.md  # Contract documentation
```

## 📄 License

MIT License - See [LICENSE](LICENSE) file for details.

This means you can:
- ✅ Use commercially
- ✅ Modify the code
- ✅ Distribute
- ✅ Use privately

Just include the original license.

## 🤝 Support

Need help?

1. **Read the docs:**
   - [SETUP_GUIDE_MV.md](docs/SETUP_GUIDE_MV.md) - Step-by-step setup
   - [CONTRACTS_REFERENCE.md](docs/CONTRACTS_REFERENCE.md) - Technical details

2. **Check Troubleshooting** - Common issues above

3. **Ask on Acki Nacki:**
   - Telegram: https://t.me/ackinackinews
   - GitHub Discussions: [Create Discussion](https://github.com/YOUR-USERNAME/tap-miner-bot/discussions)

## 📈 Roadmap

- ✅ v1.0 - Basic tap tracking
- 🚧 v1.1 - Reward calculation
- 🚧 v1.2 - Historical tracking
- 🚧 v2.0 - Web dashboard
- 🚧 v2.1 - Multi-user support
- 🚧 v3.0 - Mainnet support

## 🌟 Show Your Support

If this project helped you, please:

- ⭐ Star this repository
- 🐦 Share on Twitter/socials
- 👥 Recommend to friends
- 📝 Report bugs or suggest features

## 📧 Contact

- **Author:** Your Name
- **Email:** your.email@example.com
- **Telegram:** https://t.me/username

## 🎯 Project Status

| Component | Status |
|-----------|--------|
| Bot | ✅ Active |
| Telegram Integration | ✅ Working |
| Blockchain Queries | ✅ Working |
| Documentation | ✅ Complete |
| Testing | ✅ Tested |

## 🙏 Acknowledgments

- [Acki Nacki](https://ackinacki.com) - Blockchain network
- [python-telegram-bot](https://python-telegram-bot.org) - Telegram bot library
- [GOSH](https://gosh.sh) - TVM blockchain technology
- Community feedback and contributions

---

**Made with ❤️ for the Acki Nacki community**

⭐ If you found this useful, please star the repository!

---

**Last Updated:** April 19, 2026
**Version:** 1.0.0
**License:** MIT
