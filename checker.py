import requests
import os
from datetime import datetime
import smtplib
from email.mime.text import MIMEText

def send_notification(message):
    """ارسال ایمیل نوتیفیکیشن"""
    try:
        sender = os.environ.get('EMAIL_ADDRESS')
        password = os.environ.get('EMAIL_PASSWORD')
        
        if not sender or not password:
            print("⚠️ Email credentials not set")
            return
        
        msg = MIMEText(message)
        msg['Subject'] = '🎉 Questura Status Changed!'
        msg['From'] = sender
        msg['To'] = sender
        
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
            server.login(sender, password)
            server.send_message(msg)
        print("✅ Email sent successfully!")
    except Exception as e:
        print(f"❌ Email error: {e}")

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
    
    try:
        response = requests.get(url, headers=headers, timeout=30)
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        print(f"\n{'='*60}")
        print(f"Check at: {timestamp}")
        print(f"Status Code: {response.status_code}")
        print(f"{'='*60}")
        
        if response.status_code != 200:
            print(f"❌ Error: HTTP {response.status_code}")
            return
        
        content = response.text.lower()
        
        # بررسی محتوا
        if "accesso negato" in content or "bloccata" in content:
            print("❌ Access is BLOCKED by protection system")
        elif "disponibil" in content or "available" in content:
            message = f"""
🎉 QUESTURA SLOT AVAILABLE! 🎉

Time: {timestamp}
Link: {url}

Check immediately!
            """
            print("✅✅✅ SLOT AVAILABLE!")
            print("Sending notification...")
            send_notification(message)
        else:
            print("ℹ️  No changes detected")
            
    except requests.exceptions.Timeout:
        print("⏱️  Request timeout")
    except requests.exceptions.ConnectionError:
        print("🔌 Connection error")
    except Exception as e:
        print(f"❌ Error: {str(e)}")

if __name__ == "__main__":
    print("🔍 Starting Questura Monitor...")
    check_questura()
    print("\n✓ Check completed!")
