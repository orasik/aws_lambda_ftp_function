from __future__ import print_function
import boto3
import os
import ftplib

# AWS S3 Bucket name
bucket = ""

# FTP Credentials
ip = ""
username = ""
password = ""
remote_directory = ""
ftp_archive_folder = ""

s3_client = boto3.resource('s3')

# This function will check if a given name/path is a folder to avoid downloading it
def is_ftp_folder(ftp, filename):
    try:
        res = ftp.sendcmd('MLST ' + filename)
        if 'type=dir;' in res:
            return True
        else:
            return False
    except:
        return False


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
        if not is_ftp_folder(ftp, ftp_archive_folder):
            print("Creating archive directory {}".format(ftp_archive_folder))
            ftp.mkd(ftp_archive_folder)
    except:
        print("Error creting {} directory".format(ftp_archive_folder))

    files = ftp.nlst()

    for file in files:
        if not is_ftp_folder(ftp, file):
            try:
                if os.path.isfile("/tmp/" + file):
                    print("File {} exists locally, skip".format(file))
                    try:
                        ftp.rename(file, ftp_archive_folder + "/" + file)
                    except:
                        print("Can not move file {} to archive folder".format(file))

                else:
                    print("Downloading {} ....".format(file))
                    ftp.retrbinary("RETR " + file, open("/tmp/" + file, 'wb').write)
                    try:
                        s3_client.meta.client.upload_file("/tmp/" + file, bucket, file)
                        print("File {} uploaded to S3".format(file))

                        try:
                            ftp.rename(file, ftp_archive_folder + "/" + file)
                        except:
                            print("Can not move file {} to archive folder".format(file))
                    except:
                        print("Error uploading file {} !".format(file))
            except:
                print("Error downloading file {}!".format(file))
