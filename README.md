# Questura Monitor

🤖 Automatic daily checker for Italian Questura (Police) website

[![Check Questura Daily](https://github.com/mrmlb94/questura-monitor/actions/workflows/check-questura.yml/badge.svg)](https://github.com/mrmlb94/questura-monitor/actions/workflows/check-questura.yml)

## Features

- ✅ Checks Questura website daily
- 📧 Sends email notification when status changes
- 🔄 Runs automatically via GitHub Actions
- 💰 100% Free (no server needed)

## How it works

This script automatically checks the Questura website twice daily at 8 AM and 8 PM (CEST) using GitHub Actions.

When a slot becomes available, you'll receive an email notification immediately.

## Setup

1. Fork this repository
2. Go to Settings > Secrets and variables > Actions
3. Add two secrets:
   - `EMAIL_ADDRESS`: your Gmail address
   - `EMAIL_PASSWORD`: your Gmail App Password

## Status

Last check: Automated via GitHub Actions
