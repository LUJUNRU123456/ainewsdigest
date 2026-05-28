#!/usr/bin/env python3
"""Send HTML email via Brevo SMTP. Called by the ainewsdigest skill."""
import smtplib, os, sys, yaml
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
from pathlib import Path

# Config path: same directory as this script's parent (the skill dir)
SKILL_DIR = Path(__file__).resolve().parent.parent
CONFIG_PATH = SKILL_DIR / 'mail_config.yaml'

if not CONFIG_PATH.exists():
    print(f"ERROR: Config not found at {CONFIG_PATH}")
    sys.exit(1)

with open(CONFIG_PATH, 'r', encoding='utf-8') as f:
    config = yaml.safe_load(f)

smtp_cfg = config['smtp']
recipients = config['recipients']
subject_prefix = config['email_settings']['subject_prefix']

smtp_key = os.environ.get('EMAIL_PASSWORD')
if not smtp_key:
    print("ERROR: EMAIL_PASSWORD environment variable not set")
    sys.exit(1)

# HTML file: first CLI arg, or default path
html_path = sys.argv[1] if len(sys.argv) > 1 else str(SKILL_DIR / 'email_output.html')
if not os.path.exists(html_path):
    print(f"ERROR: HTML file not found: {html_path}")
    sys.exit(1)

with open(html_path, 'r', encoding='utf-8') as f:
    html_content = f.read()

# Subject with date
now = datetime.now()
weekday_names = ['周一','周二','周三','周四','周五','周六','周日']
weekday = weekday_names[now.weekday()]
date_str = f"{now.year}年{now.month}月{now.day}日"

msg = MIMEMultipart('alternative')
msg['Subject'] = f"{subject_prefix} | {date_str} {weekday}"
msg['From'] = f"{smtp_cfg['sender_name']} <{smtp_cfg['sender_email']}>"
msg['To'] = ', '.join(recipients)
msg.attach(MIMEText(html_content, 'html', 'utf-8'))

try:
    server = smtplib.SMTP(smtp_cfg['server'], smtp_cfg['port'], timeout=30)
    server.starttls()
    server.login(smtp_cfg['username'], smtp_key)
    server.sendmail(smtp_cfg['sender_email'], recipients, msg.as_string())
    server.quit()
    print("SUCCESS: Email sent!")
except Exception as e:
    print(f"SMTP ERROR: {e}")
    sys.exit(1)
