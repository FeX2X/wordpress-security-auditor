# wordpress-security-auditor

👾 Advanced Python WordPress Security Research Toolkit.

⚡ Concurrent HTTP testing
🌐 WordPress endpoint analysis
🔍 Dashboard security inspection
🧩 Plugin environment assessment
📊 Terminal-based reporting
🎨 Hacker-style CLI interface
🐍 Python automation
🛡️ Authorized security research

## 🚀 Key Features

- **Multiple Credential Formats:** Supports `URL|USER|PASS`, `URL#USER@PASS`, `URL#USER:PASS`, and `URL:USER:PASS`.
- **URL Normalization:** Automatically handles HTTPS prefixes and removes trailing slashes.
- **HTTP Session Management:** Uses `requests.Session()` to maintain session cookies across requests.
- **Redirect Handling:** Detects domain redirects and adjusts the base URL accordingly.
- **UserPro Detection:** Identifies UserPro login pages and detects alternate authentication flows.
- **Dashboard Validation:** Checks WordPress dashboard response indicators such as `wp-admin/profile.php` and `wpwrap`.
- **Plugin Detection:** Identifies plugin-installation references in dashboard responses.
- **File Manager Detection:** Detects WP File Manager references in dashboard HTML.
- **Multithreading:** Supports concurrent processing with `ThreadPoolExecutor`.
- **Output Management:** Exports validation results and categorized findings into separate text files.
- **Colored Terminal Output:** Provides color-coded status messages using Colorama.

## 📦 INSTALLATION

```bash
git clone https://github.com/FeX2X/wordpress-security-auditor.git

cd wordpress-security-auditor

pip install requests colorama
```

### 📂 Supported Input Formats

The parser supports multiple entry formats:

1. `URL|USER|PASS`
2. `URL#USER@PASS`
3. `URL#USER:PASS`
4. `URL:USER:PASS`

Use synthetic test data or credentials you are authorized to handle.

## 🎯 LEARNING OBJECTIVES

- Understand WordPress security architecture.
- Learn HTTP session management.
- Explore Python concurrent programming.
- Understand authentication security.
- Study plugin permissions and access controls.
- Learn secure web application testing.

## ⚠️ DISCLAIMER

This project is intended for educational purposes and authorized security testing in controlled environments.

Only test WordPress installations that you own or have explicit permission to assess.

Never use leaked credentials, perform unauthorized login attempts, or collect other people's account information.

## 🔐 SECURITY NOTICE

Use synthetic test accounts, protect sensitive information, and never publish passwords, session cookies, or private account data.

## 📜 LICENSE

XXX License

---

\<p align="center">
&#x20; 💀 \<b>THINK • TEST • SECURE\</b>
&#x20; \<br>
&#x20; 👾 CYBERSECURITY RESEARCH 👾
\</p>

