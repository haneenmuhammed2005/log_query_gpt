# Alert System — detects critical keywords and sends email alerts
import smtplib
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
from typing import Optional

# ── Critical keyword categories ───────────────────────────────────────────────
CRITICAL_KEYWORDS = [
    "brute force", "brute-force", "attack", "intrusion", "unauthorized",
    "authentication failure", "authentication failed", "auth failure",
    "failed login", "login failed", "multiple failed", "repeated failure",
    "blocked", "critical", "malware", "exploit", "suspicious",
    "anomaly", "threat", "breach", "compromised", "escalation",
    "privilege escalation", "root access", "fatal", "kernel panic",
    "memory corruption", "hardware failure", "node failure",
    "excessive", "flood", "denial of service", "dos attack",
]

def detect_severity(answer: str, query: str) -> Optional[str]:
    """
    Scan AI answer for critical keywords.
    Returns severity level or None if nothing critical found.
    """
    text = (answer + " " + query).lower()

    critical_hits = [kw for kw in CRITICAL_KEYWORDS if kw in text]

    if not critical_hits:
        return None

    # Determine severity level
    high_severity = ["attack", "brute force", "intrusion", "unauthorized", "malware",
                     "exploit", "breach", "compromised", "dos attack", "fatal", "kernel panic"]

    if any(kw in text for kw in high_severity):
        return "CRITICAL"
    return "WARNING"

def build_email_html(query: str, answer: str, severity: str,
                     dataset: str, response_time: float, username: str) -> str:
    """Build a clean HTML email body"""
    color = "#ff4444" if severity == "CRITICAL" else "#ffaa00"
    now   = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Truncate answer for email
    answer_short = answer[:800] + "..." if len(answer) > 800 else answer
    answer_html  = answer_short.replace("\n", "<br>")

    return f"""
<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<style>
  body {{ font-family: 'Segoe UI', Arial, sans-serif; background: #0a0f1e; color: #e2e8f0; margin: 0; padding: 20px; }}
  .container {{ max-width: 680px; margin: 0 auto; background: #0f1929; border-radius: 12px; overflow: hidden; border: 1px solid rgba(255,255,255,0.08); }}
  .header {{ background: linear-gradient(135deg, #0a1628, #0f1f3d); padding: 28px 32px; border-bottom: 2px solid {color}; }}
  .badge {{ display: inline-block; background: {color}22; border: 1px solid {color}; color: {color}; padding: 4px 14px; border-radius: 20px; font-size: 12px; font-weight: 700; letter-spacing: 0.1em; margin-bottom: 10px; }}
  .title {{ font-size: 22px; font-weight: 800; color: #e2e8f0; margin: 0; }}
  .subtitle {{ font-size: 13px; color: #5a7a9a; margin-top: 4px; }}
  .body {{ padding: 28px 32px; }}
  .section-label {{ font-size: 10px; font-weight: 700; color: #3a5a7a; text-transform: uppercase; letter-spacing: 0.15em; margin-bottom: 6px; }}
  .info-box {{ background: rgba(255,255,255,0.04); border: 1px solid rgba(255,255,255,0.07); border-radius: 8px; padding: 14px 18px; margin-bottom: 16px; font-size: 13px; color: #a0c0dc; line-height: 1.7; }}
  .meta-row {{ display: flex; justify-content: space-between; padding: 8px 0; border-bottom: 1px solid rgba(255,255,255,0.05); font-size: 12px; }}
  .meta-label {{ color: #5a7a9a; }}
  .meta-value {{ color: #8ab0d0; font-weight: 600; }}
  .footer {{ padding: 18px 32px; background: rgba(0,0,0,0.2); text-align: center; font-size: 11px; color: #3a5a7a; border-top: 1px solid rgba(255,255,255,0.05); }}
  .severity-bar {{ height: 3px; background: linear-gradient(90deg, {color}, transparent); margin-bottom: 0; }}
</style>
</head>
<body>
<div class="container">
  <div class="severity-bar"></div>
  <div class="header">
    <div class="badge">{severity} ALERT</div>
    <div class="title">ICS-LogQueryGPT Security Alert</div>
    <div class="subtitle">Automated threat detection — {now}</div>
  </div>
  <div class="body">
    <div class="section-label">Query That Triggered Alert</div>
    <div class="info-box">{query}</div>

    <div class="section-label">AI Analysis Result</div>
    <div class="info-box">{answer_html}</div>

    <div class="section-label">Alert Details</div>
    <div class="info-box" style="padding: 0 18px;">
      <div class="meta-row"><span class="meta-label">Severity</span><span class="meta-value" style="color:{color};">{severity}</span></div>
      <div class="meta-row"><span class="meta-label">Dataset</span><span class="meta-value">{dataset}</span></div>
      <div class="meta-row"><span class="meta-label">Response Time</span><span class="meta-value">{response_time}s</span></div>
      <div class="meta-row"><span class="meta-label">Triggered By</span><span class="meta-value">{username}</span></div>
      <div class="meta-row" style="border:none;"><span class="meta-label">Timestamp</span><span class="meta-value">{now}</span></div>
    </div>
  </div>
  <div class="footer">
    ICS-LogQueryGPT v1.0 — Automated Security Alert System<br>
    This alert was sent because critical keywords were detected in the AI analysis.
  </div>
</div>
</body>
</html>
"""

def send_alert_email(
    query: str,
    answer: str,
    severity: str,
    dataset: str,
    response_time: float,
    username: str,
    recipient_email: str = "haneenmuhammed2005@gmail.com"
) -> tuple[bool, str]:
    """
    Send alert email via Gmail SMTP.
    Returns (success, message)
    """
    sender_email = os.environ.get("ALERT_EMAIL", "haneenmuhammed2005@gmail.com")
    app_password  = os.environ.get("ALERT_EMAIL_PASSWORD", "kmswydnfnazhszja")

    subject = f"[{severity}] ICS-LogQueryGPT Security Alert — {datetime.now().strftime('%Y-%m-%d %H:%M')}"

    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"]    = f"ICS-LogQueryGPT Alerts <{sender_email}>"
    msg["To"]      = recipient_email

    # Plain text fallback
    plain = f"""
ICS-LogQueryGPT SECURITY ALERT — {severity}

Query: {query}

AI Analysis:
{answer[:500]}

Details:
- Severity: {severity}
- Dataset: {dataset}
- Response Time: {response_time}s
- Triggered By: {username}
- Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

-- ICS-LogQueryGPT Automated Alert System
"""
    html = build_email_html(query, answer, severity, dataset, response_time, username)

    msg.attach(MIMEText(plain, "plain"))
    msg.attach(MIMEText(html,  "html"))

    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(sender_email, app_password)
            server.sendmail(sender_email, recipient_email, msg.as_string())
        return True, f"Alert email sent to {recipient_email}"
    except smtplib.SMTPAuthenticationError:
        return False, "Email authentication failed. Check your App Password."
    except smtplib.SMTPException as e:
        return False, f"SMTP error: {str(e)}"
    except Exception as e:
        return False, f"Failed to send email: {str(e)}"
