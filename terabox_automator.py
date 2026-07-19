import requests
import json
import time
import logging
import secrets
import string
import asyncio
import nest_asyncio
from playwright.async_api import async_playwright
import os
import re # For regex to extract verification code
import base64
from datetime import datetime
import threading

# Optional: Gemini Vision for smart element finding
try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False
    logging.info("google-generativeai not installed. LLM vision fallback disabled.")

# Apply nest_asyncio to allow asyncio.run() in environments with existing event loops (like Colab)
nest_asyncio.apply()

# --- Logging setup: console + JSON file for dashboard ---
SCRIPT_DIR_LOG = os.path.dirname(os.path.abspath(__file__))
LOGS_FILE = os.path.join(SCRIPT_DIR_LOG, "logs.json")


# Disable verbose logs from requests / urllib3 to prevent infinite loops
logging.getLogger("urllib3").setLevel(logging.WARNING)
logging.getLogger("requests").setLevel(logging.WARNING)


class JsonLogHandler(logging.Handler):
    """Sends log entries to the dashboard API in memory to avoid disk file locks."""
    def __init__(self):
        super().__init__()
        self.port = int(os.environ.get("PORT", 8080))

    def _post_log(self, entry):
        try:
            requests.post(f"http://127.0.0.1:{self.port}/api/logs", json=entry, timeout=2.0)
        except Exception:
            pass

    def emit(self, record):
        # Ignore requests, urllib3, and dashboard API call logs to avoid infinite loop
        if record.name.startswith("urllib3") or record.name.startswith("requests"):
            return
        if "POST /api/logs" in record.getMessage() or "GET /api/" in record.getMessage():
            return
        try:
            entry = {
                "time": datetime.now().strftime("%H:%M:%S"),
                "level": record.levelname,
                "message": record.getMessage()
            }
            # Send to dashboard POST API in a background thread to prevent blocks/timeouts
            threading.Thread(target=self._post_log, args=(entry,), daemon=True).start()
        except Exception:
            pass


logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
# Add JSON handler for dashboard
logging.getLogger().addHandler(JsonLogHandler())




