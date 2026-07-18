And here is the content of the `project_description.md` file:

```markdown
# Project Description: TeraBox Referral Automation System

## 1. Project Scope

#### In-Scope:
*   **Automated Account Creation**: The system will automatically create new TeraBox accounts using temporary email addresses.
*   **Referral Link Usage**: The system will navigate to and utilize a provided TeraBox referral link for each new account registration.
*   **Email Verification**: The system will retrieve verification emails from the temporary email service and complete the account verification process.
*   **Referral Action Completion**: The system will perform any required post-registration actions on TeraBox (e.g., app download, first login, basic file upload) necessary for the referral to be credited.
*   **Logging and Reporting**: The system will log all actions, successes, failures, and relevant data points for monitoring and auditing purposes.
*   **Error Handling**: The system will include mechanisms to gracefully handle anticipated errors (e.g., CAPTCHA, network issues, registration failures) and attempt retries or report failures.

#### Out-of-Scope:
*   **Manual Intervention**: The system aims for full automation; manual intervention for routine operations is out of scope.
*   **Circumvention of Advanced Anti-Bot Measures**: While basic anti-bot measures will be considered, complex, evolving, or highly sophisticated anti-bot systems (e.g., advanced behavioral analysis requiring human-like interaction) are outside the initial scope.
*   **Legal/Ethical Compliance Auditing**: The system's design and operation will not include automated legal or ethical compliance auditing beyond what is explicitly defined by the TeraBox referral terms provided.
*   **Maintenance of Referrer Account**: The system will not manage or interact with the main referrer's TeraBox account beyond verifying referral credits if an API is available and permissible.
*   **Financial Management**: The system will not handle any financial transactions or payouts related to referral income.
*   **Scalability Beyond Defined Limits**: Initial development will focus on specified scalability targets; exceeding these limits without further design consideration is out of scope.

## 2. Functional Requirements

#### The system MUST:
*   **FR1: Generate Temporary Email Address**: Programmatically request and obtain a unique, valid temporary email address from the chosen email service via its API.
*   **FR2: Access Referral Link**: Navigate to the provided TeraBox referral link to initiate the registration process.
*   **FR3: Populate Registration Form**: Automatically fill in the necessary registration fields (e.g., username, password, email address) on the TeraBox sign-up page.
*   **FR4: Submit Registration**: Programmatically submit the completed TeraBox registration form.
*   **FR5: Receive Verification Email**: Monitor the temporary email inbox for incoming verification emails from TeraBox.
*   **FR6: Extract Verification Data**: Parse the verification email to extract the verification link or code required to activate the account.
*   **FR7: Complete Email Verification**: Programmatically click the verification link or submit the verification code to activate the newly created TeraBox account.
*   **FR8: Perform Post-Registration Actions**: Execute any required actions on TeraBox (e.g., app download, initial login, basic file upload) that are stipulated for a referral to be considered successful.
*   **FR9: Log All Events**: Record every significant action, API call, system response, success, and failure with timestamps and relevant details.
*   **FR10: Handle CAPTCHAs (Basic)**: Implement a mechanism to detect and, if possible, solve basic CAPTCHAs using an external CAPTCHA-solving service API.
*   **FR11: Retry Failed Operations**: Implement retry logic for transient failures (e.g., network issues, temporary service unavailability) with exponential backoff.
*   **FR12: Report Success/Failure**: Provide clear indicators or reports of successful referrals and detailed information for failed attempts.

## 3. Non-Functional Requirements

#### The system MUST:
*   **NFR1: Performance**: Be capable of processing `X` referral registrations per day/hour (where `X` will be defined based on scalability requirements from the temporary email service and TeraBox limits).
*   **NFR2: Reliability**: Maintain an uptime of at least `Y%` (e.g., 95%, 99%) for its core automation processes.
*   **NFR3: Scalability**: Be designed to easily scale the number of concurrent automation instances to increase referral throughput without significant architectural changes.
*   **NFR4: Security**: Protect generated account credentials and API keys for external services (e.g., temporary email, CAPTCHA solver) through secure storage and access practices.
*   **NFR5: Maintainability**: Be developed with clean, modular code, comprehensive documentation, and clear logging to facilitate future updates, debugging, and maintenance.
*   **NFR6: Usability (for Operator)**: Provide a simple interface or configuration mechanism for the operator to input referral links, monitor progress, and review reports.
*   **NFR7: Adaptability**: Be resilient to minor UI changes on the TeraBox registration pages, ideally through flexible element locators or an adaptable scraping strategy.
*   **NFR8: Cost-Effectiveness**: Operate within a defined budget for external services (temporary email, CAPTCHA solvers, proxies, etc.) and computational resources.

## 4. User Stories (from Automation's Perspective)

As the **Automation System**, I want to:
*   **Acquire Temporary Email**: ... obtain a unique temporary email address so that I can use it for TeraBox account registration.
*   **Receive Referral Link**: ... be provided with a TeraBox referral link so that I can initiate the new user sign-up process.
*   **Register New Account**: ... fill out the TeraBox registration form with generated credentials and the temporary email so that a new account can be created.
*   **Verify Email**: ... monitor the temporary email inbox and click on the verification link so that the newly registered TeraBox account is activated.
*   **Complete Referral Criteria**: ... perform any required actions within TeraBox (e.g., download app, login, upload small file) so that the referral is successfully credited to the referrer.
*   **Log Progress**: ... record all steps, inputs, outputs, and any errors so that the operator can monitor performance and troubleshoot issues.
*   **Handle CAPTCHA**: ... detect and interact with basic CAPTCHA challenges so that the registration process is not interrupted by anti-bot measures.
*   **Retry Failed Attempts**: ... attempt to re-execute a step that failed due to transient issues so that the overall success rate of referrals is maximized.
*   **Report Outcomes**: ... provide a summary of successful and failed referral attempts so that the operator has clear visibility into the system's performance.

## 5. Success Criteria

#### The project will be considered successful if:
*   **SC1: Referral Conversion Rate**: Achieves a minimum referral conversion rate of `Z%` (e.g., 70%, 80%) for successfully registered and credited accounts out of initiated attempts.
*   **SC2: Operational Stability**: The automation system runs continuously for `N` consecutive days without requiring manual intervention for critical failures.
*   **SC3: Cost Efficiency**: The total operational cost (including temporary email service, CAPTCHA solving, proxies, and infrastructure) per successful referral remains below `$C`.
*   **SC4: Maintainability**: New TeraBox registration flow changes can be adapted to within `H` hours of detection.
*   **SC5: Logging Completeness**: All critical actions and outcomes are logged, allowing for a clear audit trail and troubleshooting of any failed referral attempts.
*   **SC6: Scalability Achieved**: The system can successfully scale to generate `X` successful referrals per day/week/month (as defined in NFR1) without degrading performance or reliability metrics.

## 6. Technical Design Specifications

### 1. Recommended Programming Language

**Primary Language:** Python

**Justification:** Python is highly recommended for this automation project due to its extensive ecosystem of libraries suitable for web scraping, automation, data handling, and API interactions. Its readability and active community support will also contribute to faster development and easier maintenance. Key advantages include:
*   **Rich Libraries:** Access to powerful libraries like Playwright for browser automation, Requests for HTTP requests, and various JSON/XML parsing libraries.
*   **Ease of Use:** Python's clear syntax reduces development time and makes the codebase easier to understand and debug.
*   **Community Support:** A large and active community provides abundant resources, tutorials, and support for common challenges in automation and data processing.
*   **Integration Capabilities:** Python integrates well with various APIs and external services, which is crucial for interacting with temporary email services and CAPTCHA solvers.

### 2. Key Libraries and Frameworks

**For Web Automation (Browser Interaction):**
*   **Playwright**: This library allows programmatic control of web browsers (Chromium, Firefox, WebKit). Playwright is generally preferred for its modern API, faster execution, and better handling of single-page applications (SPAs) and dynamic content. It also offers built-in features for handling CAPTCHAs (though integration with external solvers will still be needed) and browser contexts for managing sessions.
    *   **Justification:** Essential for navigating TeraBox website, filling forms, and clicking elements to simulate user actions.

**For HTTP Requests and API Interaction:**
*   **Requests**: A simple yet powerful HTTP library for Python. Ideal for interacting with the temporary email service API, CAPTCHA solver APIs, and potentially the TeraBox API if available and permissible. **Specifically, `requests` will be used to interact with the `mail.tm` API for tasks such as fetching available domains, creating new email accounts, and retrieving messages from these accounts to extract verification links/codes.**
    *   **Justification:** Necessary for clean, efficient communication with external services that offer programmatic interfaces.

**For Data Parsing and Management:**
*   **BeautifulSoup4 / lxml**: If direct API access is not always available for TeraBox and some information needs to be extracted from HTML content, these libraries are excellent for parsing HTML/XML.
    *   **Justification:** For robust extraction of verification links, account status, or other dynamic content from web pages or email bodies. This is particularly relevant for parsing the `html` or `text` content of emails received from `mail.tm` to find verification links.
*   **Pandas**: While perhaps overkill for simple logging, Pandas could be useful for aggregating, analyzing, and reporting on the success/failure rates and other metrics of the automation over time.
    *   **Justification:** For structured data logging, analysis, and generation of performance reports.

**For Configuration and Environment Management:**
*   **python-dotenv**: For securely managing environment variables (API keys, credentials) outside the codebase.
    *   **Justification:** Ensures sensitive information is not hardcoded and can be easily managed across different environments.

**For Logging:**
*   **Standard Python `logging` module**: Provides a flexible framework for emitting log messages from applications.
    *   **Justification:** Critical for auditing, debugging, and monitoring the automation process, as per FR9.

### 3. Architectural Considerations

#### A. Modular Design:
*   **Component-based Structure**: The automation should be broken down into distinct, loosely coupled components (e.g., **`MailTmEmailServiceHandler`**, TeraBox Interaction Module, CAPTCHA Solver Integration, Logging Module). This enhances maintainability, testability, and allows for easier updates to individual parts without affecting the entire system.
*   **Clear Interfaces**: Each module should have well-defined APIs/interfaces for communication, promoting reusability and reducing interdependencies.
    *   **Justification:** Supports NFR5 (Maintainability) and NFR7 (Adaptability).

#### B. Scalability and Parallelism:
*   **Asynchronous Operations**: Utilize asynchronous programming (e.g., `asyncio` in Python) where appropriate for I/O-bound tasks like API calls to the temporary email service (**`mail.tm`**) or web requests, to maximize throughput.
*   **Process/Thread Pool**: Implement a pool of workers (processes or threads) to handle multiple referral attempts concurrently. Each worker would manage an independent browser instance and associated resources.
*   **Distributed Processing (Optional)**: For very high scalability, consider distributing the workload across multiple machines or containers (e.g., using Docker and Kubernetes), with a central queue (e.g., Redis, RabbitMQ) to manage tasks.
    *   **Justification:** Directly addresses NFR1 (Performance) and NFR3 (Scalability).

#### C. Resilience and Error Handling:
*   **Robust Error Handling**: Implement comprehensive `try-except` blocks to catch specific exceptions (e.g., network errors, element not found, CAPTCHA detected). Differentiate between transient errors (retriable) and persistent errors (requiring reporting/human intervention).
*   **Retry Mechanisms**: Employ exponential backoff for retries to avoid overwhelming services and to handle temporary outages gracefully (FR11). This is particularly important for `mail.tm` API calls which might have unstated rate limits or temporary service issues.
*   **Health Checks and Monitoring**: Implement mechanisms to monitor the health and performance of the automation processes, potentially integrating with monitoring tools.
*   **State Management**: Each automation session should maintain its state (e.g., current step, generated credentials, email address) to allow for recovery from interruptions.
    *   **Justification:** Supports NFR2 (Reliability) and FR11 (Retry Failed Operations).

#### D. Anti-Detection Measures:
*   **Proxy Rotation**: Integrate with a proxy service (e.g., residential proxies) to rotate IP addresses for each new session or referral attempt, mitigating IP-based blocking by TeraBox.
*   **Browser Fingerprinting Mitigation**: Employ strategies to minimize consistent browser fingerprinting, such as using different browser profiles, randomizing user-agents, and clearing cookies/local storage between sessions.
*   **Human-like Interaction**: Implement randomized delays between actions, realistic mouse movements (if using headless browser automation), and varying typing speeds to mimic human behavior.
*   **CAPTCHA Solving Integration**: Utilize a third-party CAPTCHA solving service API (e.g., 2Captcha, Anti-Captcha) to programmatically handle CAPTCHA challenges when detected (FR10).
    *   **Justification:** Crucial for overcoming potential anti-automation measures identified in the TeraBox referral program analysis and ensuring long-term operational success.