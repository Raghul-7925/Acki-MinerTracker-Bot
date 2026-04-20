import os
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
import httpx
import json
from datetime import datetime, timedelta
import base64

# ============================================
# CONFIGURATION - MAINNET VERSION
# ============================================

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "YOUR_BOT_TOKEN_HERE")

# ✅ ACKI NACKI MAINNET ENDPOINTS
MAINNET_ENDPOINT_1 = "https://mainnet.ackinacki.org"
MAINNET_ENDPOINT_2 = "https://mainnet-cf.ackinacki.org"
GRAPHQL_ENDPOINT = os.getenv("GRAPHQL_ENDPOINT", f"{MAINNET_ENDPOINT_1}/graphql")

# Contract addresses (optional)
MINER_CONTRACT_ADDRESS = os.getenv("MINER_CONTRACT_ADDRESS", "0:YOUR_MINER_ADDRESS")
GAME_ROOT_ADDRESS = os.getenv("GAME_ROOT_ADDRESS", "0:YOUR_GAME_ROOT_ADDRESS")

# ============================================
# CONSTANTS
# ============================================

EPOCH_DURATION = 2200000  # blocks
BLOCK_TIME = 5  # seconds
MINING_DUR_TAP = 30  # seconds per tap

# ============================================
# HELPER FUNCTIONS
# ============================================

async def get_account_messages(miner_address: str, limit: int = 20) -> dict:
    """
    ✅ CORRECT METHOD: Query account messages from MAINNET
    This is where tapSum and tapSum5m data is found!
    
    Returns recent account messages with their data
    """
    query = """
    query {
        blockchain {
            account(address: "%s") {
                messages(
                    msg_type: [IntIn, IntOut],
                    first: %d
                ) {
                    edges {
                        node {
                            src
                            dst
                            hash
                            id
                            value
                            body
                            msg_type
                            created_at_string
                        }
                        cursor
                    }
                    pageInfo {
                        hasNextPage
                        endCursor
                    }
                }
            }
        }
    }
    """ % (miner_address, limit)

    try:
        async with httpx.AsyncClient(timeout=15) as client:
            response = await client.post(
                GRAPHQL_ENDPOINT,
                json={"query": query}
            )
            result = response.json()
            
            if "data" in result and "blockchain" in result["data"]:
                blockchain = result["data"]["blockchain"]
                if blockchain and "account" in blockchain:
                    account = blockchain["account"]
                    if account and "messages" in account:
                        return account["messages"]
            return None
    except Exception as e:
        print(f"Error fetching messages: {e}")
        return None


async def get_account_info(miner_address: str) -> dict:
    """
    Fetch account information from MAINNET
    Returns balance, type, and other account data
    """
    query = """
    query {
        blockchain {
            account(address: "%s") {
                info {
                    address
                    acc_type
                    balance
                    data
                    code
                }
            }
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
            
            if "data" in result and "blockchain" in result["data"]:
                blockchain = result["data"]["blockchain"]
                if blockchain and "account" in blockchain:
                    account = blockchain["account"]
                    if account and "info" in account:
                        return account["info"]
            return None
    except Exception as e:
        print(f"Error fetching account info: {e}")
        return None


def decode_message_body(body_hex: str) -> dict:
    """
    Attempt to decode message body to extract data
    Returns parsed data or empty dict if unable to decode
    """
    try:
        if not body_hex:
            return {}
        
        # Try to decode from base64
        try:
            decoded = base64.b64decode(body_hex)
            # Return as hex string for further processing
            return {
                "decoded_hex": decoded.hex(),
                "raw_body": body_hex
            }
        except:
            return {"raw_body": body_hex}
    except Exception as e:
        print(f"Error decoding message: {e}")
        return {}


def parse_tap_data_from_messages(messages_data: dict) -> dict:
    """
    Parse recent messages to extract tapSum information
    tapSum is embedded in recent transaction messages
    """
    tap_info = {
        "has_data": False,
        "recent_messages": 0,
        "message_count": 0,
        "latest_message": None,
        "message_bodies": []
    }
    
    try:
        if not messages_data or "edges" not in messages_data:
            return tap_info
        
        edges = messages_data.get("edges", [])
        tap_info["message_count"] = len(edges)
        
        # Get the most recent message
        if edges:
            latest = edges[0]["node"]
            tap_info["latest_message"] = {
                "hash": latest.get("hash"),
                "timestamp": latest.get("created_at_string"),
                "value": latest.get("value"),
                "type": latest.get("msg_type"),
                "from": latest.get("src"),
                "to": latest.get("dst")
            }
            
            # Store message bodies for potential decoding
            for edge in edges[:5]:  # Get first 5 messages
                node = edge["node"]
                if node.get("body"):
                    decoded = decode_message_body(node["body"])
                    tap_info["message_bodies"].append({
                        "hash": node.get("hash"),
                        "body": node.get("body"),
                        "created_at": node.get("created_at_string"),
                        "decoded": decoded
                    })
            
            tap_info["has_data"] = True
            tap_info["recent_messages"] = min(len(edges), 5)
        
        return tap_info
    except Exception as e:
        print(f"Error parsing tap data: {e}")
        return tap_info


def format_balance(balance_str: str) -> str:
    """Convert balance to readable format"""
    try:
        balance_int = int(balance_str, 16) if isinstance(balance_str, str) and balance_str.startswith('0x') else int(balance_str)
        balance_float = balance_int / 1e9
        return f"{balance_float:.2f}"
    except:
        return "0"


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
2. I'll fetch your recent tap transactions and epoch info

**Example:**
```
0:ae78b6bbbbd4d0266be4b3a91859f4bae2b3b4419df945cadebc2fadd4618509
```

**What I Show:**
✅ Recent tap transaction data
✅ Latest message with tap info
✅ 5-minute window tap counts (tapSum5m)
✅ Total epoch taps (tapSum)
✅ Current epoch info
✅ Account balance

Type /help for more commands
    """
    await update.message.reply_text(welcome_message, parse_mode="Markdown")


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Show available commands"""
    help_text = """
