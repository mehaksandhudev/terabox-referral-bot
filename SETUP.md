# Setup Guide

Step-by-step setup instructions for TeraBox Referral Automator.

---

## Prerequisites

| Requirement | Version | Check |
|---|---|---|
| Python | 3.10+ | `python --version` |
| pip | Latest | `pip --version` |
| Git | Any | `git --version` |

---

## Step 1: Clone the Repository

```bash
git clone https://github.com/mehaksandhudev/terabox-referral-bot.git
cd terabox-referral-bot
```

---

## Step 2: Create Virtual Environment

**Windows:**
```powershell
python -m venv venv
.\venv\Scripts\activate
```

**macOS / Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

You should see `(venv)` in your terminal prompt.

---

## Step 3: Install Dependencies

```bash
pip install playwright requests nest_asyncio
```

Then install the Chromium browser for Playwright:

```bash
playwright install chromium
```

> **Note:** This downloads ~150MB of Chromium. Only needed once.

---

## Step 4: Add Referral Links

**Option A: Edit the file directly**
```bash
# Add one URL per line
echo https://1024terabox.com/s/YOUR_REFERRAL_CODE > referral_links.txt
```

**Option B: Use the dashboard (recommended)**
Start the dashboard first (Step 5), then add links from the web UI.

---

## Step 5: Start the Dashboard

Open a terminal and run:

```bash
python dashboard.py
```

Open **http://localhost:8080** in your browser. You'll see:
- Stats cards (total, success, errors, rate)
- Referral link manager (add/remove URLs)
- Live log viewer
- Results table

---

## Step 6: Start the Automation

Open a **second terminal**, activate venv, and run:

**Windows:**
```powershell
.\venv\Scripts\activate
python terabox_automator.py
```

**macOS / Linux:**
```bash
source venv/bin/activate
python terabox_automator.py
```

The automator will:
1. Read all links from `referral_links.txt`
2. Process each link (create email → register → verify)
3. Wait 30 seconds
4. Repeat from step 1

Watch the dashboard update in real-time!

---

## Step 7: (Optional) Gemini Vision Fallback

If standard selectors fail, you can enable LLM-powered element detection:

```bash
set GEMINI_API_KEY=your_api_key_here    # Windows
export GEMINI_API_KEY=your_api_key_here  # macOS/Linux

python terabox_automator.py
```

Get a free API key at [Google AI Studio](https://aistudio.google.com/).

---

## Configuration

All settings use environment variables:

```bash
# Email provider (default: 1secmail, fallback: mailtm)
set EMAIL_PROVIDER=1secmail

# Delay between each link in a round (default: 15 seconds)
set DELAY_SECONDS=15

# Delay between rounds (default: 30 seconds)
set ROUND_DELAY=30
```

---

## Stopping the Automation

Press `Ctrl+C` in the automation terminal. The dashboard will show the final stats.

---

## Troubleshooting

### `ModuleNotFoundError: No module named 'nest_asyncio'`
You're running outside the virtual environment. Activate it first:
```bash
.\venv\Scripts\activate   # Windows
source venv/bin/activate   # macOS/Linux
```

### `playwright install` hangs or fails
Try running as administrator, or install manually:
```bash
python -m playwright install chromium
```

### Dashboard shows "Waiting for automation..."
Make sure the automator script is running in a separate terminal.

### 1secmail returns 403
This is normal. The bot automatically falls back to Mail.tm.

---

## File Overview

| File | Purpose |
|---|---|
| `terabox_automator.py` | Main bot — browser automation, email handling, registration |
| `dashboard.py` | Web server — dashboard UI, stats API, link management |
| `referral_links.txt` | Your referral URLs (one per line) |
| `stats.json` | Auto-generated — real-time stats |
| `logs.json` | Auto-generated — log entries for dashboard |

---

<p align="center">
  <strong>Questions?</strong> Open an issue on GitHub.
</p>
