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
    
    if 'your residence permit is ready' in content_lower:
        return "✅ READY - You will be informed by SMS when and where you can collect it."
    
    if 'residence permit is being processed' in content_lower:
        return "⏳ PROCESSING - Residence permit is being processed."
    
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
    
    return "ℹ️ UNKNOWN - Status information not clearly identified"

def check_single_permesso(pratica_number, italy_tz):
    """Check single pratica status"""
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
    
    try:
        response = requests.get(url, headers=headers, timeout=30)
        
        if response.status_code != 200:
            return {
                'pratica': pratica_number,
                'status': f"❌ ERROR - HTTP {response.status_code}",
                'url': url
            }
        
        content = response.text
        content_lower = content.lower()
        
        if "accesso negato" in content_lower or "bloccata" in content_lower:
            return {
                'pratica': pratica_number,
                'status': "🚫 BLOCKED - Access denied by website",
                'url': url
            }
        
        status_text = extract_status_text(content)
        return {
            'pratica': pratica_number,
            'status': status_text,
            'url': url,
            'is_ready': 'ready' in status_text.lower()
        }
        
    except requests.exceptions.Timeout:
        return {
            'pratica': pratica_number,
            'status': "⏱️ TIMEOUT - Request timeout",
            'url': url
        }
    except Exception as e:
        return {
            'pratica': pratica_number,
            'status': f"❌ EXCEPTION - {str(e)}",
            'url': url
        }

def check_permesso():
    """Check ALL Permesso di Soggiorno statuses"""
    
    # Get ALL pratica numbers (supports multiple)
    pratica_numbers_raw = [
        os.environ.get('PRATICA_NUMBER_1'),
        os.environ.get('PRATICA_NUMBER_2'),
        os.environ.get('PRATICA_NUMBER_3')
    ]
    
    # FIXED: Strip whitespace AND filter empty
    pratica_numbers = [p.strip() for p in pratica_numbers_raw if p and p.strip()]
    
    print(f"🔍 Found {len(pratica_numbers)} valid pratiche: {pratica_numbers}")
    
    if not pratica_numbers:
        print("❌ No valid PRATICA_NUMBER_* secrets found!")
        send_notification(
            "⚠️ Configuration Error",
            "No PRATICA_NUMBER_1, PRATICA_NUMBER_2, or PRATICA_NUMBER_3 configured with valid numbers.\n\n✅ Secrets exist but contain empty/whitespace values.\n\nFix: Edit secrets and ensure they contain actual numbers like '059551999909'"
        )
        return
    
    italy_tz = ZoneInfo("Europe/Rome")
    timestamp = datetime.now(italy_tz).strftime("%Y-%m-%d %H:%M:%S")
    
    print(f"\n{'='*70}")
    print(f"🔍 Checking {len(pratica_numbers)} Permesso(s)")
    print(f"Time: {timestamp} (Italy)")
    print(f"Pratiche: {', '.join(pratica_numbers)}")
    print(f"{'='*70}\n")
    
    # Check all pratiche
    results = []
    any_ready = False
    for pratica in pratica_numbers:
        result = check_single_permesso(pratica, italy_tz)
        results.append(result)
        if result.get('is_ready'):
            any_ready = True
        print(f"📋 {pratica}: {result['status']}")
    
    # Build single email with ALL results
    email_lines = []
    
    for result in results:
        status_emoji = result['status'][0] if result['status'] and result['status'][0] in '✅⏳❌🚫⏱️' else 'ℹ️'
        email_lines.append(f"{status_emoji} **{result['pratica']}**: {result['status']}")
        if result.get('url'):
            email_lines.append(f"   🔗 {result['url']}")
        email_lines.append("")  # Empty line
    
    # Determine email type
    if any_ready:
        subject = f"🎉 PERMESSO READY! ({timestamp})"
        body = f"""🎉🎉🎉 AT LEAST ONE PERMESSO IS READY! 🎉🎉🎉

{'='*50}
📋 ALL STATUS UPDATES:
{'='*50}
"""
        body += "\n".join(email_lines)
        body += f"""
{'='*50}
⚡ GO TO QUESTURA IMMEDIATELY! ⚡
{'='*50}

Time: {timestamp} (Italy Time)
        """
    else:
        subject = f"⏳ Permesso Status Update - {timestamp}"
        body = f"""⏳ Permesso di Soggiorno Status Check

{'='*50}
📋 ALL PRACTICA STATUS:
{'='*50}
"""
        body += "\n".join(email_lines)
        body += f"""
{'='*50}
📅 Checked: {timestamp} (Italy Time)
{'='*50}

✋ No permits ready yet. Next check soon!
        """
    
    send_notification(subject, body)
    print("\n✓ All checks completed & email sent!")

if __name__ == "__main__":
    print("🔍 Starting Multi-Permesso Monitor...")
    check_permesso()
    print("\n✓ Done!")
