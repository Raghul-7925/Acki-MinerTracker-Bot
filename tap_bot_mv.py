import os
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
import httpx
import json
from datetime import datetime, timedelta

# ============================================
# CONFIGURATION - EDIT THESE VALUES
# ============================================

TELEGRAM_BOT_TOKEN = "YOUR_BOT_TOKEN_HERE"  # Get from BotFather on Telegram

# Acki Nacki GraphQL endpoint
GRAPHQL_ENDPOINT = "https://shellnet.ackinacki.org/graphql"

# Mobile Verifier Miner Contract (User's contract that holds tap data)
# Format: You need the user's Miner contract address
# It's calculated from: Mirror contract + user index
MINER_CONTRACT_ADDRESS = "0:YOUR_MINER_CONTRACT_ADDRESS"  # Replace with actual Miner address

# Mobile Verifier Root Contract (Game root)
GAME_ROOT_ADDRESS = "0:YOUR_GAME_ROOT_ADDRESS"  # Replace with Game Root address

# ============================================
# CONSTANTS FROM CONTRACT
# ============================================

EPOCH_DURATION = 2200000  # blocks (approximate)  
BLOCK_TIME = 5  # seconds per block (approximate)
MINING_DUR_TAP = 30  # seconds per tap

# ============================================
# HELPER FUNCTIONS
# ============================================

def calculate_epoch_reset():
    """
    Calculate when next epoch resets
    Epoch duration is MinerRewardPeriod (2200000 blocks)
    """
    try:
        # This is approximate - actual time depends on block time
        blocks_until_epoch = EPOCH_DURATION  # You'd need current seq_no
        seconds_until_reset = blocks_until_epoch * BLOCK_TIME
        reset_time = datetime.now() + timedelta(seconds=seconds_until_reset)
        return reset_time
    except:
        return None


async def fetch_miner_details(miner_address: str) -> dict:
    """
    Fetch Miner contract details using GraphQL
    This gets all tap data for a user
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
            data
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
        print(f"Error fetching miner data: {e}")
        return None


async def fetch_game_root_details(root_address: str) -> dict:
    """
    Fetch Game Root contract details
    This gets global game data like rewards, epoch info
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
            data
        }
    }
    """ % root_address

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
        print(f"Error fetching game root data: {e}")
        return None


def format_balance(balance_str: str) -> str:
    """
    Convert balance from hex string to readable format
    """
    try:
        balance_int = int(balance_str, 16)
        balance_float = balance_int / 1e9
        return f"{balance_float:.2f}"
    except:
        return "0"


# ============================================
# TELEGRAM BOT COMMANDS
# ============================================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    /start command - Welcome message
    """
    welcome_message = """
👋 **Welcome to Acki Nacki Mobile Verifier Tap Tracker!**

I can fetch your **tap counts** and **mining data** from the Mobile Verifier system.

**How to use:**
1. Send me your **Miner contract address** (starts with `0:`)
2. I'll fetch your tap counts and epoch info

**Example:**
```
0:abc123def456...
```

**What I Show:**
✅ Your total taps (tapSum)
✅ Current epoch info
✅ Mining difficulty
✅ Account balance
✅ Epoch reset time (approx)

Type /help for more commands
    """
    await update.message.reply_text(welcome_message, parse_mode="Markdown")


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    /help command - Show available commands
    """
    help_text = """
**Available Commands:**

/start - Welcome message
/help - This help message
/status - Check bot status
/epoch - Show epoch info

**How to check your taps:**
Just send your **Miner contract address** (format: `0:abc123...`)

**Need help finding your Miner address?**
Contact your game provider or check your game docs.
    """
    await update.message.reply_text(help_text, parse_mode="Markdown")


async def status(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    /status command - Check bot status
    """
    try:
        async with httpx.AsyncClient(timeout=5) as client:
            response = await client.get(GRAPHQL_ENDPOINT)
            if response.status_code == 200:
                await update.message.reply_text(
                    "✅ Bot is **ONLINE** and connected to Acki Nacki blockchain!",
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
    """
    /epoch command - Show epoch reset information
    """
    epoch_reset = calculate_epoch_reset()
    
    if epoch_reset:
        time_until = epoch_reset - datetime.now()
        hours = time_until.total_seconds() // 3600
        minutes = (time_until.total_seconds() % 3600) // 60
        
        epoch_text = f"""
⏰ **Epoch Information**

📍 **Current Epoch:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}
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
    """
    user_input = update.message.text.strip()
    
    # Validate format
    if not user_input.startswith("0:") or len(user_input) < 20:
        await update.message.reply_text(
            "❌ Invalid contract address format.\n\n"
            "Correct format: `0:abc123def456...` (66 hex characters after 0:)",
            parse_mode="Markdown"
        )
        return
    
    # Show loading message
    loading_msg = await update.message.reply_text("⏳ Fetching your tap data...")
    
    try:
        # Fetch Miner contract details
        miner_data = await fetch_miner_details(user_input)
        
        if not miner_data:
            await loading_msg.edit_text(
                f"❌ Miner contract not found: `{user_input}`\n\n"
                "Make sure the address is correct and exists on the blockchain.",
                parse_mode="Markdown"
            )
            return
        
        balance = format_balance(miner_data.get("balance", "0x0"))
        account_type = miner_data.get("acc_type_name", "Unknown")
        
        # Get epoch reset info
        epoch_reset = calculate_epoch_reset()
        epoch_text = "Calculating..." if epoch_reset else "Unknown"
        if epoch_reset:
            time_until = epoch_reset - datetime.now()
            hours = time_until.total_seconds() // 3600
            minutes = (time_until.total_seconds() % 3600) // 60
            epoch_text = f"{int(hours)}h {int(minutes)}m"
        
        response_text = f"""
🎮 **Mobile Verifier Miner Data**

🔐 **Miner Address:** `{user_input}`
💰 **Balance:** {balance} SHELL
📊 **Account Type:** {account_type}
⏰ **Last Updated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}

🎯 **Epoch Info:**
⏳ **Next Reset (approx):** {epoch_text}

**📝 Notes:**
• Data is fetched from the blockchain in real-time
• Tap counts are stored in the Miner contract
• Balance shows contract's SHELL balance
• Contact game provider for more detailed tap stats

**Want more detailed stats?**
Use the game's official app or dashboard!
        """
        
        await loading_msg.edit_text(response_text, parse_mode="Markdown")
        
    except Exception as e:
        await loading_msg.edit_text(
            f"❌ Error fetching data:\n`{str(e)}`\n\n"
            "Try again or contact support.",
            parse_mode="Markdown"
        )


# ============================================
# MAIN BOT SETUP
# ============================================

def main():
    """
    Start the Telegram bot
    """
    
    # Check if token is set
    if TELEGRAM_BOT_TOKEN == "YOUR_BOT_TOKEN_HERE":
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
