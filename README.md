# Dhoby's Personal Assistant

An AI-powered personal assistant built with Streamlit and PydanticAI that helps schedule meetings and send emails using natural language.

## Overview

This project is a conversational AI assistant that understands natural language instructions to:

- **Schedule Meetings**: Extract meeting details from natural language and automatically create calendar events on Google Calendar with Google Meet links
- **Send Emails**: Draft and send professional emails through Gmail
- **Conversational Confirmation**: Paraphrase and confirm meeting or email details back to the user

The assistant uses PydanticAI with the Minimax M2.5 model (via OpenRouter) to understand user intents and extract structured data for meeting and email operations.

## Features

- 🤖 **Natural Language Processing**: Understand meeting and email requests in conversational language
- 📅 **Google Calendar Integration**: Automatically create meetings with calendar invites and Google Meet links
- 📧 **Gmail Integration**: Send professionally formatted emails with automatic signature
- 💬 **Streamlit UI**: Clean, interactive chat interface
- 🔐 **Secure Authentication**: OAuth2-based Google authentication, SMTP credentials via environment variables

## Prerequisites

- Python 3.13+
- Google Account with:
  - Google Calendar API enabled
  - Google Meet enabled
- Gmail Account with App Passwords enabled
- OpenRouter API Key

## Project Setup

### 1. Clone and Install Dependencies

```bash
# Install dependencies
uv venv
uv sync
```

### 2. Google Authentication Setup

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project
3. Enable the **Google Calendar API**
4. Create an OAuth 2.0 Desktop Client ID
5. Download the credentials JSON file and save it as `credentials.json` in the project root

### 3. Gmail Setup

1. Enable 2-Factor Authentication on your Gmail account
2. Generate an App Password at [Google Account Security](https://myaccount.google.com/apppasswords)
3. Create a `.env` file in the project root with:

```env
SMTP_EMAIL=your-email@gmail.com
SMTP_APP_KEY=your-app-key
```

### 4. OpenRouter or OpenAI API Setup

Add your OpenRouter API key to your shell profile:

```bash
# Add to ~/.zprofile (or ~/.zshrc)
export OPENROUTER_API_KEY=your-openrouter-api-key
export OPENAI_API_KEY=your-openai-api-key
```

Then reload your shell:
```bash
source ~/.zprofile
```

Or export it directly in your terminal:
```bash
export OPENROUTER_API_KEY=your-openrouter-api-key
export OPENAI_API_KEY=your-openai-api-key
```

### 5. Run the Application

```bash
streamlit run main.py
```

The app will open in your browser at `http://localhost:8501`ƒ

## Project Structure

```
.
├── main.py                 # Streamlit UI and main application
├── pydantic_agent.py       # AI agent configuration and tool functions
├── credentials.json        # Google OAuth credentials (auto-generated)
├── pyproject.toml          # Project dependencies
├── .env                    # Environment variables (create this)
└── archive/                # Previous versions and experiments
```

## How It Works

### User Interaction Flow

1. User enters a request in natural language:
   - "Schedule a meeting with john@example.com at 2pm tomorrow about project updates for 30 minutes"
   - "Send an email to alice@company.com asking for a status update on the Q1 report"

2. The AI agent processes the request and structures it into one of three outputs:
   - `MeetingDetails`: Meeting information to create a calendar event
   - `EmailDetails`: Email information to send
   - `str`: General responses or confirmations

3. If a meeting or email is created, the app:
   - Calls the appropriate function (set_meeting or send_email)
   - Gets feedback on success/failure
   - Sends confirmation back to the user

### Agent Capabilities

The assistant can:
- ✅ Extract recipient email, title, agenda, time, and duration for meetings
- ✅ Extract recipient email, subject, and content for emails
- ✅ Automatically format emails professionally with signature
- ✅ Ask for clarification if required information is missing
- ❌ Refuses to perform unrelated tasks (by design for safety)

## Environment Variables

### In `.env` file (project root):

| Variable | Description |
|----------|-------------|
| `SMTP_EMAIL` | Gmail email address for sending emails |
| `SMTP_APP_KEY` | Gmail App Password (not your regular password) |

### In shell profile (`~/.zprofile` or `~/.zshrc`):

| Variable | Description |
|----------|-------------|
| `OPENROUTER_API_KEY` | API key from [OpenRouter](https://openrouter.ai/) |

## Configuration

- **AI Model**: Minimax M2.5 via OpenRouter (`openrouter:minimax/minimax-m2.5`)
- **Calendar Timezone**: Asia/Manila (configured in `pydantic_agent.py`)
- **Output Types**: `EmailDetails | MeetingDetails | str`

To change the timezone, update the `ZoneInfo("Asia/Manila")` in `pydantic_agent.py`

## Troubleshooting

### "Failed to authenticate with Google"
- Ensure `credentials.json` is in the project root
- Delete `credentials.json` and re-authenticate if the token expires

### "Failed to send email"
- Check that 2FA is enabled on the Gmail account
- Verify the App Password is correct in `.env`
- Ensure SMTP_EMAIL matches the Gmail account

### "Meeting creation failed"
- Verify Google Calendar API is enabled
- Check that the meeting time is in the future
- Ensure recipient email is valid

## Notes

- The first run will open a browser for Google OAuth authentication
- Credentials are cached locally and refreshed automatically
- SMTP connection is established once when the module loads
- All timestamps are stored in Asia/Manila timezone

---

Built with ❤️ using PydanticAI and Streamlit