# --- MailTmHandler class ---
class MailTmHandler:
    BASE_URL = "https://api.mail.tm"

    def __init__(self):
        logging.info("MailTmHandler initialized.")
        self.token = None # Store the authentication token

    def get_domains(self):
        """Fetches and returns a list of active Mail.tm domains."""
        endpoint = f"{self.BASE_URL}/domains"
        try:
            response = requests.get(endpoint)
            response.raise_for_status()
            domains_data = response.json()

            if isinstance(domains_data, dict) and 'hydra:member' in domains_data:
                domains_list = domains_data['hydra:member']
            elif isinstance(domains_data, list):
                domains_list = domains_data
            else:
                logging.error(f"Mail.tm domains endpoint returned unexpected type: {type(domains_data)} - Content: {domains_data}")
                return []

            active_domains = []
            for d in domains_list:
                if isinstance(d, dict) and "domain" in d and "isActive" in d:
                    if d["isActive"]:
                        active_domains.append(d["domain"])
                else:
                    logging.warning(f"Skipping malformed domain entry: {d}")
            logging.info(f"Fetched {len(active_domains)} active domains.")
            return active_domains
        except requests.exceptions.RequestException as e:
            logging.error(f"Error fetching domains: {e}")
            return []
        except json.JSONDecodeError as e:
            logging.error(f"JSONDecodeError fetching domains: {e} - Response content: {response.text}")
            return []

    def create_account(self):
        """Creates a new temporary email account on Mail.tm and returns account details."""
        domains = self.get_domains()
        if not domains:
            logging.error("No active domains available to create an account.")
            return None

        domain = domains[0]

        username_prefix = ''.join(secrets.choice(string.ascii_lowercase) for i in range(10))
        email_address = f"{username_prefix}@{domain}"
        password = ''.join(secrets.choice(string.ascii_letters + string.digits + string.punctuation) for i in range(12))

        endpoint = f"{self.BASE_URL}/accounts"
        headers = {"Content-Type": "application/json"}
        payload = {"address": email_address, "password": password}

        try:
            response = requests.post(endpoint, headers=headers, data=json.dumps(payload))
            response.raise_for_status()
            account_info = response.json()
            if isinstance(account_info, dict):
                logging.info(f"Account created successfully: {email_address}")
                account_info['password'] = password
                return account_info
            else:
                logging.error(f"Mail.tm create account returned unexpected non-dict type: {type(account_info)} - Content: {account_info}")
                return None
        except requests.exceptions.RequestException as e:
            logging.error(f"Error creating account {email_address}: {e}")
            if response.status_code == 422:
                logging.error(f"Account creation failed due to: {response.json().get('detail', 'Unknown error')}")
            return None
        except json.JSONDecodeError as e:
            logging.error(f"JSONDecodeError creating account {email_address}: {e} - Response content: {response.text}")
            return []

    def login(self, address, password):
        """Logs into a Mail.tm account and retrieves the authentication token."""
        endpoint = f"{self.BASE_URL}/token"
        headers = {"Content-Type": "application/json"}
        payload = {"address": address, "password": password}

        try:
            response = requests.post(endpoint, headers=headers, data=json.dumps(payload))
            response.raise_for_status()
            token_info = response.json()
            if isinstance(token_info, dict):
                self.token = token_info.get("token")
                logging.info(f"Successfully logged in to {address} and obtained token.")
                return self.token
            else:
                logging.error(f"Mail.tm login returned unexpected non-dict type: {type(token_info)} - Content: {token_info}")
                return None
        except requests.exceptions.RequestException as e:
            logging.error(f"Error logging in to {address}: {e}")
            if response.status_code == 401:
                logging.error(f"Login failed: Invalid credentials for {address}")
            return None
        except json.JSONDecodeError as e:
            logging.error(f"JSONDecodeError logging in to {address}: {e} - Response content: {response.text}")
            return []

    def get_messages(self, account_id=None, retries=10, delay=5):
        """Polls for and retrieves messages. Uses /messages endpoint with Bearer token."""
        if not self.token:
            logging.error("Not logged in. Please call login() first.")
            return []

        # Correct endpoint: /messages (NOT /accounts/{id}/messages)
        endpoint = f"{self.BASE_URL}/messages"
        headers = {"Authorization": f"Bearer {self.token}"}

        for i in range(retries):
            try:
                response = requests.get(endpoint, headers=headers)
                response.raise_for_status()
                data = response.json()

                # Mail.tm returns { "hydra:member": [...], "hydra:totalItems": N }
                if isinstance(data, dict) and 'hydra:member' in data:
                    messages = data['hydra:member']
                elif isinstance(data, list):
                    messages = data
                else:
                    logging.warning(f"Unexpected response format: {type(data)}")
                    messages = []

                if messages:
                    logging.info(f"Retrieved {len(messages)} messages.")
                    # Fetch full message bodies
                    full_messages = []
                    for msg in messages:
                        msg_id = msg.get('id')
                        if msg_id:
                            try:
                                full_resp = requests.get(f"{self.BASE_URL}/messages/{msg_id}", headers=headers)
                                full_resp.raise_for_status()
                                full_messages.append(full_resp.json())
                            except Exception as e:
                                logging.warning(f"Failed to fetch full message {msg_id}: {e}")
                                full_messages.append(msg)  # Use summary as fallback
                    return full_messages
                else:
                    logging.info(f"No messages yet. Retry {i+1}/{retries} in {delay}s...")
            except requests.exceptions.RequestException as e:
                logging.error(f"Error fetching messages: {e}")
            except json.JSONDecodeError as e:
                logging.error(f"JSONDecodeError fetching messages: {e}")
            time.sleep(delay)
        logging.warning(f"No messages retrieved after {retries} attempts.")
        return []


