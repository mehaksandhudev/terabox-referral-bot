# TeraBox Referral Automator: Automated Referral Registration Bot with Live Dashboard

[![Docker Image](https://img.shields.io/badge/Docker_Hub-mehakxsandhu%2Fterabox--referral--bot-blue?logo=docker&logoColor=white)](https://hub.docker.com/r/mehakxsandhu/terabox-referral-bot)
[![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://www.python.org/)
[![Playwright](https://img.shields.io/badge/Playwright-Browser_Automation-green.svg)](https://playwright.dev/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Educational](https://img.shields.io/badge/Purpose-Educational_Only-red.svg)](#%EF%B8%8F-disclaimer)

A fully automated TeraBox referral registration bot with a **real-time web dashboard**, **dynamic mobile IP rotation**, **automated password confirmation handling**, **credential storage**, and **multi-link support**. Built with Playwright for browser automation and a custom Python dashboard server. Runs locally or in the cloud (Render, Docker, VPS).

> **⚠️ DISCLAIMER: This project is for educational and research purposes only. See [Disclaimer](#%EF%B8%8F-disclaimer).**

---

## 📑 Table of Contents
- [✨ Features](#-features)
- [🖥️ Dashboard Preview](#️-dashboard-preview)
- [📱 Dynamic Mobile IP Rotation (Free & Unlimited)](#-dynamic-mobile-ip-rotation-free--unlimited)
- [🔐 Two-Field Password Entry & Credentials Saving](#-two-field-password-entry--credentials-saving)
- [🌐 ISP Blocking & VPN Guide (Jio / Airtel / India)](#-isp-blocking--vpn-guide-jio--airtel--india)
- [🐳 Docker & Cloud Integrations](#-docker--cloud-integrations)
- [🚀 Quick Start](#-quick-start)
- [🧪 Testing & Command Cheat Sheet](#-testing--command-cheat-sheet)
- [📁 Project Structure](#-project-structure)
- [⚙️ Configuration](#️-configuration)
- [🔌 Dashboard API](#-dashboard-api)
- [🔄 How It Works](#-how-it-works)
- [🛠️ Troubleshooting](#️-troubleshooting)
- [🤝 Contributing](#-contributing)
- [☕ Support](#-support)
- [⚠️ Disclaimer](#️-disclaimer)
- [📄 License](#-license)

---

## ✨ Features

- **Fully Automated Registration** — Navigates TeraBox referral landing pages, extracts verification codes from email subjects, and automates account creation end-to-end.
- **Two-Field Password & Confirmation Support** — Handles the updated TeraBox registration flow with both "Enter password" and "Confirm password" fields, followed by automated Enter/Submit.
- **Auto Credential Storage (`accounts.txt`)** — Automatically saves every created account with its email, password, public IP address, timestamp, and referral URL.
- **Dynamic Mobile IP Rotation via Android ADB** — Automatically toggles phone Airplane Mode between registrations to obtain a fresh cellular IP from your mobile carrier (Jio, Airtel, etc.) in ~8 seconds.
- **Self-Healing Network Stabilization & Retries** — Actively polls and verifies internet reachability after IP rotation and retries page navigation up to 3 times to prevent transient `ERR_CONNECTION_REFUSED` while USB tethering reconnects.
- **ADB Safety Lock** — Pauses automation immediately if the USB-tethered Android phone is unplugged or unreachable, ensuring the bot NEVER runs on your real home IP.
- **Direct `.txt` Referral Upload** — Upload `.txt` files containing referral URLs directly from the dashboard; built-in regex automatically parses and extracts every single valid link.
- **Real-Time Web Dashboard** — Dark-mode UI (Port 8080) displaying total processed, success/error metrics, live rate, delay sliders, and a full results table with Email, Password, and IP.
- **One-Click Clear Actions** — Purge old test results or clear live console logs directly from the dashboard header buttons.
- **Direct Accounts Download** — Download or view `accounts.txt` directly from the dashboard UI with one click.
- **Silent Background Boot Mode (`HEADLESS=true`)** — Automatically starts on Windows boot with zero intrusive browser windows popping up; monitor everything via the web dashboard.
- **Multi-Link Continuous Loop** — Cycles through multiple referral URLs in `referral_links.txt` with configurable delay intervals and kill switch.
- **Dual Email Providers** — Uses Mail.tm as primary with 1secmail fallback support.
- **Telegram Bot Integration** — Remotely monitor stats (`/stats`), pause/resume/stop automation, and add referral links via Telegram chat.

---

## 🖥️ Dashboard Preview

Access the live dashboard at **`http://localhost:8080`**:

| Section | Description |
|---|---|
| **Control Bar** | Resume, Pause, and Stop (Kill Switch) buttons, plus live delay inputs |
| **Stats Cards** | Total processed, successful, errors, and real-time success rate |
| **Progress Bar** | Visual indicator of current processing round |
| **Referral Links** | Interactive panel with live counter, URL input, and **"Upload .txt"** button |
| **Results Table** | Columns for `#`, `URL`, `Email`, `Password`, `IP`, `Status`, `Timestamp`, and **"Clear"** button |
| **Accounts Download** | Quick-action button to download `accounts.txt` directly from the browser |
| **Live Logs** | Bounded monospaced log stream with syntax-highlighted levels and **"Clear"** button |

---

## 📱 Dynamic Mobile IP Rotation (Free & Unlimited)

Instead of paying for expensive proxy services, the bot natively supports **Dynamic Mobile IP Rotation** using an Android smartphone connected via USB:

1. **How It Works**:
   - Mobile carriers (Jio, Airtel, Vi) use Carrier-Grade NAT (CGNAT).
   - Whenever Airplane Mode is toggled on mobile data, the cellular tower assigns a **brand new mobile IP address**.
2. **Automated ADB Integration**:
   - The bot communicates directly with the phone via Android Debug Bridge (`adb.exe`).
   - After each registration, it turns Airplane Mode ON for 3 seconds, turns it OFF, and waits 8 seconds for cellular data to reconnect.
   - The new IP is verified and recorded with the newly created account.
3. **Setup Requirements**:
   - Android phone with an active mobile data SIM.
   - Phone connected to PC via USB cable.
   - **USB Tethering** turned ON in phone settings.
   - **Wi-Fi** turned OFF on the phone.
   - **USB Debugging** enabled in Developer Options.

---

## 🔐 Two-Field Password Entry & Credentials Saving

TeraBox has updated its registration form to require both password entry and confirmation:
1. **Detection**: Automatically discovers multiple `input[type="password"]` and confirm-password placeholders.
2. **Filling**: Populates both fields with the generated secure password.
3. **Submission**: Dispatches a keyboard `Enter` stroke and triggers active submit buttons (`Sign up`, `Register`, `Submit`, `Continue`).
4. **Storage**: Every successful account is appended to `accounts.txt`:
   ```text
   user@uberip.com:Password123! | IP: 157.39.65.7 | Created: 2026-09-07 15:15:00 | Ref: https://1024terabox.com/s/...
   ```

---

## 🌐 ISP Blocking & VPN Guide (Jio / Airtel / India)

In India, telecom operators (Jio, Airtel, Vi) enforce regulatory blocks on `terabox.com` and its mirrors, causing `net::ERR_CONNECTION_TIMED_OUT` when accessed directly.

### Recommended Solutions:
- **Proton VPN (Recommended)**:
  - Turn ON Proton VPN on your PC before running the bot.
  - TeraBox loads instantly with zero timeouts.
  - You can switch VPN servers (Netherlands, Japan, Romania, USA) to rotate IPs.
- **Cloudflare WARP (1.1.1.1 with WARP)**:
  - Free and fast; bypasses Indian ISP blocklists without throttling speed.
- **Rotating Proxies**:
  - Add your proxy addresses into `proxies.txt` for automatic external routing.

---

## 🚀 Quick Start

### 1. Prerequisites
- Windows 10/11, macOS, or Linux
- Python 3.10+
- Chrome/Chromium (installed automatically via Playwright)

### 2. Installation
```powershell
# Clone repository
git clone https://github.com/mehaksandhudev/terabox-referral-bot.git
cd terabox-referral-bot

# Create and activate virtual environment
python -m venv venv
.\venv\Scripts\activate        # Windows
# source venv/bin/activate     # macOS / Linux

# Install dependencies
pip install -r requirements.txt
playwright install chromium
```

### 3. Add Your Referral Links
Add your links to `referral_links.txt` (one per line):
```text
https://1024terabox.com/s/YOUR_REFERRAL_CODE
```

### 4. Run the Bot
- **Full Automation with Dashboard (Auto-Restart)**:
  ```powershell
  .\start_automator.bat
  ```
  *Opens the dashboard at `http://localhost:8080` and runs the bot.*

- **Add to Windows Boot (Runs Silently in Headless Mode on Startup)**:
  Double-click `add_to_startup.bat`.

---

## 🧪 Testing & Command Cheat Sheet

Here are all the commands to test and verify every component individually:

### 1. Test a Single Registration (Live Browser GUI)
Runs 1 referral link, opens Chrome visibly on screen, fills passwords, captures the new page, and saves credentials:
```powershell
.\venv\Scripts\python.exe test_single_run.py
```

### 2. Test ADB Phone Connection
Check if your Android phone is detected and authorized for IP rotation:
```powershell
& "$env:LOCALAPPDATA\Android\Sdk\platform-tools\adb.exe" devices
```
*(Should output `List of devices attached` followed by your device ID and `device`)*

### 3. Test Mobile IP Rotation Manually
Test toggling Airplane mode on your phone and verifying that a new public IP is obtained:
```powershell
.\venv\Scripts\python.exe -c "import subprocess, time, requests; adb=r'$env:LOCALAPPDATA\Android\Sdk\platform-tools\adb.exe'; print('Current IP:', requests.get('https://api.ipify.org?format=json').json()['ip']); subprocess.run([adb, 'shell', 'cmd', 'connectivity', 'airplane-mode', 'enable']); time.sleep(3); subprocess.run([adb, 'shell', 'cmd', 'connectivity', 'airplane-mode', 'disable']); time.sleep(8); print('New Rotated IP:', requests.get('https://api.ipify.org?format=json').json()['ip'])"
```

### 4. Test TeraBox Network Reachability
Verify if TeraBox is reachable on your current network or VPN:
```powershell
.\venv\Scripts\python.exe -c "import requests; print('Status:', requests.get('https://1024terabox.com', timeout=8).status_code)"
```

### 5. Run the Dashboard Server Only
```powershell
.\venv\Scripts\python.exe dashboard.py
```
*(Open http://localhost:8080)*

### 6. Run the Automator Directly in GUI Mode (Visible Chrome)
```powershell
$env:HEADLESS="false"
.\venv\Scripts\python.exe terabox_automator.py
```

### 7. Run the Automator Directly in Headless Mode (Invisible Chrome)
```powershell
$env:HEADLESS="true"
.\venv\Scripts\python.exe terabox_automator.py
```

### 8. View Saved Account Credentials
```powershell
Get-Content accounts.txt
```

---

## 📁 Project Structure

```
terabox-referral-bot/
├── terabox_automator.py       # Core automation engine (Playwright, email, IP rotation)
├── dashboard.py               # Local web dashboard server (Port 8080) + Telegram bot
├── test_single_run.py         # Standalone single-link test runner
├── start_automator.bat        # Windows auto-restart launcher with dashboard
├── add_to_startup.bat         # Installs bot into Windows Startup folder
├── referral_links.txt         # List of target referral URLs
├── accounts.txt               # Saved credentials (email:password | IP | Timestamp)
├── after_password_popup.png   # Screenshot captured after password submission
├── stats.json                 # Real-time metrics and run results
├── control.json               # Real-time bot controls (pause/resume/stop/delays)
├── logs.json                  # Live log entries streamed to dashboard
├── requirements.txt           # Python dependencies
├── Dockerfile                 # Docker container specification
├── docker-compose.yml         # Docker orchestration
├── render.yaml                # Render Cloud Blueprint
├── SETUP.md                   # Comprehensive step-by-step setup guide
├── README.md                  # Project documentation
└── LICENSE                    # MIT License
```

---

## ⚙️ Configuration

Settings can be managed via environment variables or directly inside `control.json` / Web Dashboard:

| Variable | Default | Description |
|---|---|---|
| `HEADLESS` | `true` (in bat) / `false` | Run browser in headless (invisible) or GUI mode |
| `EMAIL_PROVIDER` | `mailtm` | Primary email provider (`mailtm` or `1secmail`) |
| `PORT` | `8080` | Port for the web dashboard |
| `DELAY_SECONDS` | `15` | Delay between each referral link (seconds) |
| `ROUND_DELAY` | `30` | Delay between full rounds (seconds) |
| `TELEGRAM_TOKEN` | `""` | Telegram Bot API token for remote monitoring |
| `TELEGRAM_CHAT_ID` | `""` | Allowed Telegram chat ID for remote control |

---

## 🔌 Dashboard API

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/` | Web dashboard interface |
| `GET` | `/api/stats` | Current stats JSON (`total`, `success`, `errors`, `results`) |
| `DELETE` | `/api/stats` | Clear past results from dashboard and stats.json |
| `GET` | `/api/accounts` | Download or view `accounts.txt` directly |
| `POST` | `/api/control` | Send Pause / Resume / Stop commands & update delays |
| `GET` | `/api/links` | List all configured referral links |
| `POST` | `/api/links` | Add a single referral link `{"url": "..."}` |
| `POST` | `/api/links/bulk` | Bulk import referral links from text `{"links": ["..."]}` |
| `DELETE` | `/api/links` | Clear or remove referral links |
| `GET` | `/api/logs` | Real-time console log stream |
| `DELETE` | `/api/logs` | Clear in-memory console logs |

---

## 🛠️ Troubleshooting

| Issue | Cause | Solution |
|---|---|---|
| `net::ERR_CONNECTION_REFUSED` | Mobile IP just toggled & USB tethering route was reconnecting | Handled automatically! The bot polls for network stabilization and retries navigation up to 3 times. Ensure phone data is active. |
| `net::ERR_CONNECTION_TIMED_OUT` | Indian ISP block (Jio / Airtel) | Connect Proton VPN or Cloudflare WARP before running. |
| `Found 2 password input fields` | Normal behavior | TeraBox now requires Password + Confirm Password. The bot fills both automatically. |
| `No module named 'nest_asyncio'` | Virtual environment not active | Run `.\venv\Scripts\activate` before launching scripts. |
| `ADB device unauthorized` | Phone authorization prompt | Unlock phone and tap "Always allow from this computer" on the USB Debugging dialog. |
| `Mobile IP not changing` | Phone connected to Wi-Fi | Turn OFF Wi-Fi on the phone; ensure Mobile Data & USB Tethering are ON. |

---

## ☕ Support & Contributing

- **Pull Requests**: Contributions and bug fixes are welcome! Feel free to open an issue or PR.
- **Support**: If this project helped you, consider supporting via [PayPal](https://paypal.me/mhksandhu) or [Buy Me A Coffee](https://buymeacoffee.com/mehaksandhudev).

[![Donate with PayPal](https://img.shields.io/badge/Donate-PayPal-00457C?style=flat-square&logo=paypal&logoColor=white)](https://paypal.me/mhksandhu) [![Buy Me A Coffee](https://img.shields.io/badge/Buy%20Me%20A%20Coffee-☕-FFDD00?style=flat-square&logo=buymeacoffee&logoColor=black)](https://buymeacoffee.com/mehaksandhudev)

---

## ⚠️ Disclaimer

> **This project is strictly for EDUCATIONAL and RESEARCH purposes.**
>
> It demonstrates automated browser workflows, dynamic mobile IP rotation, RESTful local dashboards, and temporary email integration. The authors assume no responsibility for any misuse or violation of third-party Terms of Service.

---

## 📄 License

Licensed under the [MIT License](LICENSE).

---

<div align="center">

Crafted with ❤️ by **[Mehak Sandhu](https://github.com/mehaksandhudev)** • [Portfolio](https://www.mehak-sandhu.in)

</div>

