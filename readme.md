# TeraBox Referral Automator: Automated Referral Registration Bot with Live Dashboard

[![Docker Image](https://img.shields.io/badge/Docker_Hub-mehakxsandhu%2Fterabox--referral--bot-blue?logo=docker&logoColor=white)](https://hub.docker.com/r/mehakxsandhu/terabox-referral-bot)
[![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://www.python.org/)
[![Playwright](https://img.shields.io/badge/Playwright-Browser_Automation-green.svg)](https://playwright.dev/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Educational](https://img.shields.io/badge/Purpose-Educational_Only-red.svg)](#%EF%B8%8F-disclaimer)

A fully automated TeraBox referral registration bot with a **real-time web dashboard**, **live log streaming**, **Docker Hub integration**, and **multi-link support**. Built with Playwright for browser automation and a custom Python dashboard server. Runs locally or in the cloud (Render, Docker, VPS).

> **⚠️ DISCLAIMER: This project is for educational and research purposes only. See [Disclaimer](#%EF%B8%8F-disclaimer).**

---

## 📑 Table of Contents
- [✨ Features](#-features)
- [🖥️ Dashboard Preview](#️-dashboard-preview)
- [🐳 Docker & Cloud Integrations](#-docker--cloud-integrations)
- [🚀 Quick Start](#-quick-start)
- [📁 Project Structure](#-project-structure)
- [⚙️ Configuration](#️-configuration)
- [🔌 Dashboard API](#-dashboard-api)
- [🔄 How It Works](#-how-it-works)
- [🧪 Troubleshooting](#-troubleshooting)
- [🤝 Contributing](#-contributing)
- [☕ Support](#-support)
- [⚠️ Disclaimer](#️-disclaimer)
- [📄 License](#-license)

---

## ✨ Features

- **Fully automated registration** — navigates TeraBox, fills forms, handles email verification
- **Multi-link support** — process multiple referral URLs in sequence, one account per link
- **Continuous loop mode** — runs forever with configurable delays between links and rounds
- **Live controls & kill switch** — Resume, Pause, and Stop automation instantly from the dashboard
- **Real-time web dashboard** — clean, minimal dark UI with dynamic progress cards and live stats
- **Dynamic delay adjustment** — update link and round delays on the fly without restarting
- **Live log streaming** — real-time automation console logs streamed directly to the web dashboard
- **Dashboard link management** — add/remove referral URLs directly from the UI
- **Smart email provider fallback** — tries 1secmail first with automatic rate-limit delay, falls back to Mail.tm
- **Robust verification code extraction** — extracts 4-digit code from email subject line
- **3-attempt retry logic** — retries verification code on failure with automatic resend
- **Multi-strategy button clicking** — text match → CSS selector → JavaScript DOM click fallbacks
- **Post-click verification** — confirms each step actually worked before proceeding
- **1-Click Docker & Docker Hub** — pre-built Docker image `mehakxsandhu/terabox-referral-bot` with GitHub Actions auto-build
- **Render Cloud Ready** — includes `render.yaml` blueprint and RAM optimizations for free cloud hosting

---

## 🖥️ Dashboard Preview

The dashboard provides a clean, minimal interface for monitoring and controlling automation runs:

| Section | Description |
|---|---|
| **Control Bar** | Resume, Pause, and Stop (Kill Switch) buttons, plus live delay inputs |
| **Stats Cards** | Total processed, successful, errors, and real-time success rate |
| **Progress Bar** | Visual progress indicator of current processing round |
| **Referral Links** | Interactive panel to add/remove target referral links |
| **Results Table** | Per-link execution status with timestamp and generated email |
| **Live Logs** | Real-time console terminal streaming automation engine events |

---

## 🐳 Docker & Cloud Integrations

### 1. Pre-built Docker Hub Image
The image is automatically built and pushed on every GitHub commit to Docker Hub:
```bash
docker pull mehakxsandhu/terabox-referral-bot:latest
```

### 2. 1-Click Run Command
```bash
docker run -d -p 8080:7860 --name terabox-bot mehakxsandhu/terabox-referral-bot:latest
```

### 3. Docker Compose
```bash
docker compose up -d
```

### 4. Render Cloud Hosting
Includes a `render.yaml` Blueprint specification for deploying to Render's free tier with automated port configuration and memory limits.

---

## 🚀 Quick Start

**Prerequisites:** Docker OR Python 3.10+ & Git

### 🐳 Docker Setup (Fastest)

```bash
# Option A: Run directly from Docker Hub
docker run -d -p 8080:7860 --name terabox-bot mehakxsandhu/terabox-referral-bot:latest

# Option B: Run with Docker Compose
git clone https://github.com/mehaksandhudev/terabox-referral-bot.git
cd terabox-referral-bot
docker compose up -d
```
**Open http://localhost:8080** to view your dashboard.

---

### 💻 Manual Python Setup

```bash
# 1. Clone repository
git clone https://github.com/mehaksandhudev/terabox-referral-bot.git
cd terabox-referral-bot

# 2. Create virtual environment
python -m venv venv
.\venv\Scripts\activate        # Windows
# source venv/bin/activate     # macOS/Linux

# 3. Install dependencies
pip install -r requirements.txt
playwright install chromium

# 4. Add your referral link
echo https://your-terabox-referral-link > referral_links.txt

# 5. Start dashboard (Terminal 1)
python dashboard.py

# 6. Start automation engine (Terminal 2)
python terabox_automator.py
```

**Open http://localhost:8080** to see the dashboard.

---

## 📁 Project Structure

```
terabox-referral-bot/
├── .github/workflows/
│   └── docker-image.yml   # GitHub Actions: Auto-build & push to Docker Hub
├── terabox_automator.py   # Main automation engine (Playwright + email handling)
├── dashboard.py           # Web dashboard server (stats + logs + link management)
├── referral_links.txt     # Referral URLs (one per line, editable via dashboard)
├── Dockerfile             # Docker container configuration
├── docker-compose.yml     # Docker Compose orchestration file
├── render.yaml            # Render Cloud Blueprint setup
├── requirements.txt       # Python dependencies (pinned for stability)
├── start.sh               # Container entrypoint script
├── stats.json             # Auto-generated: real-time stats for dashboard
├── control.json           # Auto-generated: dashboard control states
├── logs.json              # Auto-generated: log entries for dashboard
├── SETUP.md               # Detailed setup instructions
├── README.md              # Documentation
├── .gitignore             # Git ignore rules
└── LICENSE                # MIT License
```

---

## ⚙️ Configuration

Environment variables can be set locally, in Docker, or on Render:

| Variable | Default | Description |
|---|---|---|
| `PORT` | `7860` / `8080` | Port for the Web Dashboard server |
| `EMAIL_PROVIDER` | `1secmail` | Primary email provider (`1secmail` or `mailtm`) |
| `DELAY_SECONDS` | `15` | Delay between processing each link (seconds) |
| `ROUND_DELAY` | `30` | Delay between rounds in continuous mode (seconds) |

---

## 🔌 Dashboard API

The dashboard server provides REST API endpoints for external integrations:

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/` | Main dashboard web interface |
| `GET` | `/api/stats` | Retrieve current automation statistics (JSON) |
| `POST` | `/api/control` | Send Resume/Pause/Stop commands & update delays |
| `GET` | `/api/links` | List all configured referral links |
| `POST` | `/api/links` | Add a new referral link `{"url": "..."}` |
| `DELETE` | `/api/links` | Remove a link `{"index": 0}` or clear all |
| `GET` | `/api/logs` | Retrieve live log stream entries |

---

## 🔄 How It Works

```
┌─────────────────┐     ┌──────────────────┐     ┌─────────────────┐
│  Dashboard UI   │────▶│  referral_links   │◀────│  Automator      │
│  (localhost:8080)│     │  .txt             │     │  (Playwright)   │
│                 │     └──────────────────┘     │                 │
│  - Add/Remove   │                              │  For each link:  │
│    links        │     ┌──────────────────┐     │  1. Create email │
│  - Pause/Resume │◀────│  stats & control │◀────│  2. Open browser │
│  - Live logs    │     │  .json           │     │  3. Navigate URL │
└─────────────────┘     └──────────────────┘     │  4. Sign up      │
                                                 │  5. Verify code  │
                                                 │  6. Complete reg │
                                                 └─────────────────┘
```

---

## 🧪 Troubleshooting

| Issue | Solution |
|---|---|
| `Playwright binary mismatch` | Use pre-built Docker image or run `playwright install chromium` |
| `Mail.tm 429 Too Many Requests` | Handled automatically with rate-limit backoff delay |
| `Render Web Service crash` | Ensure memory flags `--no-sandbox --disable-dev-shm-usage` are enabled |
| `Dashboard not updating` | Verify both `dashboard.py` and `terabox_automator.py` are active |

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
> This tool was built to learn about browser automation, temporary email API integrations, Docker containerization, and web dashboards.
>
> **Do NOT use this tool to violate any website's Terms of Service.** The authors take no responsibility for misuse of this software.

---

## 📄 License

This project is licensed under the MIT License — see the [LICENSE](LICENSE) file for details.

---

<p align="center">
  Built with ❤️ by <a href="https://github.com/mehaksandhudev">mehaksandhudev</a>
</p>mer

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