# --- 1secmail Fallback Handler ---
class OneSecMailHandler:
    """Fallback email provider using 1secmail.com API."""
    BASE_URL = "https://www.1secmail.com/api/v1/"

    def __init__(self):
        self.login_name = None
        self.domain = None
        logging.info("OneSecMailHandler initialized.")

    def create_account(self):
        """Creates a random 1secmail address."""
        try:
            resp = requests.get(f"{self.BASE_URL}?action=genRandomMailbox&count=1")
            resp.raise_for_status()
            emails = resp.json()
            if emails:
                email = emails[0]
                self.login_name, self.domain = email.split('@')
                logging.info(f"1secmail account created: {email}")
                # Generate a random password for TeraBox registration
                password = ''.join(secrets.choice(string.ascii_letters + string.digits + string.punctuation) for _ in range(12))
                return {
                    'address': email,
                    'password': password,
                    'id': email,  # Use email as ID
                    'login': self.login_name,
                    'domain': self.domain
                }
        except Exception as e:
            logging.error(f"1secmail create account error: {e}")
        return None

    def get_messages(self, retries=12, delay=10):
        """Polls for messages on the 1secmail address."""
        if not self.login_name or not self.domain:
            logging.error("No 1secmail account created.")
            return []

        for i in range(retries):
            try:
                resp = requests.get(
                    f"{self.BASE_URL}?action=getMessages&login={self.login_name}&domain={self.domain}"
                )
                resp.raise_for_status()
                messages = resp.json()
                if messages:
                    logging.info(f"1secmail: Retrieved {len(messages)} messages.")
                    # Fetch full message bodies
                    full_messages = []
                    for msg in messages:
                        msg_id = msg.get('id')
                        try:
                            full_resp = requests.get(
                                f"{self.BASE_URL}?action=readMessage&login={self.login_name}&domain={self.domain}&id={msg_id}"
                            )
                            full_resp.raise_for_status()
                            full_messages.append(full_resp.json())
                        except Exception:
                            full_messages.append(msg)
                    return full_messages
                else:
                    logging.info(f"1secmail: No messages yet. Retry {i+1}/{retries} in {delay}s...")
            except Exception as e:
                logging.error(f"1secmail error: {e}")
            time.sleep(delay)
        logging.warning(f"1secmail: No messages after {retries} attempts.")
        return []

# --- LLM Vision Helper ---
async def find_element_with_llm(page, description, gemini_api_key=None):
    """Uses Gemini Vision to find a UI element by taking a screenshot and asking the LLM."""
    if not GEMINI_AVAILABLE or not gemini_api_key:
        logging.warning("Gemini Vision not available (no API key or package not installed).")
        return None

    try:
        genai.configure(api_key=gemini_api_key)
        model = genai.GenerativeModel('gemini-2.0-flash')

        # Take screenshot
        screenshot_bytes = await page.screenshot()
        screenshot_b64 = base64.b64encode(screenshot_bytes).decode('utf-8')

        prompt = f"""Look at this screenshot of a web page. I need to click on: {description}

Return ONLY a JSON object with the approximate x,y pixel coordinates of the CENTER of that element.
Format: {{"x": 123, "y": 456}}
Do not include any other text, just the JSON."""

        response = model.generate_content([
            prompt,
            {"mime_type": "image/png", "data": screenshot_b64}
        ])

        # Parse coordinates from response
        coord_text = response.text.strip()
        # Extract JSON from response
        match = re.search(r'\{[^}]+\}', coord_text)
        if match:
            coords = json.loads(match.group())
            logging.info(f"LLM found element at coordinates: x={coords['x']}, y={coords['y']}")
            return coords
        else:
            logging.warning(f"LLM response did not contain valid coordinates: {coord_text}")
            return None
    except Exception as e:
        logging.error(f"LLM vision error: {e}")
        return None


