import os
import subprocess
import sys
import random, datetime
import socket

def client(server_to_connect, port, data):
    try:
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client.settimeout(1)
        client.connect((server_to_connect, port))
        client.send(data.encode("utf-8"))
        return True
    except Exception as e:
       return False
    finally:
       client.close()

directory_path = sys.argv[1]
sw_command = sys.argv[2]
current_script_dir = os.path.dirname(os.path.realpath(__file__))
filenames = sorted(os.listdir(directory_path), key=lambda x: os.path.getmtime(os.path.join(directory_path, x)), reverse=False)

identifier = f"{random.randint(1, 9999999)}: {datetime.datetime.now()}"
data = f'User: {os.getlogin().capitalize()} Identifier: {identifier} historymode\n'
client('10.85.129.100', 2234, data)

for filename in filenames:
    try:
        file_path = os.path.join(directory_path, filename)
        main_script_path = os.path.join(current_script_dir, "Main.py")
        command = f"python3 {main_script_path} {file_path} '{sw_command}'"
        print(filename)
        result = subprocess.run(command, shell=True, stdout=subprocess.PIPE, text=True)
        print(result.stdout)
        print('*'*20+'\n')
    except KeyboardInterrupt as e:
        print("Aborting command")
        sys.exit()


