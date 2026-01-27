# UniControl Telegram Bot

Telegram bot for UniControl attendance system. Sends real-time attendance updates to Telegram groups.

## Features

- 🔍 **Group Search**: Students and group leaders can search for their group
- 📋 **Group Subscription**: Subscribe Telegram groups to receive attendance updates
- 📊 **Attendance Notifications**: Real-time attendance updates sent to groups
- 👤 **Personal Status**: Individual students can check their attendance

## Setup

### 1. Create Telegram Bot

1. Open [@BotFather](https://t.me/BotFather) in Telegram
2. Send `/newbot` and follow instructions
3. Copy the bot token

### 2. Environment Configuration

Create `.env` file:

```env
BOT_TOKEN=your_bot_token_here
API_BASE_URL=http://localhost:8000
API_KEY=your_api_key_here
DATABASE_URL=sqlite+aiosqlite:///./bot.db
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Run Bot

```bash
python -m bot
```

## Commands

- `/start` - Start bot and get instructions
- `/search <group_code>` - Search for a group (e.g., `/search KI_25-09`)
- `/subscribe <group_code>` - Subscribe current chat to group attendance
- `/unsubscribe` - Unsubscribe from attendance updates
- `/attendance` - Get today's attendance for subscribed group
- `/mystatus` - Check your personal attendance (after registration)
- `/help` - Show help message

## How It Works

1. **Group Leaders/Students** add the bot to their Telegram group
2. Use `/search KI_25-09` to find their academic group
3. Use `/subscribe KI_25-09` to link Telegram group with academic group
4. Bot automatically sends attendance updates when:
   - Student arrives late
   - Student is absent
   - Student arrives on time
   - Any attendance status changes

## Attendance Message Format

```
📋 Davomat yangilandi - KI_25-09

👤 Xurshidbek Xasanboyev
📅 2024-01-26 | 1-para
⏰ Holat: Kech qoldi
📝 Sabab: Transport muammosi

━━━━━━━━━━━━━━━━━━
```

## Docker

```bash
docker build -t unicontrol-bot .
docker run -d --env-file .env unicontrol-bot
```

## Architecture

```
unicontrol-bot/
├── bot/
│   ├── __init__.py
│   ├── __main__.py
│   ├── config.py
│   ├── database/
│   │   ├── __init__.py
│   │   ├── base.py
│   │   └── models.py
│   ├── handlers/
│   │   ├── __init__.py
│   │   ├── start.py
│   │   ├── search.py
│   │   ├── subscribe.py
│   │   └── attendance.py
│   ├── services/
│   │   ├── __init__.py
│   │   ├── api_client.py
│   │   └── attendance_formatter.py
│   ├── keyboards/
│   │   ├── __init__.py
│   │   └── inline.py
│   └── middlewares/
│       ├── __init__.py
│       └── throttling.py
└── requirements.txt
```