# --- Main Orchestration Script ---
async def orchestrate_full_registration(terabox_referral_url):
    """Returns dict: {'success': bool, 'email': str}"""
    mailtm_handler = MailTmHandler()
    onesecmail_handler = OneSecMailHandler()
    email_provider = None  # Track which provider is active

    browser = None
    page = None
    created_account = None

    try:
        # 1. Create temporary email account
        preferred_provider = os.environ.get("EMAIL_PROVIDER", "1secmail").lower()

        if preferred_provider == '1secmail':
            logging.info("Using 1secmail as preferred email provider...")
            created_account = onesecmail_handler.create_account()
            if created_account:
                email_provider = '1secmail'
            else:
                logging.warning("1secmail failed. Waiting 3s before trying Mail.tm as fallback...")
                time.sleep(3)
                created_account = mailtm_handler.create_account()
                if created_account:
                    email_provider = 'mailtm'
        else:
            logging.info("Using Mail.tm as preferred email provider...")
            created_account = mailtm_handler.create_account()
            if created_account:
                email_provider = 'mailtm'
            else:
                logging.warning("Mail.tm failed. Waiting 3s before trying 1secmail as fallback...")
                time.sleep(3)
                created_account = onesecmail_handler.create_account()
                if created_account:
                    email_provider = '1secmail'

        if not created_account:
            logging.error("Failed to create email account with any provider. Aborting.")
            return {'success': False, 'email': '—'}

        if not isinstance(created_account, dict):
            logging.critical(f"create_account returned unexpected type: {type(created_account)}.")
            return {'success': False, 'email': '—'}

        temp_email_address = created_account.get('address')
        temp_email_password = created_account.get('password')
        temp_account_id = created_account.get('id')

        if not all([temp_email_address, temp_email_password, temp_account_id]):
            logging.error(f"Missing critical account details. Aborting.")
            return {'success': False, 'email': '—'}

        logging.info(f"Email account created: {temp_email_address}")

        # 2. Initialize Playwright and navigate to TeraBox referral link
        logging.info("Initializing Playwright and launching browser...")
        async with async_playwright() as p:
            browser = await p.chromium.launch(
                headless=True,
                args=[
                    "--no-sandbox",
                    "--disable-setuid-sandbox",
                    "--disable-dev-shm-usage",
                    "--disable-gpu",
                    "--no-first-run",
                    "--no-zygote"
                ]
            )
            page = await browser.new_page()
            logging.info("Playwright initialized, browser launched in headless mode, and new page created.")

            terabox_username = temp_email_address.split('@')[0]
            terabox_password = temp_email_password

            logging.info(f"Attempting to register on TeraBox with email: {temp_email_address}")

            logging.info(f"Navigating to referral URL: {terabox_referral_url}")
            try:
                await page.goto(terabox_referral_url)
                await page.wait_for_load_state('networkidle')
                logging.info(f"Successfully navigated to {terabox_referral_url}")

                # --- SELECTORS (inspected from live 1024terabox.com site) ---
                # TeraBox uses a React SPA with minimal CSS classes.
                # We use Playwright text/role selectors for reliability.

                # Step 1: Click "Login" button in top-right corner
                logging.info("Looking for Login button in top-right corner...")
                login_btn = page.get_by_text("Login", exact=True).last
                await login_btn.wait_for(state="visible", timeout=15000)
                await login_btn.click()
                logging.info("Clicked Login button.")
                await asyncio.sleep(3)

                # Step 2: Click "Sign up" tab in the login dialog
                logging.info("Looking for 'Sign up' tab...")
                try:
                    signup_tab = page.get_by_text("Sign up", exact=True).first
                    await signup_tab.wait_for(state="visible", timeout=10000)
                    await signup_tab.click()
                    logging.info("Clicked 'Sign up' tab.")
                except Exception:
                    logging.warning("'Sign up' tab not found.")
                    return False
                await asyncio.sleep(2)

                # Step 3: Click the envelope/mail icon on the sign-up view
                # The mail icon uses a base64 data URI. We match a unique fingerprint.
                logging.info("Looking for email/envelope icon on sign-up view...")
                email_clicked = False

                # Strategy 1: Match by unique base64 fingerprint of the mail icon
                MAIL_ICON_FINGERPRINT = "AACOEfKt"  # Unique substring from mail icon's base64 src
                try:
                    mail_icon = page.locator(f'img[src*="{MAIL_ICON_FINGERPRINT}"]').first
                    await mail_icon.wait_for(state="visible", timeout=5000)
                    await mail_icon.click()
                    logging.info("Clicked email icon via base64 fingerprint match.")
                    email_clicked = True
                except Exception:
                    logging.info("Base64 fingerprint match failed.")

                # Strategy 2: LLM Vision fallback (if Gemini API key is set)
                if not email_clicked:
                    gemini_key = os.environ.get("GEMINI_API_KEY")
                    if gemini_key:
                        logging.info("Trying LLM vision to find the email icon...")
                        coords = await find_element_with_llm(
                            page,
                            "the small envelope/mail icon button (NOT Google, NOT Facebook, NOT Apple). It's a small icon in the bottom row of login options that looks like an envelope.",
                            gemini_key
                        )
                        if coords:
                            await page.mouse.click(coords['x'], coords['y'])
                            logging.info(f"Clicked email icon via LLM vision at ({coords['x']}, {coords['y']}).")
                            email_clicked = True
                    else:
                        logging.info("No GEMINI_API_KEY set. Skipping LLM vision fallback.")

                if not email_clicked:
                    logging.warning("Could not find email/envelope icon on sign-up view.")
                    return {'success': False, 'email': temp_email_address}

                await asyncio.sleep(2)

                logging.info(f"Attempting to fill registration form for {temp_email_address}")

                # Step 4: Fill email field
                email_input = page.locator('#email-input, input[placeholder*="email" i]').first
                try:
                    await email_input.wait_for(state="visible", timeout=5000)
                    await email_input.fill(temp_email_address)
                    logging.info(f"Filled email: {temp_email_address}")
                except Exception:
                    logging.error("Email input field not found.")
                    return {'success': False, 'email': temp_email_address}
                await asyncio.sleep(1)

                # Step 5: Click "Continue" button to proceed to verification
                logging.info("Looking for Continue button...")
                continue_clicked = False

                # Strategy 1: Text match with force click
                try:
                    continue_btn = page.get_by_text("Continue", exact=True).first
                    await continue_btn.wait_for(state="visible", timeout=5000)
                    await continue_btn.click(force=True)
                    logging.info("Clicked Continue button (text match).")
                    continue_clicked = True
                except Exception:
                    logging.info("Text match for Continue failed.")

                # Strategy 2: CSS selector for the specific button
                if not continue_clicked:
                    try:
                        btn = page.locator('button:has-text("Continue"), div:has-text("Continue")[class*="btn"], div:has-text("Continue")[class*="button"]').first
                        await btn.wait_for(state="visible", timeout=3000)
                        await btn.click(force=True)
                        logging.info("Clicked Continue button (CSS selector).")
                        continue_clicked = True
                    except Exception:
                        logging.info("CSS selector for Continue failed.")

                # Strategy 3: JavaScript click on any element containing "Continue"
                if not continue_clicked:
                    try:
                        clicked = await page.evaluate("""() => {
                            const els = document.querySelectorAll('button, div[role="button"], [class*="btn"], [class*="button"]');
                            for (const el of els) {
                                if (el.textContent.trim() === 'Continue' && el.offsetParent !== null) {
                                    el.click();
                                    return true;
                                }
                            }
                            return false;
                        }""")
                        if clicked:
                            logging.info("Clicked Continue button (JS click).")
                            continue_clicked = True
                        else:
                            logging.warning("JS click found no matching Continue button.")
                    except Exception as e:
                        logging.warning(f"JS click failed: {e}")

                if not continue_clicked:
                    logging.error("Could not click Continue button with any strategy.")
                    return {'success': False, 'email': temp_email_address}

                await asyncio.sleep(3)

                # Verify the click worked — check if verification code input appeared
                try:
                    code_check = page.locator('input[class*="code"], input[class*="verify"], input[maxlength="1"], input[maxlength="4"]').first
                    await code_check.wait_for(state="visible", timeout=8000)
                    logging.info("Verification code input detected — Continue click succeeded.")
                except Exception:
                    # The page didn't change — try clicking Continue again with force
                    logging.warning("Verification input not found. Retrying Continue click...")
                    try:
                        await page.evaluate("""() => {
                            const els = [...document.querySelectorAll('*')];
                            for (const el of els) {
                                if (el.textContent.trim() === 'Continue' && el.children.length === 0 && el.offsetParent !== null) {
                                    el.click(); return;
                                }
                            }
                        }""")
                        await asyncio.sleep(5)
                        logging.info("Retried Continue click via JS.")
                    except Exception:
                        pass

                # Step 6 & 7: Retrieve and fill verification code (with retry on wrong code)
                MAX_CODE_ATTEMPTS = 3
                code_accepted = False

                for attempt in range(1, MAX_CODE_ATTEMPTS + 1):
                    logging.info(f"Verification code attempt {attempt}/{MAX_CODE_ATTEMPTS}...")

                    # --- Retrieve verification code from email ---
                    logging.info(f"Retrieving verification code for {temp_email_address} via {email_provider}...")

                    verification_code = None
                    messages = []

                    if email_provider == 'mailtm':
                        if attempt == 1:
                            mailtm_handler.login(temp_email_address, temp_email_password)
                        messages = mailtm_handler.get_messages(retries=15, delay=8)
                        if not messages:
                            logging.warning("Mail.tm returned no messages.")
                    elif email_provider == '1secmail':
                        messages = onesecmail_handler.get_messages(retries=15, delay=8)

                    for message in messages:
                        subject = message.get('subject', '')
                        subject_lower = subject.lower()

                        if "terabox" in subject_lower or "verif" in subject_lower or "code" in subject_lower or not subject:
                            logging.info(f"Found verification email. Subject: {subject}")

                            # Strategy 1: Extract code from SUBJECT first (most reliable!)
                            # TeraBox subject format: "5532 is your TeraBox verification code"
                            subject_match = re.search(r'\b(\d{4,6})\b', subject)
                            if subject_match:
                                candidate = subject_match.group(1)
                                # Filter out years (2020-2030) as false positives
                                if not (2020 <= int(candidate) <= 2030):
                                    verification_code = candidate
                                    logging.info(f"Extracted verification code from SUBJECT: {verification_code}")
                                    break

                            # Strategy 2: Fall back to email body
                            body = (
                                message.get('text', '') or
                                message.get('html', '') or
                                message.get('textBody', '') or
                                message.get('htmlBody', '') or
                                message.get('body', '')
                            )
                            # Find all digit sequences and filter out years
                            all_matches = re.findall(r'\b(\d{4,6})\b', body)
                            for candidate in all_matches:
                                if not (2020 <= int(candidate) <= 2030):
                                    verification_code = candidate
                                    logging.info(f"Extracted verification code from BODY: {verification_code}")
                                    break
                            if verification_code:
                                break
                            else:
                                logging.warning(f"No valid code found. All matches: {all_matches}. Body preview: {body[:200]}")

                    if not verification_code:
                        logging.error("Failed to extract verification code from email. Aborting.")
                        return {'success': False, 'email': temp_email_address}

                    # --- Fill verification code ---
                    logging.info(f"Filling verification code: {verification_code}")
                    code_inputs = page.locator('input[type="text"], input[type="tel"], input[type="number"]')
                    code_input_count = await code_inputs.count()

                    if code_input_count >= 4:
                        # Clear existing values first
                        for i in range(min(len(verification_code), code_input_count)):
                            await code_inputs.nth(i).fill('')
                        await asyncio.sleep(0.5)
                        for i, digit in enumerate(verification_code):
                            if i < code_input_count:
                                await code_inputs.nth(i).fill(digit)
                        logging.info("Filled verification code in individual input boxes.")
                    else:
                        single_code_input = page.locator('input[placeholder*="code" i], input[placeholder*="verif" i]').first
                        try:
                            await single_code_input.fill(verification_code)
                            logging.info("Filled verification code in single input field.")
                        except Exception:
                            logging.error("Could not find verification code input field.")
                            return {'success': False, 'email': temp_email_address}

                    await asyncio.sleep(3)

                    # --- Check for "Incorrect verification code" error ---
                    try:
                        error_msg = page.get_by_text("Incorrect", exact=False).first
                        is_error = await error_msg.is_visible(timeout=2000)
                    except Exception:
                        is_error = False

                    if is_error:
                        logging.warning(f"Incorrect verification code on attempt {attempt}. Will retry...")
                        if attempt < MAX_CODE_ATTEMPTS:
                            # Click "Resend Verification Code" and wait for new email
                            try:
                                resend_btn = page.get_by_text("Resend", exact=False).first
                                await resend_btn.wait_for(state="visible", timeout=10000)
                                await resend_btn.click()
                                logging.info("Clicked 'Resend Verification Code'. Waiting for new email...")
                                await asyncio.sleep(10)  # Wait for new email to arrive
                            except Exception:
                                logging.warning("Could not click Resend button. Waiting anyway...")
                                await asyncio.sleep(30)
                        continue  # Try again
                    else:
                        logging.info("Verification code accepted!")
                        code_accepted = True
                        break

                if not code_accepted:
                    logging.error(f"Failed to enter correct verification code after {MAX_CODE_ATTEMPTS} attempts.")
                    return {'success': False, 'email': temp_email_address}

                # Step 8: Fill password field
                pwd_input = page.locator('#pwd-input, input[placeholder*="password" i]').first
                try:
                    await pwd_input.wait_for(state="visible", timeout=5000)
                    await pwd_input.fill(terabox_password)
                    logging.info("Filled password.")
                except Exception:
                    logging.warning("Password input not found - may appear on a later step.")
                await asyncio.sleep(1)

                # Step 9: Click final submit/register button
                logging.info("Looking for final submit button...")
                for btn_text in ["Sign up", "Register", "Create Account", "Submit", "Continue"]:
                    final_btn = page.get_by_text(btn_text, exact=False).first
                    try:
                        if await final_btn.is_visible(timeout=2000):
                            await final_btn.click()
                            logging.info(f"Clicked '{btn_text}' button.")
                            break
                    except Exception:
                        continue
                else:
                    try:
                        generic_btn = page.locator('button[type="submit"]').first
                        await generic_btn.click()
                        logging.info("Clicked generic submit button.")
                    except Exception:
                        logging.error("Could not find any submit button.")
                        return {'success': False, 'email': temp_email_address}

                await page.wait_for_load_state('networkidle')

                logging.info(f"Registration form submitted for {temp_email_address}. Current URL: {page.url}")
                registration_success = True

            except Exception as e:
                logging.error(f"Error during TeraBox registration for {temp_email_address}: {e}")
                registration_success = False

            if not registration_success:
                logging.error("TeraBox registration failed. Aborting.")
                return {'success': False, 'email': temp_email_address}

            logging.info("Full registration completed successfully!")
            return {'success': True, 'email': temp_email_address}

    except Exception as e:
        logging.critical(f"An unexpected error occurred during orchestration: {e}")
        return {'success': False, 'email': temp_email_address if 'temp_email_address' in dir() else '—'}


