# Telegram Channel Copier Bot

This is a reliable, zero-maintenance Telegram bot designed to automatically copy all messages from a source channel (Channel A) to a target channel (Channel B). It uses the `copyMessage` API to ensure that messages in the target channel appear as original posts, without the "Forwarded from..." tag.

## Features

*   **Automatic & Reliable Sync:** Keeps two channels perfectly in sync.
*   **Native Look:** Messages are copied using `copyMessage` to look like original posts.
*   **Full Message Type Support:** Handles text, photos, videos, GIFs, voice notes, audio, documents, stickers, polls, locations, contacts, and media groups (albums).
*   **Owner-Only Control:** Commands are restricted to a single configured owner ID.
*   **Permission Verification:** Checks bot's read/post permissions on startup and alerts the owner if issues are found.
*   **Graceful Error Handling:** Automatically retries and logs errors, notifying the owner of critical failures.

## Setup Instructions

### 1. Get Your Credentials

You will need four pieces of information to configure the bot:

| Credential | How to Get It |
| :--- | :--- |
| **BOT\_TOKEN** | Create a new bot by talking to **@BotFather** on Telegram. Use the `/newbot` command. |
| **CHANNEL\_SOURCE\_ID** | **Channel A (Source):** Add your bot as a member to this channel. The bot only needs to be a regular member to read messages. |
| **CHANNEL\_TARGET\_ID** | **Channel B (Target):** Add your bot as an **Administrator** to this channel and ensure the **"Post messages"** permission is enabled. |
| **OWNER\_ID** | Your personal Telegram User ID. Forward any message from yourself to **@userinfobot** and copy the `ID` number. |

### 2. Get Channel IDs

Telegram channel IDs are long negative numbers (e.g., `-1001234567890`).

1.  **For Public Channels:** You can use the channel's public username (e.g., `@my_public_channel`) as the ID.
2.  **For Private Channels:** You must use the numeric ID.
    *   Temporarily make the channel public, get the ID from a bot like **@get_id_bot**, then make it private again.
    *   Alternatively, use the numeric ID format: `-100` followed by the channel's unique ID.

### 3. Configuration

1.  Clone this repository or download the files.
2.  Edit the included `.env` file and replace the placeholder values with your actual credentials:

    ```ini
    # --- Telegram Channel Copier Bot Configuration ---
    
    BOT_TOKEN="YOUR_BOT_TOKEN_HERE"
    CHANNEL_SOURCE_ID="-1001234567890"
    CHANNEL_TARGET_ID="-1000987654321"
    OWNER_ID="123456789"
    ```

## How to Run

### 1. Install Dependencies

The bot requires Python 3.8+ and the packages listed in `requirements.txt`.

```bash
# It is highly recommended to use a virtual environment
python3 -m venv venv
source venv/bin/activate

# Install the required libraries
pip install -r requirements.txt
```

### 2. Start the Bot

Run the main script:

```bash
python bot.py
```

The bot will start, perform a permission check, and send a confirmation message to your `OWNER_ID` chat. It will then begin listening for new messages in the source channel.

## Control Commands (Owner Only)

These commands can only be used by the user whose ID is set in `OWNER_ID`.

| Command | Description |
| :--- | :--- |
| `/start_forward` | Starts the message syncing process. |
| `/stop_forward` | Pauses the message syncing process. |
| `/status` | Shows the current configuration and forwarding status (Active/Inactive). |

## Stability and Reliability

The bot is designed for stability:

*   **Error Handling:** Includes a global error handler that logs exceptions and notifies the owner.
*   **Retry Mechanism:** The underlying `python-telegram-bot` library automatically handles connection issues and retries, ensuring high reliability.
*   **Graceful Failure:** Unsupported messages or deleted messages are logged and ignored, preventing crashes.
*   **Polling:** Uses long-polling, which is a simple and stable method for deployment on platforms like Render or Railway.

## Deployment (Render / Railway)

This bot is designed to be easily deployed on cloud platforms like Render or Railway. Since it uses long-polling, you will need to ensure your platform supports long-running background processes.

### 1. Prepare Your Project

1.  Ensure your `.env` file is complete with all four required values.
2.  Make sure your `requirements.txt` is up-to-date (it should be if you followed the setup).

### 2. Configure Environment Variables

Instead of relying on the `.env` file, it is best practice to configure your secrets directly in the hosting platform's environment settings.

| Variable Name | Value |
| :--- | :--- |
| `BOT_TOKEN` | Your Telegram Bot Token |
| `CHANNEL_SOURCE_ID` | Channel A ID |
| `CHANNEL_TARGET_ID` | Channel B ID |
| `OWNER_ID` | Your Telegram User ID |

### 3. Deployment Steps

#### For Render

1.  **New Web Service:** Create a new **Web Service** (not a Static Site).
2.  **Connect Repository:** Connect your GitHub repository (after pushing the code).
3.  **Environment:** Select **Python**.
4.  **Build Command:** `pip install -r requirements.txt`
5.  **Start Command:** `python bot.py`
6.  **Environment Variables:** Add the four variables listed above in the "Environment" section.
7.  **Service Type:** Choose a service type that supports background workers (e.g., a paid tier Web Service or a **Background Worker** if available).

#### For Railway

1.  **New Project:** Create a new project and connect your GitHub repository.
2.  **Environment:** Railway will automatically detect the Python project.
3.  **Variables:** Go to the "Variables" tab and add the four environment variables listed above.
4.  **Start Command:** Railway usually detects the start command, but if not, set it to `python bot.py`.
5.  **Service Type:** Railway's default setup should work for this type of application.

**Important Note on Polling:** Since this bot uses long-polling, it runs as a single, continuous process. Ensure your chosen hosting plan supports this type of background worker and is configured not to sleep or shut down due to inactivity.
