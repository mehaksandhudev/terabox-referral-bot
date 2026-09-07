# Step-by-Step Setup & Testing Guide

Comprehensive setup, configuration, and testing guide for **TeraBox Referral Automator**.

---

## 📋 Prerequisites

| Requirement | Details | Verification Command |
|---|---|---|
| **Python** | Version 3.10 or higher | `python --version` |
| **pip** | Latest Python package manager | `pip --version` |
| **Playwright Chromium** | Automated browser binary | `playwright install chromium` |
| **Git** | Version control | `git --version` |
| **VPN / WARP** (India) | Proton VPN or Cloudflare WARP | Needed to bypass Indian ISP blocks (Jio/Airtel) |
| **Android Phone** (Optional) | For free, unlimited Mobile IP rotation | Phone with recharged SIM + USB cable |

---

## 🚀 Step 1: Clone Repository & Virtual Environment

Open a PowerShell terminal and run:

```powershell
# 1. Clone repository
git clone https://github.com/mehaksandhudev/terabox-referral-bot.git
cd terabox-referral-bot

# 2. Create Python virtual environment
python -m venv venv

# 3. Activate virtual environment
.\venv\Scripts\activate
```

You will see `(venv)` prefixed in your terminal prompt.

---

## 📦 Step 2: Install Dependencies

```powershell
# Install required Python packages
pip install -r requirements.txt

# Install Playwright Chromium browser
playwright install chromium
```

> **Note:** `playwright install chromium` downloads a standalone Chromium binary (~150MB). This only needs to be run once.

---

## 🔗 Step 3: Configure Referral Links

Open [`referral_links.txt`](referral_links.txt) and paste your TeraBox referral links (one URL per line):

```text
https://1024terabox.com/s/YOUR_REFERRAL_CODE_1
https://1024terabox.com/s/YOUR_REFERRAL_CODE_2
```

*(You can also add or delete links dynamically from the Web Dashboard later).*

---

## 📱 Step 4: (Optional) Setup Mobile IP Rotation via Phone

To get a **fresh, clean mobile IP for every single registration** using an Android smartphone:

1. Connect your phone to your PC via USB cable.
2. On your phone:
   - Turn **OFF Wi-Fi**.
   - Turn **ON Mobile Data** (ensure the SIM has an active data pack).
   - Turn **ON USB Tethering** (*Settings -> Network / Hotspot -> USB Tethering*).
   - Turn **ON USB Debugging** (*Settings -> Developer Options -> USB Debugging*).
3. Unlock your phone screen. When prompted with *"Allow USB Debugging?"*, check **"Always allow from this computer"** and tap **OK**.

---

## 🌐 Step 5: Bypass Indian ISP Restrictions (Jio / Airtel)

Because Indian telecom operators block `terabox.com` and its mirrors at the ISP level:
- Open **Proton VPN** on your PC and click **Connect**.
- Once connected, TeraBox links will load with zero timeouts or connection errors.

---

## 🧪 Step 6: Test Every Component (Testing Cheat Sheet)

Before running the full bot, you can test every individual feature using these quick commands:

### Command 1: Run Single Test Registration (Live Screen)
Tests the complete registration flow on the first referral link (fills email, verification code, **both password and confirm password fields**, takes a screenshot, and saves to `accounts.txt`):
```powershell
.\venv\Scripts\python.exe test_single_run.py
```

### Command 2: Test ADB Phone Connection
Verify that your Android phone is detected and authorized:
```powershell
& "$env:LOCALAPPDATA\Android\Sdk\platform-tools\adb.exe" devices
```
*Expected output:*
```text
List of devices attached
YOUR_DEVICE_ID    device
```

### Command 3: Test Dynamic Mobile IP Rotation
Manually test toggling Airplane mode via ADB and watch your public IP change:
```powershell
.\venv\Scripts\python.exe -c "import subprocess, time, requests; adb=r'$env:LOCALAPPDATA\Android\Sdk\platform-tools\adb.exe'; print('Old IP:', requests.get('https://api.ipify.org?format=json').json()['ip']); subprocess.run([adb, 'shell', 'cmd', 'connectivity', 'airplane-mode', 'enable']); time.sleep(3); subprocess.run([adb, 'shell', 'cmd', 'connectivity', 'airplane-mode', 'disable']); time.sleep(8); print('New IP:', requests.get('https://api.ipify.org?format=json').json()['ip'])"
```

### Command 4: Test TeraBox Reachability
Verify if TeraBox is currently accessible on your internet connection:
```powershell
.\venv\Scripts\python.exe -c "import requests; print('HTTP Status:', requests.get('https://1024terabox.com', timeout=8).status_code)"
```
*If this times out, connect Proton VPN or Cloudflare WARP.*