# --- Stats & Control Tracking ---
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
STATS_FILE = os.path.join(SCRIPT_DIR, "stats.json")
LINKS_FILE = os.path.join(SCRIPT_DIR, "referral_links.txt")
CONTROL_FILE = os.path.join(SCRIPT_DIR, "control.json")


def load_control():
    """Load control settings from JSON file."""
    try:
        if os.path.exists(CONTROL_FILE):
            with open(CONTROL_FILE, 'r') as f:
                return json.load(f)
    except Exception:
        pass
    return {"paused": False, "stopped": False, "round_delay": 30, "link_delay": 15}


def load_stats():
    """Load stats from JSON file."""
    try:
        if os.path.exists(STATS_FILE):
            with open(STATS_FILE, 'r') as f:
                return json.load(f)
    except Exception:
        pass
    return {"total": 0, "success": 0, "errors": 0, "total_links": 0, "running": False, "results": []}


def save_stats(stats):
    """Save stats to JSON file (dashboard reads this)."""
    try:
        with open(STATS_FILE, 'w') as f:
            json.dump(stats, f, indent=2)
    except Exception as e:
        logging.error(f"Failed to save stats: {e}")


def load_referral_links():
    """Load referral links from file."""
    if not os.path.exists(LINKS_FILE):
        logging.warning(f"No referral_links.txt found at {LINKS_FILE}")
        return []
    with open(LINKS_FILE, 'r') as f:
        links = [line.strip() for line in f if line.strip() and line.strip().startswith('http')]
    logging.info(f"Loaded {len(links)} referral links from {LINKS_FILE}")
    return links


