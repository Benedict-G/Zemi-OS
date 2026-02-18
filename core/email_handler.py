"""
Zemi Email Handler
Handles sending and reading emails via Proton Bridge
"""

import smtplib
import imaplib
import email
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from pathlib import Path
import sys
sys.path.append('/Users/zemi/ZemiV1/core')
from vault import SecureVault

class EmailHandler:
    def __init__(self):
        self.vault = SecureVault('/Users/zemi/ZemiV1/vault')
        self.creds = self.vault.get_credentials('proton.enc')
        print("📧 Email handler initialized")
    
    async def send_email(self, to, subject, body, tone="professional"):
        """Send email via Proton Bridge SMTP"""
        
        print(f"📤 Sending email to: {to}")
        
        try:
            # Create message
            msg = MIMEMultipart()
            msg['From'] = self.creds['username']
            msg['To'] = to
            msg['Subject'] = subject
            msg.attach(MIMEText(body, 'plain'))
            
            # Connect to Proton Bridge SMTP
            with smtplib.SMTP(
                self.creds['smtp_host'],
                self.creds['smtp_port']
            ) as server:
                server.starttls()
                server.login(
                    self.creds['username'],
                    self.creds['password']
                )
                server.send_message(msg)
            
            print(f"✅ Email sent to {to}")
            return f"✅ Email sent successfully to {to}!\nSubject: {subject}"
            
        except Exception as e:
            return f"❌ Failed to send email: {str(e)}"
    
    async def read_emails(self, folder="INBOX", limit=5):
        """Read recent emails via Proton Bridge IMAP"""
        
        print(f"📥 Reading emails from {folder}")
        
        try:
            # Connect to Proton Bridge IMAP
            mail = imaplib.IMAP4(
                self.creds['imap_host'],
                self.creds['imap_port']
            )
            
            mail.login(
                self.creds['username'],
                self.creds['password']
            )
            
            mail.select(folder)
            
            # Get recent emails
            _, messages = mail.search(None, 'ALL')
            email_ids = messages[0].split()
            
            # Get last N emails
            recent_ids = email_ids[-limit:] if len(email_ids) > limit else email_ids
            
            emails = []
            for email_id in reversed(recent_ids):
                _, msg_data = mail.fetch(email_id, '(RFC822)')
                msg = email.message_from_bytes(msg_data[0][1])
                
                emails.append({
                    'from': msg['From'],
                    'subject': msg['Subject'],
                    'date': msg['Date'],
                    'body': self._get_body(msg)
                })
            
            mail.logout()
            return self._format_emails(emails)
            
        except Exception as e:
            return f"❌ Failed to read emails: {str(e)}"
    
    def _get_body(self, msg):
        """Extract email body"""
        if msg.is_multipart():
            for part in msg.walk():
                if part.get_content_type() == "text/plain":
                    return part.get_payload(decode=True).decode()[:500]
        else:
            return msg.get_payload(decode=True).decode()[:500]
        return ""
    
    def _format_emails(self, emails):
        """Format emails for display"""
        
        if not emails:
            return "📭 No emails found"
        
        response = f"📬 **Recent Emails ({len(emails)}):**\n\n"
        
        for i, email in enumerate(emails, 1):
            response += f"**{i}. {email['subject']}**\n"
            response += f"From: {email['from']}\n"
            response += f"Date: {email['date']}\n"
            response += f"{email['body'][:200]}...\n\n"
        
        return response

# Test
if __name__ == "__main__":
    import asyncio
    
    async def test():
        handler = EmailHandler()
        # Test reading emails
        result = await handler.read_emails(limit=3)
        print(result)
    
    asyncio.run(test())

