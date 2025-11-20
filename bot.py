import os
import logging
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import Application, MessageHandler, filters, ContextTypes

# Load environment variables from .env file
load_dotenv()

# Configuration
BOT_TOKEN = os.getenv("BOT_TOKEN")
CHANNEL_SOURCE_ID = os.getenv("CHANNEL_SOURCE_ID")
CHANNEL_TARGET_ID = os.getenv("CHANNEL_TARGET_ID")
OWNER_ID = int(os.getenv("OWNER_ID")) if os.getenv("OWNER_ID") else None

# Set up logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Global state for forwarding status
forwarding_active = True

# --- Utility Functions ---

def is_owner(user_id: int) -> bool:
    """Checks if the user ID matches the configured owner ID."""
    return user_id == OWNER_ID

async def send_owner_message(context: ContextTypes.DEFAULT_TYPE, text: str) -> None:
    """Sends a message to the owner's private chat."""
    if OWNER_ID:
        try:
            await context.bot.send_message(chat_id=OWNER_ID, text=text)
        except Exception as e:
            logger.error(f"Failed to send message to owner ID {OWNER_ID}. Error: {e}")

# --- Command Handlers ---

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Greets the user and provides basic instructions."""
    if update.effective_chat.type != 'private':
        return
        
    welcome_message = (
        "👋 Welcome to the Channel Copier Bot!\n\n"
        "I am running and ready to sync your channels.\n"
        "If you are the owner, you can use the following commands:\n"
        "• /status - Check the bot's configuration and forwarding status.\n"
        "• /start_forward - Activate the message copying.\n"
        "• /stop_forward - Pause the message copying.\n\n"
        "If you haven't received the initial permission check message, please ensure:\n"
        "1. Your Telegram User ID is correctly set as the OWNER_ID.\n"
        "2. The bot has been added to both channels with the correct permissions."
    )
    await update.message.reply_text(welcome_message)
    logger.info(f"User {update.effective_user.id} started the bot.")

async def start_forward_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Starts the message forwarding process."""
    global forwarding_active
    if not is_owner(update.effective_user.id):
        logger.warning(f"Unauthorized access attempt to /start_forward by user ID: {update.effective_user.id}")
        return

    if forwarding_active:
        await update.message.reply_text("✅ Forwarding is already active.")
    else:
        forwarding_active = True
        await update.message.reply_text("▶️ Forwarding started.")
        logger.info("Forwarding status set to ACTIVE by owner.")

async def stop_forward_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Pauses the message forwarding process."""
    global forwarding_active
    if not is_owner(update.effective_user.id):
        logger.warning(f"Unauthorized access attempt to /stop_forward by user ID: {update.effective_user.id}")
        return

    if not forwarding_active:
        await update.message.reply_text("⏸️ Forwarding is already paused.")
    else:
        forwarding_active = False
        await update.message.reply_text("⏸️ Forwarding paused.")
        logger.info("Forwarding status set to INACTIVE by owner.")

async def status_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Shows the current status of the bot."""
    if not is_owner(update.effective_user.id):
        logger.warning(f"Unauthorized access attempt to /status by user ID: {update.effective_user.id}")
        return

    status_text = (
        "🤖 **Channel Copier Bot Status**\n\n"
        f"**Source Channel ID:** `{CHANNEL_SOURCE_ID}`\n"
        f"**Target Channel ID:** `{CHANNEL_TARGET_ID}`\n"
        f"**Owner ID:** `{OWNER_ID}`\n"
        f"**Forwarding Status:** {'✅ ACTIVE' if forwarding_active else '⏸️ INACTIVE'}"
    )
    await update.message.reply_text(status_text, parse_mode='Markdown')
    logger.info("Status requested and sent to owner.")

async def check_permissions(application: Application) -> None:
    """
    Verifies the bot's permissions for the source and target channels.
    This is a crucial check to be run at startup.
    """
    logger.info("Starting permission check...")
    bot = application.bot
    
    # 1. Check Source Channel (Read permission)
    source_ok = False
    try:
        # get_chat_member is a good way to check if the bot is in the channel
        member = await bot.get_chat_member(chat_id=CHANNEL_SOURCE_ID, user_id=bot.id)
        if member.status in ['administrator', 'member']:
            source_ok = True
            logger.info(f"✅ Bot is a member of the source channel {CHANNEL_SOURCE_ID}.")
        else:
            logger.error(f"❌ Bot is not a member of the source channel {CHANNEL_SOURCE_ID}. Status: {member.status}")
            await send_owner_message(application.context, f"❌ **Permission Error:** Bot is not a member of the source channel `{CHANNEL_SOURCE_ID}`. Please add the bot to the channel.")
            
    except Exception as e:
        logger.error(f"❌ Failed to check source channel {CHANNEL_SOURCE_ID} permissions. Error: {e}")
        await send_owner_message(application.context, f"❌ **Permission Error:** Failed to check source channel `{CHANNEL_SOURCE_ID}`. Ensure the bot is added to the channel and the ID is correct. Error: `{e}`")

    # 2. Check Target Channel (Post permission)
    target_ok = False
    try:
        # get_chat_member is used to check if the bot is an admin with post rights
        member = await bot.get_chat_member(chat_id=CHANNEL_TARGET_ID, user_id=bot.id)
        if member.status == 'administrator' and member.can_post_messages:
            target_ok = True
            logger.info(f"✅ Bot has posting rights in the target channel {CHANNEL_TARGET_ID}.")
        elif member.status == 'administrator' and not member.can_post_messages:
            logger.error(f"❌ Bot is an admin in target channel {CHANNEL_TARGET_ID} but is missing 'Post messages' permission.")
            await send_owner_message(application.context, f"❌ **Permission Error:** Bot is an admin in target channel `{CHANNEL_TARGET_ID}` but is missing the 'Post messages' permission.")
        else:
            logger.error(f"❌ Bot is not an administrator in the target channel {CHANNEL_TARGET_ID}. Status: {member.status}")
            await send_owner_message(application.context, f"❌ **Permission Error:** Bot is not an administrator in the target channel `{CHANNEL_TARGET_ID}`. Please make the bot an administrator and grant it 'Post messages' permission.")

    except Exception as e:
        logger.error(f"❌ Failed to check target channel {CHANNEL_TARGET_ID} permissions. Error: {e}")
        await send_owner_message(application.context, f"❌ **Permission Error:** Failed to check target channel `{CHANNEL_TARGET_ID}`. Ensure the bot is an administrator with 'Post messages' permission. Error: `{e}`")

    if source_ok and target_ok:
        await send_owner_message(application.context, "✅ **All permissions verified!** The bot is ready to start forwarding messages.")
    else:
        await send_owner_message(application.context, "⚠️ **Startup Warning:** One or more critical permissions are missing. Forwarding may fail until permissions are corrected.")