def update_result(stats, index, **kwargs):
    """Update a specific result entry in stats."""
    while len(stats["results"]) <= index:
        stats["results"].append({})
    stats["results"][index].update(kwargs)
    save_stats(stats)


if __name__ == '__main__':
    from datetime import datetime

    logging.info("=" * 60)
    logging.info("TeraBox Referral Automation — Starting")
    logging.info("=" * 60)

    EMAIL_PROVIDER = os.environ.get("EMAIL_PROVIDER", "1secmail")

    print(f"\n  [*] TeraBox Referral Automation (continuous mode)")
    print(f"  [*] Email provider: {EMAIL_PROVIDER}")
    print(f"  [*] Control and delays managed via Dashboard at http://localhost:8080")
    print(f"  [*] Press Ctrl+C to stop\n")

    # Cumulative stats across rounds
    total_all = 0
    success_all = 0
    errors_all = 0
    round_num = 0

    try:
        while True:
            # Check control file at start of round
            ctrl = load_control()
            if ctrl.get("stopped"):
                logging.info("Automation stopped via dashboard control.")
                break

            # Handle pause
            if ctrl.get("paused"):
                logging.info("Automation paused via dashboard. Waiting...")
                while True:
                    time.sleep(2)
                    ctrl = load_control()
                    if ctrl.get("stopped"):
                        logging.info("Automation stopped via dashboard while paused.")
                        break
                    if not ctrl.get("paused"):
                        logging.info("Automation resumed!")
                        break
                if ctrl.get("stopped"):
                    break

            round_num += 1

            # Re-read links each round (picks up new links added via dashboard)
            referral_links = load_referral_links()

            if not referral_links:
                logging.info("No referral links found. Waiting for links to be added via dashboard...")
                if not os.path.exists(LINKS_FILE):
                    with open(LINKS_FILE, 'w') as f:
                        f.write("")
                # Update stats to show idle
                stats = load_stats()
                stats["running"] = False
                stats["total_links"] = 0
                save_stats(stats)
                time.sleep(5)
                continue

            logging.info(f"\n{'='*60}")
            logging.info(f"ROUND {round_num} -- {len(referral_links)} links to process")
            logging.info(f"{'='*60}")

            # Initialize stats for this round
            stats = load_stats()
            stats["total"] = total_all
            stats["success"] = success_all
            stats["errors"] = errors_all
            stats["total_links"] = total_all + len(referral_links)
            stats["running"] = True
            stats["results"] = stats.get("results", [])
            save_stats(stats)

            for i, url in enumerate(referral_links):
                # Double-check stop/pause during links loop
                ctrl = load_control()
                if ctrl.get("stopped"):
                    logging.info("Automation stopped via dashboard.")
                    break
                if ctrl.get("paused"):
                    logging.info("Automation paused via dashboard. Waiting...")
                    while True:
                        time.sleep(2)
                        ctrl = load_control()
                        if ctrl.get("stopped") or not ctrl.get("paused"):
                            break
                    if ctrl.get("stopped"):
                        break
                    logging.info("Automation resumed!")

                result_idx = total_all + i  # Global index across rounds

                logging.info(f"Processing link {i+1}/{len(referral_links)}: {url}")

                timestamp = datetime.now().strftime("%H:%M:%S")
                update_result(stats, result_idx, url=url, email="--", status="running", timestamp=timestamp, error="")
                stats["running"] = True
                save_stats(stats)

                try:
                    result = asyncio.run(orchestrate_full_registration(url))
                    email_used = result.get('email', '--') if isinstance(result, dict) else '--'
                    success = result.get('success', False) if isinstance(result, dict) else bool(result)

                    update_result(stats, result_idx, email=email_used)

                    stats["total"] += 1
                    if success:
                        stats["success"] += 1
                        update_result(stats, result_idx, status="success", timestamp=datetime.now().strftime("%H:%M:%S"))
                        logging.info(f"[OK] Link {i+1}/{len(referral_links)} SUCCEEDED ({email_used})")
                    else:
                        stats["errors"] += 1
                        update_result(stats, result_idx, status="error", error="Registration failed", timestamp=datetime.now().strftime("%H:%M:%S"))
                        logging.error(f"[FAIL] Link {i+1}/{len(referral_links)} FAILED ({email_used})")

                except Exception as e:
                    stats["total"] += 1
                    stats["errors"] += 1
                    update_result(stats, result_idx, status="error", error=str(e)[:100], timestamp=datetime.now().strftime("%H:%M:%S"))
                    logging.error(f"[FAIL] Link {i+1}/{len(referral_links)} CRASHED: {e}")

                save_stats(stats)

                # Delay between referrals
                link_delay = ctrl.get("link_delay", 15)
                if i < len(referral_links) - 1:
                    logging.info(f"Waiting {link_delay}s before next link...")
                    # Wait in small intervals so we can respond to pause/stop during delay
                    for _ in range(int(link_delay)):
                        time.sleep(1)
                        ctrl = load_control()
                        if ctrl.get("stopped"):
                            break
                    if ctrl.get("stopped"):
                        break

            # Update cumulative counters
            total_all = stats["total"]
            success_all = stats["success"]
            errors_all = stats["errors"]

            ctrl = load_control()
            if ctrl.get("stopped"):
                break

            round_delay = ctrl.get("round_delay", 30)
            logging.info(f"\nRound {round_num} done | Total: {total_all} | Success: {success_all} | Errors: {errors_all}")
            logging.info(f"Next round in {round_delay}s... (Ctrl+C to stop)")

            stats["running"] = False
            stats["next_round_at"] = time.time() + round_delay
            save_stats(stats)

            # Wait in small intervals so we can respond to pause/stop during round delay
            for _ in range(int(round_delay)):
                time.sleep(1)
                ctrl = load_control()
                if ctrl.get("stopped"):
                    break
            if ctrl.get("stopped"):
                break

    except KeyboardInterrupt:
        logging.info("\nStopped by user (Ctrl+C).")

    # Finalize stats
    stats = load_stats()
    stats["running"] = False
    save_stats(stats)
    print(f"\n  Final stats: Total={total_all} | Success={success_all} | Errors={errors_all}")

