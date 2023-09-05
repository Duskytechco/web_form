# import pysftp
# import os

# #just install pip install pysftp

# cnopts = pysftp.CnOpts()
# cnopts.hostkeys = None    # disable host key checking.

# hostname = 'dusky.bond'
# username = 'admin'
# password = 'Aiss2017b536442.'
# remote_directory = '/Development/test'
# local_file = '/home/admin/test/SFTP TRANSFER FILE.py' 

# try:
#   with pysftp.Connection(hostname, username=username, password=password, cnopts=cnopts) as sftp:
#       with sftp.cd(remote_directory):  # change directory to `remote_directory`
#           # os.system('xdg-open ' + local_file)
#           sftp.put(local_file, remote_directory)  # upload local_file to remote_direc>
#     # upload local_file to remote_directory on remote
#   print("File uploaded successfully")

# except pysftp.ConnectionException as e:
#     print("Connection error:", str(e))

# except pysftp.AuthenticationException as e:
#     print("Authentication error:", str(e))

# except Exception as e:
#     print("An error occurred:", str(e))



# import paramiko
# import os

# hostname = 'dusky.bond'
# username = 'admin'
# password = 'Aiss2017b536442.'
# remote_directory = '/Development/test'
# local_file = '/home/admin/test/SFTP TRANSFER FILE.py'

# # Create an SSH client instance
# client = paramiko.SSHClient()
# client.set_missing_host_key_policy(paramiko.AutoAddPolicy())  # Auto-add host key (not recommended for production)

# try:
#     client.connect(hostname, username=username, password=password)

#     # Use SFTP to upload the file
#     with client.open_sftp() as sftp:
#         sftp.put(local_file, remote_directory + '/' + os.path.basename(local_file))
#     print("File uploaded successfully")

# except paramiko.AuthenticationException as e:
#     print("Authentication error:", str(e))

# except paramiko.SSHException as e:
#     print("SSH error:", str(e))

# except Exception as e:
#     print("An error occurred:", str(e))

# finally:
#     client.close()











import paramiko
import os
import psutil  # Import the psutil library
import sys

pdfFile = sys.argv[1]
print(f"Received PDF File: {pdfFile}")

hostname = '207.148.121.38'
username = 'admin'
password = 'Aiss2017b536442.'
remote_directory = '/Development/Webform/Webform/WEBFORM/pdfFiles'
local_file = f"webform/{pdfFile}"

# Create an SSH client instance
client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())  # Auto-add host key (not recommended for production)

try:
    client.connect(hostname, username=username, password=password)

    # Get the initial memory usage
    initial_memory = psutil.virtual_memory().used

    # Use SFTP to upload the file
    with client.open_sftp() as sftp:
        sftp.put(local_file, remote_directory + '/' + os.path.basename(local_file))

    # Get the memory usage after the transfer
    final_memory = psutil.virtual_memory().used
    memory_used = final_memory - initial_memory

    print("File uploaded successfully")
    print(f"Memory used during transfer: {memory_used} bytes")

except paramiko.AuthenticationException as e:
    print("Authentication error:", str(e))

except paramiko.SSHException as e:
    print("SSH error:", str(e))

except Exception as e:
    print("An error occurred:", str(e))

finally:
    client.close()