# --- Error Handler ---

async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Log the error and send a message to the owner."""
    logger.error("Exception while handling an update:", exc_info=context.error)

    # Send a concise error message to the owner
    error_message = f"🔥 **Bot Error** 🔥\n\nAn error occurred while processing an update:\n`{context.error}`"
    
    # Try to get the update info for context
    if update:
        error_message += f"\n\n**Update Type:** `{type(update)}`"
        if isinstance(update, Update) and update.effective_chat:
            error_message += f"\n**Chat ID:** `{update.effective_chat.id}`"

    await send_owner_message(context, error_message)

# --- Main Logic ---

async def handle_channel_post(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Copies a channel post from the source channel to the target channel."""
    
    # 1. Check if forwarding is active
    if not forwarding_active:
        logger.info("Forwarding is currently paused. Ignoring message.")
        return

    # 2. Check if the message is from the source channel
    # Telegram channel IDs are typically negative integers.
    # We convert the string ID from .env to an integer for comparison.
    try:
        source_id_int = int(CHANNEL_SOURCE_ID)
    except (ValueError, TypeError):
        logger.error(f"Invalid CHANNEL_SOURCE_ID: {CHANNEL_SOURCE_ID}. Please check your .env file.")
        return

    if update.channel_post and update.channel_post.chat.id == source_id_int:
        message = update.channel_post
        
        # 3. Gracefully ignore unsupported message types (e.g., service messages)
        if not message.effective_message.text and not message.effective_message.caption and not message.effective_message.media_group_id and not message.effective_message.poll and not message.effective_message.location and not message.effective_message.contact and not message.effective_message.sticker:
            logger.info(f"Ignoring unsupported or empty message type from {message.chat.title} (ID: {message.chat.id}).")
            return

        logger.info(f"Received message ID {message.message_id} from source channel {message.chat.title}.")

        try:
            # 4. Use copy_message to send the message to the target channel
            # This ensures the "Forwarded from" tag is not present.
            # copy_message supports all required message types (text, photo, video, GIF, voice, audio, document, sticker, poll, location, contact).
            # Media groups (albums) are handled by the library automatically as a sequence of posts.
            
            # Note: copy_message requires the chat_id of the source and the message_id.
            await context.bot.copy_message(
                chat_id=CHANNEL_TARGET_ID,
                from_chat_id=CHANNEL_SOURCE_ID,
                message_id=message.message_id
            )
            logger.info(f"Successfully copied message ID {message.message_id} to target channel {CHANNEL_TARGET_ID}.")

        except Exception as e:
            # 5. Robust error handling for rate limits, permissions, etc.
            logger.error(f"Failed to copy message ID {message.message_id}. Error: {e}")
            
            # 5. Robust error handling for rate limits, permissions, etc.
            logger.error(f"Failed to copy message ID {message.message_id}. Error: {e}")
            
            # Send a notification to the owner about the failure
            error_message = f"🚨 **CRITICAL ERROR** 🚨\n\nFailed to copy message ID `{message.message_id}` from `{CHANNEL_SOURCE_ID}` to `{CHANNEL_TARGET_ID}`.\n\n**Error Details:**\n`{e}`"
            await send_owner_message(context, error_message)

    else:
        # Log other channel posts for transparency, but do not process them
        if update.channel_post:
            logger.debug(f"Ignoring channel post from non-source chat ID: {update.channel_post.chat.id}")
        elif update.message:
            logger.debug(f"Ignoring regular message from chat ID: {update.message.chat.id}")


def main() -> None:
    """Start the bot."""
    if not all([BOT_TOKEN, CHANNEL_SOURCE_ID, CHANNEL_TARGET_ID, OWNER_ID]):
        logger.error("One or more required environment variables (BOT_TOKEN, CHANNEL_SOURCE_ID, CHANNEL_TARGET_ID, OWNER_ID) are missing. Please check your .env file.")
        return

    # Create the Application and pass it your bot's token.
    application = Application.builder().token(BOT_TOKEN).build()

    # Register handlers
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("start_forward", start_forward_command))
    application.add_handler(CommandHandler("stop_forward", stop_forward_command))
    application.add_handler(CommandHandler("status", status_command))
    
    # Register the handler for all channel posts
    application.add_handler(MessageHandler(filters.ALL & filters.ChatType.CHANNEL, handle_channel_post))

    # Register the error handler
    application.add_error_handler(error_handler)

    # Run the bot (using polling, as it's the simplest stable option for deployment)
    logger.info("Bot started. Running initial permission check...")
    
    # Run permission check asynchronously after the bot starts
    application.job_queue.run_once(lambda context: check_permissions(application), 1)

    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    main()