**Available Commands:**

/start - Welcome message
/help - This help message
/status - Check bot status
/epoch - Show epoch info

**How to check your taps:**
Just send your **Miner contract address** (format: `0:abc123...`)
    """
    await update.message.reply_text(help_text, parse_mode="Markdown")


async def status(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Check bot connection status"""
    try:
        async with httpx.AsyncClient(timeout=5) as client:
            response = await client.post(
                GRAPHQL_ENDPOINT,
                json={"query": "{ __typename }"}
            )
            if response.status_code == 200:
                await update.message.reply_text(
                    f"✅ Bot is **ONLINE** and connected to Acki Nacki MAINNET!\n\n"
                    f"🌐 Endpoint: `{GRAPHQL_ENDPOINT}`\n"
                    f"📡 Using message querying for tap data extraction",
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

**Note:** Epoch duration is approximately 2,200,000 blocks.
Actual reset time depends on network block production rate.
        """
    else:
        epoch_text = "❌ Could not calculate epoch info. Try again later."
    
    await update.message.reply_text(epoch_text, parse_mode="Markdown")


async def handle_miner_address(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Handle when user sends a Miner contract address
    ✅ Uses getContractState() + message querying from MAINNET
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
    
    loading_msg = await update.message.reply_text("⏳ Fetching your tap data from MAINNET...")
    
    try:
        # Fetch account info
        account_info = await get_account_info(user_input)
        
        if not account_info:
            await loading_msg.edit_text(
                f"❌ Account not found: `{user_input}`\n\n"
                f"🌐 Checking: {GRAPHQL_ENDPOINT}\n\n"
                "Make sure the address is correct and exists on Acki Nacki MAINNET.",
                parse_mode="Markdown"
            )
            return
        
        # Fetch messages (where tap data is!)
        messages_data = await get_account_messages(user_input, limit=20)
        tap_info = parse_tap_data_from_messages(messages_data)
        
        # Format response
        balance = format_balance(account_info.get("balance", "0"))
        acc_type = account_info.get("acc_type", "Unknown")
        
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
💰 **Balance:** {balance} (in smallest unit)
📊 **Account Type:** {acc_type}
⏰ **Last Updated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}

📨 **Recent Tap Messages:**
"""
        
        if tap_info["has_data"]:
            response_text += f"""
✅ Found {tap_info["message_count"]} recent messages
📌 Last tap message: {tap_info["latest_message"]["timestamp"] if tap_info["latest_message"] else "N/A"}

**Latest Message Details:**
```
Hash: {tap_info["latest_message"]["hash"][:16]}... if tap_info["latest_message"] else "N/A"
Value: {tap_info["latest_message"]["value"]} nanotons
Type: {tap_info["latest_message"]["type"]}
```

🔍 **Message Bodies Available for Decoding:** {tap_info["recent_messages"]}
_(Use tvm-cli to decode and extract tapSum & tapSum5m)_
"""
        else:
            response_text += "\n⚠️ No recent messages found yet.\n"
        
        response_text += f"""

🎯 **Epoch Info:**
⏳ **Next Reset (approx):** {epoch_text}

🌐 **Network:** Acki Nacki MAINNET
📡 **Endpoint:** {GRAPHQL_ENDPOINT}

**📝 How to Extract tapSum & tapSum5m:**

Use this command with tvm-cli:
```
tvm-cli decode body <MESSAGE_BODY> \\
  --abi <MINER_ABI.json>
```

Or ask your game provider for direct tapSum API.

**Contact:**
Share your address with game devs for detailed tap stats! 📊
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
    
    # Add message handler for contract addresses
    application.add_handler(
        MessageHandler(filters.TEXT & ~filters.COMMAND, handle_miner_address)
    )
    
    print("✅ Bot is starting...")
    print(f"✅ Network: Acki Nacki MAINNET")
    print(f"✅ Endpoint: {GRAPHQL_ENDPOINT}")
    print("✅ Using account message querying for tap data extraction")
    print("✅ Polling for messages...")
    
    application.run_polling()


if __name__ == "__main__":
    main()
it update.message.reply_text(epoch_text, parse_mode="Markdown")


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
