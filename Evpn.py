import sys
import os, subprocess
import readline
from class_definition.showTechExtendedClass import *
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

# creating a parsed object
evpntech = showTechExtended(sys.argv[1])
evpntech.command_collector()
evpntech.routing_logic() 
# giving the completer function as input to the readline for autocompleting commands
readline.parse_and_bind ("bind ^I rl_complete") 
readline.set_completer(evpntech.complete)

identifier = f"{random.randint(1, 9999999)}: {datetime.datetime.now()}"
data = f'User: {os.getlogin().capitalize()} Identifier: {identifier} evpnmode\n'
client('10.85.129.100', 2234, data)

# loop for the device console
while True:
    try:
        cli_command = ''
        bash_command = ''
        command = input(f'switch: ').strip() # strips off starting and ending whitespacese
        if command == '':
           continue
        command = re.sub(r' +', ' ', command) # removing white spaces between words if any
        # populating switch_command and bash_command variable values
        # print(evpnparsed.sed(command))
        try:
            cli_command, bash_command = command.split('|', maxsplit=1)
            cli_command = cli_command.rstrip()
        except ValueError as e:
            cli_command = command
        if bash_command:
            command_prior_pipe = evpntech.command_processor(evpntech.sed(cli_command))
            input_data = command_prior_pipe.encode()
            result = subprocess.run(bash_command, shell=True, input=input_data, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            bash_output = result.stdout.decode()
            bash_err = result.stderr.decode()
            if bash_err:
                print(bash_err)
            else:
                print(bash_output)
        else:
            print(evpntech.command_processor(evpntech.sed(cli_command)))
            
    except KeyboardInterrupt as e:
        print()
    except ValueError as e:
        print('wrong input or / notation not supported')
        pass