"""
**emailing.py**: Module for notification functions

:Author: W. Aaron (william.aaron@cfa.harvard.edu)
:Last Updated: May 22, 2025

"""

import sys
import os
from datetime import datetime
from flask          import current_app, flash
from flask_login    import current_user
from email.message import EmailMessage
from subprocess import Popen, PIPE

CUS  = 'cus@cfa.harvard.edu'

def construct_msg(content, subject, to, sender = None, cc = []):
    """
    Construct Email Instance
    """
    msg = EmailMessage()
    msg.set_content(content)
    msg['Subject'] = subject
    msg['To'] = to
    if sender is not None:
        msg['From'] = sender
    msg['CC'] = [CUS] + cc
    return msg

def send_msg(msg):
    """
    Send Email Instance
    """
    #: Print message instead of sending it if configured to test notifications
    if current_app.config['TEST_NOTIFICATIONS']:
        print(msg.as_string())
    else:
        p = Popen(["/sbin/sendmail", "-t", "-oi"], stdin=PIPE)
        (out, error) = p.communicate(msg.as_bytes())
        if error is not None:
            current_app.logger.error(error)
            flash("Error sending notification email. Check Inbox.")
            send_error_email()

def send_email(content, subject, to, sender = None, cc = []):
    """
    Combined send email function.

    :NOTE: This functionality is split only to allow cases in which we'd like to prepare sending emails in bulk before actually sending them.
    In typical usage, the send_email() function will be used across the board.
    """
    msg = construct_msg(content, subject, to, sender = None, cc = [])
    send_msg(msg)
    

def send_error_email(e=None,logline=None):
    if not current_app.debug:
        handler_list = current_app.logger.handlers
        for item in handler_list:
            if item.name == "Error-Info":
                error_handler = item
                break
        file_path = error_handler.baseFilename
        #Once the log path is found, must search the file to send email contents
        with open(file_path,'r') as f:
            content = f.read()
        content = f"User: {current_user}\n\nocat.log:\n{content}"
        msg = EmailMessage()
        msg.set_content(content)
        msg['Subject'] = f"Usint Error-[{datetime.now().strftime('%c')}]"
        msg['To'] = current_app.config['ADMINS']
        msg['From'] = "UsintErrorHandler"
        p = Popen(["/sbin/sendmail", "-t", "-oi"], stdin=PIPE)
        (out, error) = p.communicate(msg.as_bytes())
        
    else:
        if e is not None:
            #
            #--- File logger has not been initialized for the UsintErrorHandler as we are using the Werkzeug Browser Debugger instead.
            #--- If error passed, then raise in the Werkzeug Browser Debugger.
            #
            raise e
        if logline is not None:
            print(logline)