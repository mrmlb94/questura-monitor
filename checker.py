import requests
import os
from datetime import datetime
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

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
        msg.attach(MIMEText(body, 'plain'))
        
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
            server.login(sender, password)
            server.send_message(msg)
        print("✅ Email sent successfully!")
        return True
    except Exception as e:
        print(f"❌ Email error: {e}")
        return False

def check_questura():
    """بررسی وضعیت سایت Questura"""
    url = "https://questure.poliziadistato.it/stranieri/?lang=english&mime=1&pratica=059551999909&invia=Submit"
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.9,it;q=0.8',
        'Accept-Encoding': 'gzip, deflate, br',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1'
    }
    
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    try:
        response = requests.get(url, headers=headers, timeout=30)
        
        print(f"\n{'='*60}")
        print(f"Check at: {timestamp}")
        print(f"Status Code: {response.status_code}")
        print(f"{'='*60}")
        
        if response.status_code != 200:
            status = "❌ Error"
            message = f"HTTP {response.status_code}"
            print(f"{status}: {message}")
            
            # ارسال ایمیل برای خطا
            send_notification(
                f"⚠️ Questura Check Error - {timestamp}",
                f"Error checking Questura website.\n\nHTTP Status: {response.status_code}\nTime: {timestamp}\nURL: {url}"
            )
            return
        
        content = response.text.lower()
        
        # بررسی محتوا و تعیین وضعیت
        if "accesso negato" in content or "bloccata" in content:
            status = "❌ BLOCKED"
            emoji = "🚫"
            message = "Access is BLOCKED by protection system"
            print(message)
            
            # ایمیل برای حالت مسدود
            send_notification(
                f"{emoji} Questura Check - BLOCKED - {timestamp}",
                f"Status: Access Blocked\n\nThe website protection system blocked the request.\nTime: {timestamp}\nURL: {url}"
            )
            
        elif "disponibil" in content or "available" in content:
            status = "✅ AVAILABLE"
            emoji = "🎉"
            message = "SLOT IS AVAILABLE!"
            print(f"✅✅✅ {message}")
            
            # ایمیل فوری برای اسلات موجود
            send_notification(
                f"{emoji} QUESTURA SLOT AVAILABLE! - {timestamp}",
                f"🎉🎉🎉 SLOT IS AVAILABLE! 🎉🎉🎉\n\nTime: {timestamp}\nURL: {url}\n\n⚡ CHECK IMMEDIATELY!"
            )
            
        else:
            status = "ℹ️ No Change"
            emoji = "✓"
            message = "No changes detected - website is accessible"
            print(f"ℹ️  {message}")
            
            # ایمیل برای وضعیت عادی
            send_notification(
                f"{emoji} Questura Daily Check - {timestamp}",
                f"Status: OK - No changes\n\nWebsite checked successfully.\nNo slots available yet.\nTime: {timestamp}\nURL: {url}\n\nNext check in a few hours..."
            )
            
    except requests.exceptions.Timeout:
        message = "Request timeout"
        print(f"⏱️  {message}")
        send_notification(
            f"⏱️ Questura Check Timeout - {timestamp}",
            f"Request timeout while checking website.\n\nTime: {timestamp}\nURL: {url}"
        )
        
    except requests.exceptions.ConnectionError:
        message = "Connection error"
        print(f"🔌 {message}")
        send_notification(
            f"🔌 Questura Connection Error - {timestamp}",
            f"Connection error while checking website.\n\nTime: {timestamp}\nURL: {url}"
        )
        
    except Exception as e:
        message = str(e)
        print(f"❌ Error: {message}")
        send_notification(
            f"❌ Questura Check Error - {timestamp}",
            f"Unexpected error occurred.\n\nError: {message}\nTime: {timestamp}\nURL: {url}"
        )

if __name__ == "__main__":
    print("🔍 Starting Questura Monitor...")
    check_questura()
    print("\n✓ Check completed!")
