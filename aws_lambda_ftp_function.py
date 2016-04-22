from __future__ import print_function
import boto3
import os
import ftplib

#AWS S3 Bucket name
bucket = ""

# FTP Credentials
ip = ""
username = ""
password = ""
remote_directory = ""
# In Lambda, you only have access to /tmp folder. If you want to download files to a directory inside /tmp
# please change the follow to: /tmp/folder_name
local_directory = "/tmp/"

# This function will check if a given name/path is a folder to avoid downloading it
def is_ftp_folder(filename):
    try:
        res = ftp.sendcmd('MLST ' + filename)
        if 'type=dir;' in res:
            return True
        else:
            return False
    except:
        return False

# This is required by AWS lambda. Main function should be called lambda_handler
def lambda_handler(event, context):
    # Connecting to FTP
    try:
        ftp = ftplib.FTP(ip)
        ftp.login(username, password)
    except:
        print("Error connecting to FTP")

    try:
        ftp.cwd(remote_directory)
    except:
        print("Error changing to directory {}".format(remote_directory))

    try:
        files = ftp.nlst()
    except:
        print("Error listing files in {} directory".format(remote_directory))


    if not os.path.exists(local_directory):
        os.makedirs(local_directory)
        print("Created local directory {}".format(local_directory))

    # AWS Python SDK
    s3_client = boto3.resource('s3')

    for file in files:
        if not is_ftp_folder(file):
            try:
                if os.path.isfile(local_directory + "/" + file):
                    print("File {} exists locally, skip".format(file))
                    try:
                        s3_client.meta.client.upload_file(local_directory + "/" + file, bucket, file)
                        print("File {} uploaded to S3".format(file))
                    except:
                        print("Error uploading file {} !".format(file))
                else:
                    print("Downloading {} ....".format(file))
                    ftp.retrbinary("RETR " + file, open(local_directory + "/" + file, 'wb').write)
                    try:
                        s3_client.meta.client.upload_file(local_directory + "/" + file, bucket, file)
                        print("File {} uploaded to S3".format(file))
                    except:
                        print("Error uploading file {} !".format(file))
            except:
                print("Error downloading file {}!".format(file))
