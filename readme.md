# TeraBox Referral Automator: Automated Referral Registration Bot with Live Dashboard

[![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://www.python.org/)
[![Playwright](https://img.shields.io/badge/Playwright-Browser_Automation-green.svg)](https://playwright.dev/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Educational](https://img.shields.io/badge/Purpose-Educational_Only-red.svg)](#%EF%B8%8F-disclaimer)

A fully automated TeraBox referral registration bot with a **real-time web dashboard**, **live log streaming**, and **multi-link support**. Built with Playwright for browser automation and a custom Python dashboard server. No cloud services, no paid APIs, 100% local.

> **⚠️ DISCLAIMER: This project is for educational and research purposes only. See [Disclaimer](#%EF%B8%8F-disclaimer).**

---

## 📑 Table of Contents
- [✨ Features](#-features)
- [🖥️ Dashboard Preview](#️-dashboard-preview)
- [🚀 Quick Start](#-quick-start)
- [📁 Project Structure](#-project-structure)
- [⚙️ Configuration](#️-configuration)
- [🔌 Dashboard API](#-dashboard-api)
- [🔄 How It Works](#-how-it-works)
- [🧪 Troubleshooting](#-troubleshooting)
- [🤝 Contributing](#-contributing)
- [⚠️ Disclaimer](#️-disclaimer)
- [📄 License](#-license)

---

## ✨ Features

- **Fully automated registration** — navigates TeraBox, fills forms, handles email verification
- **Multi-link support** — process multiple referral URLs in sequence, one account per link
- **Continuous loop mode** — runs forever with configurable delays
- **Live controls & configuration** — Resume, Pause, and Stop (Kill Switch) automation directly from the web dashboard
- **Real-time web dashboard** — clean, minimal dark UI at `localhost:8080` with live stats and logs
- **Dynamic delay adjustment** — configure the delay between links and rounds directly from the dashboard UI in real-time
- **Live log streaming** — all automation logs streamed to dashboard in real-time
- **Dashboard link management** — add/remove referral URLs from the web UI, no code touching
- **Smart email provider fallback** — tries 1secmail first, falls back to Mail.tm automatically
- **Robust verification code extraction** — extracts 4-digit code from email subject line
- **3-attempt retry logic** — retries verification code on failure with automatic resend
- **Multi-strategy button clicking** — text match → CSS selector → JavaScript DOM click fallbacks
- **Post-click verification** — confirms each step actually worked before proceeding
- **Stats tracking** — success/error/total counts saved to `stats.json` in real-time
- **Optional LLM vision fallback** — uses Gemini API to find UI elements if selectors fail

---

## 🖥️ Dashboard Preview

The dashboard provides a clean, minimal interface for monitoring and controlling automation runs:

| Section | Description |
|---|---|
| **Control Bar** | Resume, Pause, and Stop (Kill Switch) buttons, and input fields to configure link & round delays on the fly |
| **Stats Cards** | Total processed, successful, errors, and success rate |
| **Progress Bar** | Visual progress of current round |
| **Referral Links** | Add/remove URLs directly from the UI |
| **Results Table** | Per-link status with email used, timestamp |
| **Live Logs** | Real-time log stream from the automation engine |

---

## 🚀 Quick Start

**Prerequisites:** Python 3.10+, Git

```bash
# 1. Clone the repository
git clone https://github.com/mehaksandhudev/terabox-referral-bot.git
cd terabox-referral-bot

# 2. Follow the setup guide
# See SETUP.md for detailed step-by-step instructions
```

### 🐳 1-Click Docker Setup (Recommended)

Run the entire application (Dashboard + Automation Engine) with a single command using Docker:

```bash
docker compose up -d --build
```
Or using plain Docker:
```bash
docker build -t terabox-bot .
docker run -d -p 8080:7860 --name terabox-bot terabox-bot
```
**Open http://localhost:8080** to see your live dashboard!

---

### 💻 Manual Setup

```bash
# Create virtual environment
python -m venv venv
.\venv\Scripts\activate        # Windows
# source venv/bin/activate     # macOS/Linux

# Install dependencies
pip install -r requirements.txt
playwright install chromium

# Add your referral link
echo https://your-terabox-referral-link > referral_links.txt

# Start dashboard (Terminal 1)
python dashboard.py

# Start automation (Terminal 2)
python terabox_automator.py
```

**Open http://localhost:8080** to see the dashboard.

---

## 📁 Project Structure

```
terabox-referral-bot/
├── terabox_automator.py   # Main automation engine (Playwright + email handling)
├── dashboard.py           # Web dashboard server (stats + logs + link management)
├── referral_links.txt     # Referral URLs (one per line, editable via dashboard)
├── stats.json             # Auto-generated: real-time stats for dashboard
├── logs.json              # Auto-generated: log entries for dashboard
├── SETUP.md               # Detailed setup instructions
├── README.md              # This file
├── .gitignore             # Git ignore rules
└── LICENSE                # MIT License
```

---

## ⚙️ Configuration

All configuration is done via **environment variables** (optional):

| Variable | Default | Description |
|---|---|---|
| `EMAIL_PROVIDER` | `1secmail` | Email provider: `1secmail` or `mailtm` |
| `DELAY_SECONDS` | `15` | Delay between processing each link (seconds) |
| `ROUND_DELAY` | `30` | Delay between rounds in continuous mode (seconds) |
| `GEMINI_API_KEY` | *(none)* | Optional: Google Gemini API key for LLM vision fallback |

**Example:**
```bash
set DELAY_SECONDS=10
set ROUND_DELAY=60
python terabox_automator.py
```

---

## 🔌 Dashboard API

The dashboard exposes REST endpoints for programmatic access:

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/` | Dashboard web UI |
| `GET` | `/api/stats` | Current automation stats (JSON) |
| `GET` | `/api/links` | List all referral links |
| `POST` | `/api/links` | Add a referral link `{"url": "..."}` |
| `DELETE` | `/api/links` | Remove a link `{"index": 0}` or `{"clear_all": true}` |
| `GET` | `/api/logs` | Live log entries (JSON) |

---

## 🔄 How It Works

```
┌─────────────────┐     ┌──────────────────┐     ┌─────────────────┐
│  Dashboard UI   │────▶│  referral_links   │◀────│  Automator      │
│  (localhost:8080)│     │  .txt             │     │  (Playwright)   │
│                 │     └──────────────────┘     │                 │
│  - Add/Remove   │                              │  For each link:  │
│    links        │     ┌──────────────────┐     │  1. Create email │
│  - View stats   │◀────│  stats.json       │◀────│  2. Open browser │
│  - Live logs    │     └──────────────────┘     │  3. Navigate URL │
│                 │     ┌──────────────────┐     │  4. Sign up      │
│                 │◀────│  logs.json        │◀────│  5. Verify code  │
│                 │     └──────────────────┘     │  6. Complete reg │
└─────────────────┘                              └─────────────────┘
                                                        │
                                                        ▼
                                                  Wait 30s, repeat
```

**Registration flow per link:**
1. Create a temporary email account (1secmail → Mail.tm fallback)
2. Launch headless Chromium via Playwright
3. Navigate to referral URL → Click Login → Sign up → Email option
4. Fill email → Click Continue (3-strategy fallback)
5. Retrieve verification code from email subject line
6. Fill code with retry logic (3 attempts, auto-resend)
7. Set password → Submit → Account created
8. Save result to `stats.json` → Next link

---

## 🧪 Troubleshooting

| Issue | Solution |
|---|---|
| `ModuleNotFoundError: nest_asyncio` | Activate venv: `.\venv\Scripts\activate` |
| `1secmail 403 Forbidden` | Normal — falls back to Mail.tm automatically |
| Continue button not clicking | Fixed with 3-strategy fallback (text, CSS, JS) |
| Wrong verification code | Extracts from subject line, retries 3 times |
| Dashboard not updating | Check both scripts are running in separate terminals |
| `playwright install` fails | Run as admin: `playwright install chromium` |

---

## 🤝 Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

---

## ☕ Support

If this project helped you, consider buying me a coffee!

[![Buy Me A Coffee](https://img.shields.io/badge/Buy%20Me%20A%20Coffee-ffdd00?style=flat-square&logo=buy-me-a-coffee&logoColor=black)](https://buymeacoffee.com/mehaksandhudev)

---

## ⚠️ Disclaimer

> **This project is for EDUCATIONAL and RESEARCH purposes only.**
>
> This tool was built to learn about:
> - Browser automation with Playwright
> - Temporary email API integration
> - Real-time web dashboard development
> - Multi-strategy element detection in dynamic web apps
>
> **Do NOT use this tool to violate any website's Terms of Service.**
> The authors are not responsible for any misuse of this software.
> Use at your own risk and always respect the terms and conditions of any service you interact with.

---

## 📄 License

This project is licensed under the MIT License — see the [LICENSE](LICENSE) file for details.

---

<p align="center">
  Built with ❤️ by <a href="https://github.com/mehaksandhudev">mehaksandhudev</a>
</p>