import imaplib
import smtplib
from email.message import EmailMessage
from datetime import datetime
import os
import json
from typing import Optional, List, Dict

class EmailManager:
    def __init__(self):
        self.connected = False
        self.templates_path = os.path.join(os.path.dirname(__file__), 'resources', 'email_templates.json')
        self.scheduled_emails: List[Dict] = []
        self._load_templates()
        
    def _load_templates(self):
        """Load email templates from JSON file"""
        try:
            if os.path.exists(self.templates_path):
                with open(self.templates_path, 'r') as f:
                    self.templates = json.load(f)
            else:
                self.templates = {
                    'assignment_reminder': {
                        'subject': 'Assignment Reminder: {subject}',
                        'body': 'Dear {name},\n\nThis is a reminder that your {subject} assignment is due on {due_date}.\n\nBest regards,\nAnna'
                    },
                    'study_summary': {
                        'subject': 'Study Session Summary',
                        'body': 'Dear {name},\n\nHere is your study session summary for {date}:\n\nTotal study time: {duration} minutes\nTopics covered: {topics}\n\nKeep up the good work!\n\nBest regards,\nAnna'
                    }
                }
                os.makedirs(os.path.dirname(self.templates_path), exist_ok=True)
                with open(self.templates_path, 'w') as f:
                    json.dump(self.templates, f, indent=4)
        except Exception as e:
            print(f"Error loading templates: {str(e)}")
            self.templates = {}
        
    def connect(self) -> Optional[str]:
        """Connect to email server with error handling"""
        try:
            self.smtp = smtplib.SMTP_SSL('smtp.gmail.com', 465)
            self.imap = imaplib.IMAP4_SSL('imap.gmail.com')
            
            email = os.getenv('EMAIL_USER')
            password = os.getenv('EMAIL_PASS')
            
            if not email or not password:
                return "Email credentials not found in environment variables"
            
            self.smtp.login(email, password)
            self.imap.login(email, password)
            self.connected = True
            return None
        except Exception as e:
            return f"Connection failed: {str(e)}"
    def check_email(self) -> int:
        """Check for unread emails"""
        if not self.connected:
            self.connect()
        try:
            self.imap.select('inbox')
            _, data = self.imap.search(None, 'UNSEEN')
            return len(data[0].split())
        except Exception as e:
            print(f"Error checking email: {str(e)}")
            return 0
    def send_email(self, to: str, subject: str, body: str, template_name: Optional[str] = None, template_data: Optional[Dict] = None) -> Optional[str]:
        """Send an email with optional template support"""
        if not self.connected:
            result = self.connect()
            if result:
                return result

        try:
            if template_name and template_name in self.templates:
                template = self.templates[template_name]
                subject = template['subject'].format(**(template_data or {}))
                body = template['body'].format(**(template_data or {}))

            msg = EmailMessage()
            msg.set_content(body)
            msg['Subject'] = subject
            msg['From'] = os.getenv('EMAIL_USER')
            msg['To'] = to

            self.smtp.send_message(msg)
            return None
        except Exception as e:
            return f"Failed to send email: {str(e)}"

    def schedule_email(self, to: str, subject: str, body: str, send_date: datetime, 
                      template_name: Optional[str] = None, template_data: Optional[Dict] = None) -> None:
        """Schedule an email to be sent at a specific time"""
        self.scheduled_emails.append({
            'to': to,
            'subject': subject,
            'body': body,
            'send_date': send_date,
            'template_name': template_name,
            'template_data': template_data
        })

    def process_scheduled_emails(self) -> None:
        """Process and send scheduled emails"""
        current_time = datetime.now()
        remaining_emails = []

        for email in self.scheduled_emails:
            if current_time >= email['send_date']:
                result = self.send_email(
                    email['to'],
                    email['subject'],
                    email['body'],
                    email['template_name'],
                    email['template_data']
                )
                if result:
                    print(f"Failed to send scheduled email: {result}")
                    remaining_emails.append(email)
            else:
                remaining_emails.append(email)

        self.scheduled_emails = remaining_emails

    def add_template(self, name: str, subject: str, body: str) -> None:
        """Add a new email template"""
        self.templates[name] = {
            'subject': subject,
            'body': body
        }
        try:
            with open(self.templates_path, 'w') as f:
                json.dump(self.templates, f, indent=4)
        except Exception as e:
            print(f"Error saving template: {str(e)}")