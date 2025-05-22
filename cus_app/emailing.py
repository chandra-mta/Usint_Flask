"""
**emailing.py**: Module for notification functions

:Author: W. Aaron (william.aaron@cfa.harvard.edu)
:Last Updated: May 22, 2025

"""

import sys
import os
from flask          import current_app, flash
from flask_login    import current_user
from email.message import EmailMessage
from subprocess import Popen, PIPE

CUS  = 'cus@cfa.harvard.edu'

def send_email(content, subject, to, cc = []):
    """
    Send Email Notification
    """

    msg = EmailMessage()
    msg.set_content(content)
    msg['Subject'] = subject
    msg['To'] = to
    msg['CC'] = [CUS] + cc
    #: Print message instead of sending it if configured to test notifications
    if current_app.config['TEST_NOTIFICATIONS']:
        print(msg.as_string())
    else:
        p = Popen(["/sbin/sendmail", "-t", "-oi"], stdin=PIPE)
        (out, error) = p.communicate(msg.as_bytes())
