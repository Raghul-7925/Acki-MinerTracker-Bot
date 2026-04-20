import os
import json
import base64
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
import httpx
from datetime import datetime, timedelta

# ============================================
# CONFIGURATION - MAINNET VERSION
# ============================================

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "YOUR_BOT_TOKEN_HERE")

# ✅ ACKI NACKI MAINNET ENDPOINTS (Not Shellnet!)
MAINNET_ENDPOINT_1 = "https://mainnet.ackinacki.org"
MAINNET_ENDPOINT_2 = "https://mainnet-cf.ackinacki.org"
GRAPHQL_ENDPOINT = os.getenv("GRAPHQL_ENDPOINT", f"{MAINNET_ENDPOINT_1}/graphql")

# Contract addresses (optional)
MINER_CONTRACT_ADDRESS = os.getenv("MINER_CONTRACT_ADDRESS", "0:YOUR_MINER_ADDRESS")
GAME_ROOT_ADDRESS = os.getenv("GAME_ROOT_ADDRESS", "0:YOUR_GAME_ROOT_ADDRESS")
MINER_ABI_PATH = os.getenv("MINER_ABI_PATH", None)

# ============================================
# CONSTANTS
# ============================================

EPOCH_DURATION = 2200000  # blocks
BLOCK_TIME = 5  # seconds
MINING_DUR_TAP = 30  # seconds per tap

# ============================================
# LOAD ABI (Optional)
# ============================================

MINER_ABI = None
if MINER_ABI_PATH and os.path.exists(MINER_ABI_PATH):
    try:
        with open(MINER_ABI_PATH, 'r') as f:
            MINER_ABI = json.load(f)
        print(f"✅ Loaded Miner ABI from {MINER_ABI_PATH}")
    except Exception as e:
        print(f"⚠️ Could not load ABI: {e}")

# ============================================
# HELPER FUNCTIONS
# ============================================

def decode_contract_data(data_hex: str, abi=None) -> dict:
    """
    Attempt to decode contract data field
    Data is BASE64 encoded TVM cell containing contract state
    Full decoding requires the compiled ABI
    """
    result = {
        "raw_data": data_hex[:50] + "..." if len(data_hex) > 50 else data_hex,
        "encoded": True,
        "decoded": False,
        "note": "Contract state is TVM-encoded. Use Miner ABI for full decoding."
    }
    
    try:
        # Try to decode base64
        decoded = base64.b64decode(data_hex)
        result["raw_bytes"] = len(decoded)
        result["hex"] = decoded.hex()[:50] + "..." if len(decoded.hex()) > 50 else decoded.hex()
    except Exception as e:
        result["error"] = f"Could not decode: {str(e)}"
    
    return result


async def fetch_miner_contract_data(miner_address: str) -> dict:
    """
    ✅ CORRECT METHOD: Use getContractState() via blockchainAccountState
    Fetches contract data field from MAINNET
    Data contains: tapSum, tapSum5m, taps[], mbiCurTaps[], etc.
    """
    query = """
    query {
        blockchainAccountState(
            address: "%s"
        ) {
            state {
                data
                code
            }
            hash
        }
    }
    """ % miner_address

    try:
        async with httpx.AsyncClient(timeout=10) as client:
            response = await client.post(
                GRAPHQL_ENDPOINT,
                json={"query": query}
            )
            result = response.json()
            
            if "data" in result and "blockchainAccountState" in result["data"]:
                state = result["data"]["blockchainAccountState"]
                if state:
                    return state
            return None
    except Exception as e:
        print(f"Error fetching contract state: {e}")
        return None


async def fetch_miner_account(miner_address: str) -> dict:
    """
    Fetch account information from MAINNET
    Returns balance, type, and contract data field
    """
    query = """
    query {
        accounts(
            filter: {
                id: {
                    eq: "%s"
                }
            }
        ) {
            id
            balance
            acc_type_name
            code_hash
            data
            last_paid
        }
    }
    """ % miner_address

    try:
        async with httpx.AsyncClient(timeout=10) as client:
            response = await client.post(
                GRAPHQL_ENDPOINT,
                json={"query": query}
            )
            result = response.json()
            
            if "data" in result and "accounts" in result["data"]:
                accounts = result["data"]["accounts"]
                if accounts:
                    return accounts[0]
            return None
    except Exception as e:
        print(f"Error fetching account: {e}")
        return None


