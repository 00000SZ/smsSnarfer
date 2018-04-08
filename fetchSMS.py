#!/usr/local/bin/python
# -*- coding: utf-8 -*-
import imaplib, sys, email, email.header, datetime, re, base64, getpass, time, configparser
from slackclient import SlackClient

config = configparser.RawConfigParser()
config.read('config.ini')
imapServer = config.get('email', 'imapServer')
imapPort = config.getint('email', 'imapPort')
imapUsername = config.get('email', 'imapUsername')
imapPassword = config.get('email', 'imapPassword')
imapFolder = config.get('email', 'imapFolder')
slackToken = config.get('slack', 'slackToken')
slackChannel = config.get('slack', 'slackChannel')
slackUsername = config.get('slack', 'slackUsername')

print("""\
--------------------------------------------------------------------------------------
  ██████ ███▄ ▄███▓ ██████      ██████ ███▄    █ ▄▄▄      ██▀███   █████▓█████ ██▀███
▒██    ▒▓██▒▀█▀ ██▒██    ▒    ▒██    ▒ ██ ▀█   █▒████▄   ▓██ ▒ ██▓██   ▒▓█   ▀▓██ ▒ ██▒
░ ▓██▄  ▓██    ▓██░ ▓██▄      ░ ▓██▄  ▓██  ▀█ ██▒██  ▀█▄ ▓██ ░▄█ ▒████ ░▒███  ▓██ ░▄█ ▒
  ▒   ██▒██    ▒██  ▒   ██▒     ▒   ██▓██▒  ▐▌██░██▄▄▄▄██▒██▀▀█▄ ░▓█▒  ░▒▓█  ▄▒██▀▀█▄
▒██████▒▒██▒   ░██▒██████▒▒   ▒██████▒▒██░   ▓██░▓█   ▓██░██▓ ▒██░▒█░   ░▒████░██▓ ▒██▒
▒ ▒▓▒ ▒ ░ ▒░   ░  ▒ ▒▓▒ ▒ ░   ▒ ▒▓▒ ▒ ░ ▒░   ▒ ▒ ▒▒   ▓▒█░ ▒▓ ░▒▓░▒ ░   ░░ ▒░ ░ ▒▓ ░▒▓░
░ ░▒  ░ ░  ░      ░ ░▒  ░ ░   ░ ░▒  ░ ░ ░░   ░ ▒░ ▒   ▒▒ ░ ░▒ ░ ▒░░      ░ ░  ░ ░▒ ░ ▒░
░  ░  ░ ░      ░  ░  ░  ░     ░  ░  ░    ░   ░ ░  ░   ▒    ░░   ░ ░ ░      ░    ░░   ░
      ░        ░        ░           ░          ░      ░  ░  ░              ░  ░  ░
---------------------------------------------------------------------------------------
https://github.com/00000sz/smsSnarfer
""")

print "\nSetting up..."
try:
    mail = imaplib.IMAP4_SSL(imapServer, imapPort)
    r, d = mail.login(imapUsername, imapPassword)
    sc = SlackClient(slackToken)
except:
    print "Login failed"
    exit(1)
print r
print "\nStarting pollers...\n"
while True:
    #print "\nSearching the " + imapFolder + " folder"
    mail.select(imapFolder)
    r, mids = mail.search(None,'UNSEEN')
    mids = mids[0].split()
    if len(mids) > 0:
        print "Found "+str(len(mids))+" emails...\n"
        for mid in mids:
            if mid:
                r, mdata = mail.fetch(mid, '(rfc822)')
                raw_email = mdata[0][1]
                email_message = email.message_from_string(raw_email)
                msubject = email_message['Subject']
                mfrom = email_message['From']
                if email_message.is_multipart():
                    for payload in email_message.get_payload():
                        mbody = (
                            payload.get_payload()
                            .split(email_message['from'])[0]
                            .split('\r\n\r\n2015')[0]
                        )
                else:
                    mbody = (
                        email_message.get_payload()
                        .split(email_message['from'])[0]
                        .split('\r\n\r\n2015')[0]
                    )
                mpayload = base64.b64decode(mbody)
                print "MessageId: " +str(mid)
                print "From: "+mfrom
                print "Subject: "+msubject
                try:
                    msource = re.search('SMS from (\d+)', msubject).group(1)
                except AttributeError:
                    print "Invalid subject"
                if msource:
                    print "---------------"
                    print msource
                    print "Payload: "+mpayload
                    print "---------------"
                    print "Processing..."
                    sc.api_call(
                        "chat.postMessage",
                        channel=slackChannel,
                        username=slackUsername,
                        text="SMS from "+msource+": "+mpayload
                    )
                    print "Sent to Slack!\n"
                else:
                    pass
            else:
                pass

            #print "Marking messageid "+str(mid)+" as read\n"
            #mail.store(mid.replace(' ',','),'+FLAGS','\SEEN')

    time.sleep(5)
