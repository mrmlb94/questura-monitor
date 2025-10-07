import requests
import os
from datetime import datetime
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import re

def send_notification(subject, body):
    """ارسال ایمیل نوتیفیکیشن"""
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
    """استخراج متن وضعیت از HTML"""
    patterns = [
        r'Residence permit position:\s*(.+?)(?:\.|<br|</)',
        r'Posizione permesso di soggiorno:\s*(.+?)(?:\.|<br|</)',
        r'Il documento di soggiorno.*?(?:pronto|consegna)',
        r'residence permit is being processed',
        r'is ready for collection',
        r'pronto per la consegna'
    ]
    
    for pattern in patterns:
        match = re.search(pattern, html_content, re.IGNORECASE | re.DOTALL)
        if match:
            if match.groups():
                text = match.group(1).strip()
            else:
                text = match.group(0).strip()
            
            # پاک کردن همه تگ‌های HTML
            text = re.sub(r'<[^>]+>', '', text)
            # پاک کردن فضای خالی اضافی
            text = re.sub(r'\s+', ' ', text).strip()
            return text
    
    return None


def check_permesso():
    """بررسی وضعیت Permesso di Soggiorno"""
    url = "https://questure.poliziadistato.it/stranieri/?lang=english&mime=1&pratica=059551999909&invia=Submit"
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.9,it;q=0.8',
        'Accept-Encoding': 'gzip, deflate, br',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
        'Referer': 'https://questure.poliziadistato.it/'
    }
    
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    try:
        response = requests.get(url, headers=headers, timeout=30)
        
        print(f"\n{'='*70}")
        print(f"🔍 Checking Permesso di Soggiorno Status")
        print(f"Time: {timestamp}")
        print(f"HTTP Status: {response.status_code}")
        print(f"{'='*70}\n")
        
        if response.status_code != 200:
            message = f"⚠️ Error: HTTP {response.status_code}"
            print(message)
            
            send_notification(
                f"⚠️ Permesso Check Error - {timestamp}",
                f"Error checking Permesso status.\n\nHTTP Status: {response.status_code}\nTime: {timestamp}\nURL: {url}"
            )
            return
        
        content = response.text
        content_lower = content.lower()
        
        # استخراج متن دقیق وضعیت
        status_text = extract_status_text(content)
        
        # بررسی حالت‌های مختلف
        if "accesso negato" in content_lower or "bloccata" in content_lower:
            # حالت 1: دسترسی مسدود شده
            print("❌ ACCESS BLOCKED by protection system")
            
            send_notification(
                f"🚫 Permesso Check - Access Blocked - {timestamp}",
                f"⚠️ The website blocked the request.\n\nTime: {timestamp}\n\nTry checking manually:\n{url}"
            )
            
        elif any(keyword in content_lower for keyword in [
            "ready for collection",
            "pronto per la consegna",
            "è pronto",
            "ready for delivery",
            "available for pickup"
        ]):
            # حالت 2: آماده برای تحویل! 🎉
            print("🎉🎉🎉 PERMESSO IS READY FOR COLLECTION!")
            print(f"Status: {status_text if status_text else 'Ready!'}")
            
            email_body = f"""
🎉🎉🎉 PERMESSO DI SOGGIORNO IS READY! 🎉🎉🎉

Your residence permit is ready for collection!

Current Status:
{status_text if status_text else 'Ready for delivery'}

Time: {timestamp}

⚡ GO TO QUESTURA TO PICK IT UP IMMEDIATELY!

Check details at:
{url}

You may also receive an SMS with pickup instructions.
            """
            
            send_notification(
                f"🎉 PERMESSO READY! - {timestamp}",
                email_body
            )
            
        elif any(keyword in content_lower for keyword in [
            "being processed",
            "in lavorazione",
            "in corso",
            "processing"
        ]):
            # حالت 3: در حال پردازش
            print("⏳ Permesso is still being processed")
            print(f"Current status: {status_text if status_text else 'Being processed'}")
            
            email_body = f"""
⏳ Permesso Status Update

Your residence permit is still being processed.

Current Status:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
{status_text if status_text else 'Residence permit is being processed'}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📅 Checked at: {timestamp}

✋ You need to wait. The permit is not ready yet.

We will notify you as soon as the status changes to "ready for collection".

Next check: In a few hours...
            """
            
            send_notification(
                f"⏳ Permesso Status - Still Processing - {timestamp}",
                email_body
            )
            
        else:
            # حالت 4: وضعیت نامشخص
            print("ℹ️ Status checked - Unknown state")
            if status_text:
                print(f"Found text: {status_text}")
            
            email_body = f"""
ℹ️ Permesso Status Check

Status checked successfully.

Current Status:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
{status_text if status_text else 'Status information not clearly identified'}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Time: {timestamp}

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
            f"Request timeout while checking.\n\nTime: {timestamp}\nURL: {url}"
        )
        
    except requests.exceptions.ConnectionError:
        print("🔌 Connection error")
        send_notification(
            f"🔌 Permesso Connection Error - {timestamp}",
            f"Connection error.\n\nTime: {timestamp}\nURL: {url}"
        )
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        send_notification(
            f"❌ Permesso Check Error - {timestamp}",
            f"Error occurred:\n{str(e)}\n\nTime: {timestamp}\nURL: {url}"
        )

if __name__ == "__main__":
    print("🔍 Starting Permesso di Soggiorno Monitor...")
    check_permesso()
    print("\n✓ Check completed!")