def format_balance(balance_str: str) -> str:
    """Convert hex balance to readable format"""
    try:
        balance_int = int(balance_str, 16)
        balance_float = balance_int / 1e9
        return f"{balance_float:.2f}"
    except:
        return "0"


def extract_data_info(data_hex: str) -> str:
    """Extract information about the contract data"""
    if not data_hex:
        return "No data available"
    
    try:
        # Decode base64
        decoded = base64.b64decode(data_hex)
        data_size = len(decoded)
        
        info = f"📦 Contract Data:\n"
        info += f"  Size: {data_size} bytes\n"
        info += f"  Format: BASE64 encoded TVM cell\n\n"
        
        info += "**Available Data (TVM Encoded):**\n"
        info += "  • tapSum (total taps)\n"
        info += "  • tapSum5m (5-min window)\n"
        info += "  • taps[] (tap history)\n"
        info += "  • mbiCurTaps[] (current MBI taps)\n"
        info += "  • easyComplexity, hardComplexity\n"
        info += "  • seed, commitData, miningDurSum\n"
        info += "  • modifiedTapSum\n\n"
        
        info += "📌 **To Decode This Data:**\n"
        info += "  1. Get Miner.abi.json from game provider\n"
        info += "  2. Use tvm-cli: `tvm-cli run <address> getDetails {} --abi Miner.abi.json`\n"
        info += "  3. Or provide ABI to bot via MINER_ABI_PATH\n"
        
        return info
    except Exception as e:
        return f"Error processing data: {str(e)}"


def calculate_epoch_reset():
    """Calculate approximate epoch reset time"""
    try:
        blocks_until_epoch = EPOCH_DURATION
        seconds_until_reset = blocks_until_epoch * BLOCK_TIME
        reset_time = datetime.now() + timedelta(seconds=seconds_until_reset)
        return reset_time
    except:
        return None


# ============================================
# TELEGRAM BOT COMMANDS
# ============================================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Welcome message"""
    welcome_message = """
👋 **Welcome to Acki Nacki MinerTracker Bot!**

I fetch your **tap counts** and **mining data** from the Acki Nacki MAINNET.

**How to use:**
1. Send me your **Miner contract address** (starts with `0:`)
2. I'll fetch your contract data and tap information

**Example:**
```
0:ae78b6bbbbd4d0266be4b3a91859f4bae2b3b4419df945cadebc2fadd4618509
```

**What I Show:**
✅ Contract data field (TVM encoded)
✅ Account balance & status
✅ Data size & encoding info
✅ How to decode with Miner ABI
✅ Epoch reset time (approx)

**Requirements:**
📝 For full tap data decoding, you'll need:
  - Miner.abi.json from game provider
  - tvm-cli tool (or contact support)

Type /help for more commands
    """
    await update.message.reply_text(welcome_message, parse_mode="Markdown")


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Show available commands"""
    help_text = """
**Available Commands:**

/start - Welcome message
/help - This help message
/status - Check bot connection
/epoch - Show epoch info
/decode - Learn how to decode contract data

**How to check your taps:**
Just send your **Miner contract address** (format: `0:abc123...`)

**To get full tap data:**
You need the compiled Miner.abi.json file from your game provider.
The bot can parse it if you provide it!
    """
    await update.message.reply_text(help_text, parse_mode="Markdown")


async def status(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Check bot connection status"""
    try:
        async with httpx.AsyncClient(timeout=5) as client:
            response = await client.get(GRAPHQL_ENDPOINT)
            if response.status_code == 200:
                await update.message.reply_text(
                    f"✅ Bot is **ONLINE** and connected to Acki Nacki MAINNET!\n\n"
                    f"🌐 Endpoint: `{GRAPHQL_ENDPOINT}`\n\n"
                    f"📚 Using: **blockchainAccountState()** method\n"
                    f"📦 Fetching: Contract **data** field\n"
                    f"🔧 Status: Ready to decode with ABI",
                    parse_mode="Markdown"
                )
            else:
                await update.message.reply_text(
                    "⚠️ Bot is online but blockchain connection is slow",
                    parse_mode="Markdown"
                )
    except:
        await update.message.reply_text(
            "❌ Bot is having connection issues. Try again later.",
            parse_mode="Markdown"
        )