### Command 5: View Saved Accounts
Check all registered accounts and the IP used for each:
```powershell
Get-Content accounts.txt
```

---

## 🖥️ Step 7: Launch Full Automation with Web Dashboard

To run the continuous automator with auto-restart and the live web dashboard:

```powershell
.\start_automator.bat
```

1. Starts the web dashboard server on **http://localhost:8080**.
2. Automatically opens the dashboard in your default browser.
3. Runs the bot in continuous round mode.
4. If the automator stops or completes, it automatically restarts after 10 seconds.

---

## 🔕 Step 8: Configure Silent Headless Startup on Boot

If you want the bot to **run automatically on Windows startup** without opening any browser windows:

1. Double-click **`add_to_startup.bat`** (or run `.\add_to_startup.bat` in PowerShell).
2. This creates a shortcut in your Windows Startup directory:
   `%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup\TeraBoxAutomator.lnk`
3. Because `start_automator.bat` has `set HEADLESS=true`, whenever your PC boots:
   - The bot launches completely invisible in the background.
   - You will see zero Chrome windows pop up.
   - The web dashboard will be available at **`http://localhost:8080`** to monitor progress and view accounts.

---

## 🤖 Step 9: (Optional) Telegram Bot Setup

Remotely monitor and control the bot from your phone via Telegram:

### 1. Create a Bot
1. Open Telegram and search for **`@BotFather`**.
2. Send `/newbot`, choose a name and username.
3. Copy the **HTTP API Token** (e.g. `123456789:ABCdef...`).

### 2. Get Your Chat ID
1. Search for **`@userinfobot`** on Telegram.
2. Send any message to receive your numeric Chat ID.

### 3. Save via Dashboard
1. Open **http://localhost:8080**.
2. In the **Telegram Integration** card, paste your **Bot Token** and **Chat ID**.
3. Click **Save Settings** and then click **Test Connection**.

### Telegram Commands
| Command | Description |
|---|---|
| `/stats` | View total processed, successes, errors, and success rate |
| `/pause` | Temporarily pause automation |
| `/resume` | Resume automation |
| `/stop` | Stop the automation loop |
| `/addlink <url>` | Add a new referral link directly from Telegram |
| `/help` | Show command list |

---

## 📁 File Reference

| File | Purpose |
|---|---|
| [`terabox_automator.py`](terabox_automator.py) | Main automation engine (Playwright, email verification, two-field password input, mobile IP rotation) |
| [`dashboard.py`](dashboard.py) | Local web dashboard HTTP server (port 8080), REST APIs, and Telegram bot |
| [`test_single_run.py`](test_single_run.py) | Standalone single-link test script with visible browser GUI |
| [`start_automator.bat`](start_automator.bat) | Windows launcher with auto-restart loop and headless configuration |
| [`add_to_startup.bat`](add_to_startup.bat) | Windows boot shortcut creator |
| [`accounts.txt`](accounts.txt) | Saved credentials (`email:password | IP | Timestamp | Ref URL`) |
| [`after_password_popup.png`](after_password_popup.png) | High-resolution screenshot captured immediately after registration |
| [`referral_links.txt`](referral_links.txt) | Configured referral links to cycle through |
| [`stats.json`](stats.json) | Metrics and historical results displayed on the dashboard |
| [`control.json`](control.json) | Real-time control flags (`paused`, `stopped`, delays, Telegram config) |
| [`logs.json`](logs.json) | In-memory log stream for the web dashboard terminal |

---

## 🛠️ Common Issues & Fixes

### 1. `Page.goto: net::ERR_CONNECTION_TIMED_OUT`
- **Cause**: Indian telecom operator (Jio, Airtel) blocks TeraBox domains at the ISP level.
- **Fix**: Connect **Proton VPN** or **Cloudflare WARP** before running the automator.

### 2. `Found 2 password input fields`
- **Cause**: Normal behavior. TeraBox updated its registration form to require Password + Confirm Password.
- **Fix**: The script automatically populates both fields and submits.

### 3. `1secmail create account error: 403 Forbidden`
- **Cause**: 1secmail has frequent Cloudflare rate limits.
- **Fix**: The bot defaults to `Mail.tm`, which creates temporary accounts reliably.

### 4. `ADB device unauthorized`
- **Cause**: Your phone has not authorized your computer for USB debugging.
- **Fix**: Unlock your phone screen, accept the USB Debugging prompt, and check "Always allow from this computer".
