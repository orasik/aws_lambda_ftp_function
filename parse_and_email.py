from __future__ import print_function

import urllib
import boto3
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

print('Loading function')
s3 = boto3.resource('s3')
local_folder = "/tmp/"

def sendMail(FROM,TO,SUBJECT,TEXT):
    import smtplib
    # your AWS SES smtp
    SERVER = ''
    EMAIL_USERNAME = ''
    EMAIL_PASSWORD = ''
    """this is some test documentation in the function"""
    msg = MIMEMultipart()
    msg['From'] = FROM
    msg['To'] = TO
    msg['Subject'] = SUBJECT
    part1 = MIMEText(TEXT, 'plain', 'utf-8')
    msg.attach(part1)
    # if you want to send HTML email, uncomment the following two lines
    # part2 = MIMEText(TEXT, 'html', 'utf-8')
    #msg.attach(part2)

    # Send the mail
    server = smtplib.SMTP(SERVER)
    "New part"
    server.starttls()
    server.login(EMAIL_USERNAME, EMAIL_PASSWORD)
    server.sendmail(FROM, TO, msg.as_string())
    server.quit()


def lambda_handler(event, context):

    # Get the object from the event and show its content type
    bucket = event['Records'][0]['s3']['bucket']['name']
    key = urllib.unquote_plus(event['Records'][0]['s3']['object']['key']).decode('utf8')
    try:
        print("Saving file {} to folder {}".format(key,local_folder))
        s3.Bucket(bucket).download_file(key, local_folder+key)
        with open(local_folder+key, 'r') as content_file:
            content = content_file.read()
            print(content)

            try:
                sendMail('email@example.com','email@example.com', 'File '+ key , content)
                print("Email sent with subject {}".format(key))
            except Exception as e:
                print(e)
                raise(e)
    except Exception as e:
        print(e)
        print('Error getting object {} from bucket {}. Make sure they exist and your bucket is in the same region as this function.'.format(key, bucket))
        raise e