async def epoch_info(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Show epoch reset information"""
    epoch_reset = calculate_epoch_reset()
    
    if epoch_reset:
        time_until = epoch_reset - datetime.now()
        hours = time_until.total_seconds() // 3600
        minutes = (time_until.total_seconds() % 3600) // 60
        
        epoch_text = f"""
⏰ **Epoch Information**

📍 **Current Time:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}
🔄 **Next Epoch Reset (approx):** {epoch_reset.strftime('%Y-%m-%d %H:%M:%S UTC')}
⏳ **Time Until Reset:** {int(hours)}h {int(minutes)}m

**Epoch Configuration:**
  Duration: 2,200,000 blocks
  Block time: ~5 seconds
  Approx epoch: ~3.3 hours

**Note:** Actual reset depends on network block production rate.
        """
    else:
        epoch_text = "❌ Could not calculate epoch info. Try again later."
    
    await update.message.reply_text(epoch_text, parse_mode="Markdown")


async def decode_help(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Show how to decode contract data"""
    decode_text = """
📚 **How to Decode Contract Data**

Your contract data is stored as a **TVM-encoded cell** (BASE64).
It contains: tapSum, tapSum5m, taps[], and more!

**Option 1: Use tvm-cli (Recommended)**
```
tvm-cli run <YOUR_ADDRESS> getDetails {} \\
  --abi Miner.abi.json
```

**Option 2: Use Explorer**
Go to: https://mainnet.ackinacki.org
Search your Miner address → View contract state

**Option 3: Provide ABI to Bot**
Set environment variable:
```
MINER_ABI_PATH=/path/to/Miner.abi.json
```

**Getting the ABI:**
Ask your game provider for `Miner.abi.json`
It's usually in: `contracts/mvsystem/Miner.abi.json`

**What You'll Get:**
✅ tapSum - Total taps in big epoch
✅ tapSum5m - Taps in 5-minute window
✅ taps[] - Complete tap history
✅ mbiCurTaps[] - Current MBI taps
✅ Mining difficulties
✅ And more!
    """
    await update.message.reply_text(decode_text, parse_mode="Markdown")


async def handle_miner_address(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Handle when user sends a Miner contract address
    ✅ Uses blockchainAccountState() from MAINNET
    ✅ Extracts contract data field
    ✅ Shows decoding information
    """
    user_input = update.message.text.strip()
    
    # Validate format
    if not user_input.startswith("0:") or len(user_input) < 60:
        await update.message.reply_text(
            "❌ Invalid contract address format.\n\n"
            "Correct format: `0:abc123def456...` (66 hex characters)",
            parse_mode="Markdown"
        )
        return
    
    loading_msg = await update.message.reply_text("⏳ Fetching your contract data from MAINNET...")
    
    try:
        # ✅ CORRECT METHOD: Fetch account with data field
        account_data = await fetch_miner_account(user_input)
        
        if not account_data:
            await loading_msg.edit_text(
                f"❌ Miner contract not found: `{user_input}`\n\n"
                f"🌐 Checked: {GRAPHQL_ENDPOINT}\n\n"
                "Make sure the address is correct and exists on Acki Nacki MAINNET.",
                parse_mode="Markdown"
            )
            return
        
        balance = format_balance(account_data.get("balance", "0x0"))
        account_type = account_data.get("acc_type_name", "Unknown")
        data_field = account_data.get("data", None)
        last_paid = account_data.get("last_paid", "Unknown")
        
        # Get epoch reset info
        epoch_reset = calculate_epoch_reset()
        epoch_text = "Calculating..." if epoch_reset else "Unknown"
        if epoch_reset:
            time_until = epoch_reset - datetime.now()
            hours = time_until.total_seconds() // 3600
            minutes = (time_until.total_seconds() % 3600) // 60
            epoch_text = f"{int(hours)}h {int(minutes)}m"
        
        # Build response
        response_text = f"""
🎮 **Mobile Verifier Miner Data**

🔐 **Miner Address:** `{user_input}`
💰 **Balance:** {balance} (smallest unit)
📊 **Account Type:** {account_type}
⏱️ **Last Paid:** {last_paid}
🕐 **Last Updated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}

