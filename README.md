# Questura Permesso Monitor 🇮🇹

🤖 Automatic checker for Italian Residence Permit (Permesso di Soggiorno) status

[![Check Questura Daily](https://github.com/mrmlb94/questura-monitor/actions/workflows/check-questura.yml/badge.svg)](https://github.com/mrmlb94/questura-monitor/actions/workflows/check-questura.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT)
[![Python 3.11](https://img.shields.io/badge/python-3.11-blue.svg)](https://www.python.org/downloads/)

## 🎯 Problem

Waiting for your Italian residence permit and manually checking the Questura website multiple times daily? This tool automates the process and notifies you instantly when your permit is ready!

## ✨ Features

- ✅ **Automated Checking**: Monitors Questura website 5 times daily
- 📧 **Instant Notifications**: Email alerts when status changes
- 🔄 **Runs 24/7**: Via GitHub Actions (even when your computer is off)
- 💰 **100% Free**: No server costs, no subscriptions
- 🔒 **Privacy First**: Your data stays secure in GitHub Secrets
- 🕐 **Italy Timezone**: Displays accurate Italy time (CEST/CET)
- 🌍 **Open Source**: Fully transparent and customizable

## 📋 Requirements

- GitHub account (free)
- Gmail account with App Password
- Your Questura pratica number (10 digits)

## 🚀 Setup Guide

### Step 1: Fork This Repository

Click the **"Fork"** button at the top right of this page to create your own copy.

### Step 2: Get Your Pratica Number

Find your **10-digit pratica number** on your Questura receipt. It looks like: `0595519999`

### Step 3: Generate Gmail App Password

1. Go to [Google Account Security](https://myaccount.google.com/security)
2. Enable **2-Step Verification** (required)
3. Go to **App passwords** (search for it in settings)
4. Generate a new app password for "GitHub Questura Monitor"
5. Copy the **16-character password** (e.g., `abcd efgh ijkl mnop`)

> **Note**: Remove spaces when adding to GitHub Secrets

### Step 4: Add GitHub Secrets

1. In your forked repository, go to: **Settings** → **Secrets and variables** → **Actions**
2. Click **"New repository secret"**
3. Add the following three secrets:

| Secret Name | Description | Example |
|------------|-------------|---------|
| `EMAIL_ADDRESS` | Your Gmail address | `your.email@gmail.com` |
| `EMAIL_PASSWORD` | Gmail App Password (no spaces) | `abcdefghijklmnop` |
| `PRATICA_NUMBER` | Your 10-digit Questura number | `0595519999` |

### Step 5: Enable GitHub Actions

1. Go to the **Actions** tab in your repository
2. Click **"I understand my workflows, go ahead and enable them"**
3. The workflow is now active! ✅

### Step 6: Test It

1. Go to **Actions** → **Check Questura Daily**
2. Click **"Run workflow"** → **"Run workflow"** (green button)
3. Wait 1-2 minutes
4. Check your email inbox! 📧

## 📧 Email Notifications

### While Processing ⏳

```
Subject: ⏳ Permesso Status - Still Processing

Your residence permit is still being processed.

Current Status:
━━━━━━━━━━━━━━━━━━━━━
residence permit is being processed
━━━━━━━━━━━━━━━━━━━━━

📅 Checked at: 2025-10-07 22:11:28 (Italy Time)

✋ You need to wait. The permit is not ready yet.

Next check: In a few hours...
```

### When Ready! 🎉

```
Subject: 🎉 PERMESSO READY!

🎉🎉🎉 PERMESSO DI SOGGIORNO IS READY! 🎉🎉🎉

Your residence permit is ready for collection!

⚡ GO TO QUESTURA TO PICK IT UP IMMEDIATELY!

Time: 2025-10-07 22:11:28 (Italy Time)

You may also receive an SMS with pickup instructions.
```

## ⏰ Checking Schedule

The bot automatically checks at:

- **08:00** (8 AM)
- **14:00** (2 PM)
- **17:00** (5 PM)
- **20:00** (8 PM)
- **00:00** (12 AM)

All times in **Italy timezone (CEST/CET)**

> **To change schedule**: Edit `.github/workflows/check-questura.yml` and modify the `cron` line

## 🔧 Customization

### Change Check Frequency

Edit `.github/workflows/check-questura.yml`:

```
schedule:
  # Check every 3 hours
  - cron: '0 */3 * * *'
  
  # Or only twice daily (8 AM and 8 PM)
  - cron: '0 6,18 * * *'
```

### Add More Notification Methods

The code can be extended to support:
- Telegram Bot
- Discord Webhook
- Slack
- SMS (Twilio)

## 🔒 Privacy & Security

✅ **Your data is safe:**
- Pratica number stored securely in GitHub Secrets
- Secrets are encrypted and never visible in logs
- No third-party services involved (except Gmail)
- Repository can be kept public safely
- Only you receive the email notifications

✅ **What is stored:**
- Nothing! Data is only processed in-memory during checks

## 🛠️ Troubleshooting

### Email Not Received?

1. **Check Spam folder** - First email may be flagged
2. **Verify Secrets** - Make sure all 3 secrets are added correctly
3. **Check App Password** - 16 characters, no spaces
4. **View Logs** - Go to Actions tab to see detailed logs

### Bot Not Running?

1. **Check Actions** - Make sure workflows are enabled
2. **Check Repository** - Must be your fork, not the original
3. **Check Secrets** - All 3 must be present

### Access Blocked Error?

The Questura website has anti-bot protection. If this happens frequently:
- The bot includes proper headers to avoid detection
- Checks are spaced out (5 times daily)
- If persists, try reducing check frequency

## 🤝 Contributing

Contributions are welcome! Feel free to:

- 🐛 Report bugs
- 💡 Suggest new features
- 🔧 Submit pull requests
- ⭐ Star the repo if you find it useful!

## 📝 License

MIT License - Feel free to use, modify, and share!

## 💬 Support

- **Issues**: Open a GitHub issue for bugs or questions
- **Discussions**: Use GitHub Discussions for general questions
- **LinkedIn**: Connect with me [@mrmlb94](https://linkedin.com/in/mrmlb94)

## 🌟 Acknowledgments

Built with ❤️ for the expat community in Italy 🇮🇹

Made by [Mohammadreza Motallebi](https://github.com/mrmlb94) - Data Analyst Engineer @ HCFX, Milano

---

**⭐ If this tool helped you, please star the repository!**

**📢 Share with friends waiting for their permesso**

**🤝 Contributions and feedback are always welcome**
