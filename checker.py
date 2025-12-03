import requests
import os
from datetime import datetime
from zoneinfo import ZoneInfo
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import re

def send_notification(subject, body):
    """Send email notification"""
    try:
        sender = os.environ.get('EMAIL_ADDRESS')
        password = os.environ.get('EMAIL_PASSWORD')
        
        if not sender or not password:
            print("⚠️ Email credentials not set")
            return False
        
        msg = MIMEMultipart()
        msg['Subject'] = subject
        msg['From'] = sender
        msg['To'] = sender
        msg.attach(MIMEText(body, 'plain', 'utf-8'))
        
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
            server.login(sender, password)
            server.send_message(msg)
        print("✅ Email sent successfully!")
        return True
    except Exception as e:
        print(f"❌ Email error: {e}")
        return False

def extract_status_text(html_content):
    """Extract status text from HTML"""
    # NEW PATTERNS that match your actual website
    patterns = [
        r'residence permit.*?ready.*?collect[^\.]*\.',
        r'residence permit.*?pronto[^\.]*\.',
        r'is ready[^\.]*\.',
        r'Residence permit position:\s*(.+?)(?:\.|<br|</)',
        r'Posizione permesso di soggiorno:\s*(.+?)(?:\.|<br|</)',
        r'residence permit is being processed',
        r'is ready for collection',
        r'pronto per la consegna'
    ]
    
    content_lower = html_content.lower()
    
    # Check for READY status first (most important)
    if 'your residence permit is ready' in content_lower:
        return "Your residence permit is ready. You will be informed by SMS when and where you can collect it."
    
    # Check for processing status
    if 'residence permit is being processed' in content_lower:
        return "Residence permit is being processed."
    
    # Try regex patterns
    for pattern in patterns:
        match = re.search(pattern, html_content, re.IGNORECASE | re.DOTALL)
        if match:
            if match.groups():
                text = match.group(1).strip()
            else:
                text = match.group(0).strip()
            
            text = re.sub(r'<[^>]+>', '', text)
            text = re.sub(r'\s+', ' ', text).strip()
            return text
    
    return None

def check_permesso():
    """Check Permesso di Soggiorno status"""
    
    pratica_number = os.environ.get('PRATICA_NUMBER')
    
    if not pratica_number:
        print("❌ Error: PRATICA_NUMBER not set in Secrets!")
        send_notification(
            "⚠️ Configuration Error",
            "PRATICA_NUMBER is not configured. Please add it to GitHub Secrets."
        )
        return
    
    url = f"https://questure.poliziadistato.it/stranieri/?lang=english&mime=1&pratica={pratica_number}&invia=Submit"
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.9,it;q=0.8',
        'Accept-Encoding': 'gzip, deflate, br',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
        'Referer': 'https://questure.poliziadistato.it/'
    }
    
    italy_tz = ZoneInfo("Europe/Rome")
    timestamp = datetime.now(italy_tz).strftime("%Y-%m-%d %H:%M:%S")
    
    try:
        response = requests.get(url, headers=headers, timeout=30)
        
        print(f"\n{'='*70}")
        print(f"🔍 Checking Permesso di Soggiorno Status")
        print(f"Time: {timestamp} (Italy)")
        print(f"HTTP Status: {response.status_code}")
        print(f"{'='*70}\n")
        
        if response.status_code != 200:
            message = f"⚠️ Error: HTTP {response.status_code}"
            print(message)
            
            send_notification(
                f"⚠️ Permesso Check Error - {timestamp}",
                f"Error checking Permesso status.\n\nHTTP Status: {response.status_code}\nTime: {timestamp} (Italy Time)\nURL: {url}"
            )
            return
        
        content = response.text
        content_lower = content.lower()
        
        status_text = extract_status_text(content)
        print(f"DEBUG - Extracted status: {status_text}")  # DEBUG LINE
        
        if "accesso negato" in content_lower or "bloccata" in content_lower:
            print("❌ ACCESS BLOCKED by protection system")
            send_notification(
                f"🚫 Permesso Check - Access Blocked - {timestamp}",
                f"⚠️ The website blocked the request.\n\nTime: {timestamp} (Italy Time)\n\nTry checking manually:\n{url}"
            )
            
        elif "your residence permit is ready" in content_lower or "ready" in (status_text.lower() if status_text else ""):
            print("🎉🎉🎉 PERMESSO IS READY FOR COLLECTION!")
            print(f"Status: {status_text if status_text else 'Ready!'}")
            
            email_body = f"""
🎉🎉🎉 PERMESSO DI SOGGIORNO IS READY! 🎉🎉🎉

Your residence permit is ready for collection!

Current Status:
{status_text if status_text else 'Ready for delivery'}

Time: {timestamp} (Italy Time)

⚡ GO TO QUESTURA LECCO TO PICK IT UP IMMEDIATELY!
UFFICIO IMMIGRAZIONE PRESSO UFFICIO STRANIERI POLIZIA - LECCO

Check details at:
{url}

You may also receive an SMS with pickup instructions.
            """
            
            send_notification(
                f"🎉 PERMESSO READY! - {timestamp}",
                email_body
            )
            
        elif "being processed" in (content_lower or "") or "in lavorazione" in content_lower:
            print("⏳ Permesso is still being processed")
            print(f"Current status: {status_text if status_text else 'Being processed'}")
            
            email_body = f"""
⏳ Permesso Status Update

Your residence permit is still being processed.

Current Status:
━━━━━━━━━━━━━━━━━━━
{status_text if status_text else 'Residence permit is being processed'}
━━━━━━━━━━━━━━━━━━━

📅 Checked at: {timestamp} (Italy Time)

✋ You need to wait. The permit is not ready yet.

We will notify you as soon as it's READY FOR COLLECTION.

Next check: In a few hours...
            """
            
            send_notification(
                f"⏳ Permesso Status - Still Processing - {timestamp}",
                email_body
            )
            
        else:
            print("ℹ️ Status checked - Unknown state")
            if status_text:
                print(f"Found text: {status_text}")
            
            email_body = f"""
ℹ️ Permesso Status Check

Status checked successfully.

Current Status:
━━━━━━━━━━━━━━━━━━━
{status_text if status_text else 'Status information not clearly identified'}
━━━━━━━━━━━━━━━━━━━

Time: {timestamp} (Italy Time)

⚠️ The exact status could not be determined.
You may want to check manually at:
{url}

Next automatic check: In a few hours...
            """
            
            send_notification(
                f"ℹ️ Permesso Status - Checked - {timestamp}",
                email_body
            )
            
    except requests.exceptions.Timeout:
        print("⏱️ Request timeout")
        send_notification(
            f"⏱️ Permesso Check Timeout - {timestamp}",
            f"Request timeout while checking.\n\nTime: {timestamp} (Italy Time)\nURL: {url}"
        )
        
    except requests.exceptions.ConnectionError:
        print("🔌 Connection error")
        send_notification(
            f"🔌 Permesso Connection Error - {timestamp}",
            f"Connection error.\n\nTime: {timestamp} (Italy Time)\nURL: {url}"
        )
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        send_notification(
            f"❌ Permesso Check Error - {timestamp}",
            f"Error occurred:\n{str(e)}\n\nTime: {timestamp} (Italy Time)\nURL: {url}"
        )

if __name__ == "__main__":
    print("🔍 Starting Permesso di Soggiorno Monitor...")
    check_permesso()
    print("\n✓ Check completed!")
