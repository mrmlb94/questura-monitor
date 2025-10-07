# Questura Monitor

🤖 Automatic daily checker for Italian Questura (Police) website

[![Check Questura Daily](https://github.com/mrmlb94/questura-monitor/actions/workflows/check-questura.yml/badge.svg)](https://github.com/mrmlb94/questura-monitor/actions/workflows/check-questura.yml)

## Features

- ✅ Checks Permesso di Soggiorno status automatically
- 📧 Email notifications when status changes
- 🔄 Runs twice daily via GitHub Actions
- 💰 100% Free (no server needed)
- 🔒 Secure - data stored in GitHub Secrets

## Setup

### 1. Fork this repository

### 2. Get your Pratica Number
Find your 10-digit pratica number on your Questura receipt

### 3. Get Gmail App Password
1. Enable 2-Step Verification in Google Account
2. Generate App Password
3. Copy the 16-character password

### 4. Add Secrets
Go to: Settings > Secrets and variables > Actions

Add these secrets:

| Name | Value |
|------|-------|
| EMAIL_ADDRESS | Your Gmail address |
| EMAIL_PASSWORD | Gmail App Password |
| PRATICA_NUMBER | Your 10-digit number |

### 5. Enable Actions
Go to Actions tab and enable workflows

### 6. Test
Actions > Check Questura Daily > Run workflow

## Email Notifications

**Processing:**