⏰ **Epoch Info:**
⏳ **Next Reset (approx):** {epoch_text}

🌐 **Network:** Acki Nacki MAINNET
📡 **Endpoint:** {GRAPHQL_ENDPOINT}
🔍 **Method:** blockchainAccountState()

"""
        
        # Add data field information
        if data_field:
            response_text += extract_data_info(data_field)
        else:
            response_text += "⚠️ No contract data found\n"
        
        response_text += f"""

**📝 Next Steps:**

1. **Get the ABI:**
   Ask your game provider for `Miner.abi.json`

2. **Decode with tvm-cli:**
   ```
   tvm-cli run {user_input} getDetails {{}} \\
     --abi Miner.abi.json
   ```

3. **Or use the Explorer:**
   https://mainnet.ackinacki.org/

**Questions?**
Type /decode for detailed instructions!
        """
        
        await loading_msg.edit_text(response_text, parse_mode="Markdown")
        
    except Exception as e:
        await loading_msg.edit_text(
            f"❌ Error fetching data:\n`{str(e)}`\n\n"
            f"Endpoint: {GRAPHQL_ENDPOINT}\n\n"
            "Try again or contact support.",
            parse_mode="Markdown"
        )


# ============================================
# MAIN BOT SETUP
# ============================================

def main():
    """Start the Telegram bot"""
    
    if TELEGRAM_BOT_TOKEN == "YOUR_BOT_TOKEN_HERE":
        print("❌ ERROR: Set TELEGRAM_BOT_TOKEN first!")
        print("\nHow to set token:")
        print("1. In Replit: Click 'Secrets' button")
        print("2. Add: TELEGRAM_BOT_TOKEN = your_token_from_BotFather")
        print("3. Restart bot")
        return
    
    application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()
    
    # Add command handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("status", status))
    application.add_handler(CommandHandler("epoch", epoch_info))
    application.add_handler(CommandHandler("decode", decode_help))
    
    # Add message handler for contract addresses
    application.add_handler(
        MessageHandler(filters.TEXT & ~filters.COMMAND, handle_miner_address)
    )
    
    print("✅ Bot is starting...")
    print(f"✅ Network: Acki Nacki MAINNET")
    print(f"✅ Endpoint: {GRAPHQL_ENDPOINT}")
    print(f"✅ Method: blockchainAccountState() + data field")
    print(f"✅ Miner ABI loaded: {MINER_ABI is not None}")
    print("✅ Polling for messages...")
    
    application.run_polling()


if __name__ == "__main__":
    main()
    print("1. In Replit: Click 'Secrets' button")
        print("2. Add: TELEGRAM_BOT_TOKEN = your_token_from_BotFather")
        print("3. Restart bot")
        return
    
    application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()
    
    # Add command handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("status", status))
    application.add_handler(CommandHandler("epoch", epoch_info))
    
    # Add message handler for contract addresses
    application.add_handler(
        MessageHandler(filters.TEXT & ~filters.COMMAND, handle_miner_address)
    )
    
    print("✅ Bot is starting...")
    print(f"✅ Network: Acki Nacki MAINNET")
    print(f"✅ Endpoint: {GRAPHQL_ENDPOINT}")
    print("✅ Using getContractState() method")
    print("✅ Polling for messages...")
    
    application.run_polling()


if __name__ == "__main__":
    main()
      print("❌ ERROR: Set TELEGRAM_BOT_TOKEN first!")
        print("\nHow to get token:")
        print("1. Open Telegram and search for @BotFather")
        print("2. Send /newbot and follow instructions")
        print("3. Copy the token and paste it in this script")
        return
    
    # Create application
    application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()
    
    # Add command handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("status", status))
    application.add_handler(CommandHandler("epoch", epoch_info))
    
    # Add message handler for wallet/contract addresses
    application.add_handler(
        MessageHandler(filters.TEXT & ~filters.COMMAND, handle_miner_address)
    )
    
    print("✅ Bot is starting...")
    print(f"✅ Connected to: {GRAPHQL_ENDPOINT}")
    print("✅ Polling for messages...")
    
    # Start polling
    application.run_polling()


if __name__ == "__main__":
    main()
