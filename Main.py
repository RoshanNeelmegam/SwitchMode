import sys, os
import readline
from class_definition.showTechClass import *
import traceback, logging
import random, datetime
import socket

def proc(command):
    switch_command = ''
    bash_command = ''
    command = re.sub(r' +', ' ', command) # removing white spaces between words if any
    try:
        switch_command, bash_command = command.split('|', maxsplit=1)
        switch_command = switch_command.rstrip()
    except ValueError as e:
        switch_command = command
    if bash_command:
        command_prior_pipe = showtech.command_processor(switch_command)
        input_data = command_prior_pipe.encode()
        result = subprocess.run(bash_command, shell=True, input=input_data, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        bash_output = result.stdout.decode()
        bash_err = result.stderr.decode()
        if bash_err:
            print(bash_err)
        else:
            print(bash_output)
    else:
        print(showtech.command_processor(switch_command))

identifier = f"{random.randint(1, 9999999)}: {datetime.datetime.now()}"

def init(verbose=None):
    if verbose:
        showtech = ShowTech(sys.argv[1]) 
        print("ShowTech Initialized")
        showtech.show_tech_commands_modifier() 
        print("Commands Modified")
        showtech.get_hostname() 
        showtech.gather_commands() 
        print('Command Dictionary Created')
        print('Parsing ipv4 and ipv6 Routing Table')
        showtech.routing_logic() 
        print("Routing Parsed")
        readline.parse_and_bind ("bind ^I rl_complete") 
        readline.set_completer(showtech.complete)
    else:
        showtech = ShowTech(sys.argv[1]) 
        showtech.show_tech_commands_modifier() 
        showtech.get_hostname() 
        showtech.gather_commands() 
        showtech.routing_logic() 
    return showtech

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

if (len(sys.argv)-1 == 1):
    data = f'User: {os.getlogin().capitalize()} Identifier: {identifier} shellmode\n'
    client('10.85.129.100', 2234, data)
    showtech = init(verbose=True)
    # Loop for the device console
    commandList = []
    while True:
        try:
            command = input(f'{showtech.hostname}: ').strip() # strips off starting and ending whitespacese
            if command == '':
               continue
            elif command == 'exit':
               closing_data = f'''-----------
User: {os.getlogin()} 
Identifier: {identifier} 
file: {sys.argv[1]} 
{commandList}
-----------\n'''
               client('10.85.129.100', 2235, closing_data)
               sys.exit()
            commandList.append(command)
            proc(command)
        except KeyboardInterrupt as e:
            print()
        except ValueError as e:
            print('wrong input or / notation not supported')
            pass
        except Exception as e:
            logging.error(traceback.format_exc())
            exception_data = f'''-----------
User: {os.getlogin()} 
Identifier: {identifier} 
file: {sys.argv[1]} 
command: {command}
exception: {traceback.format_exc()}
-----------\n'''
            if client('10.85.129.100', 2246, exception_data):
                print("NOTIFIED EXCEPTION TO SERVER")
            else:
                print("CONNECTION TO SERVER FAILED. PLEASE NOTIFY MANUALLY")
elif (len(sys.argv)-1 == 2):
    showtech = init()
    command = sys.argv[-1].strip()
    try:
        if command == '':
           sys.exit()
        proc(command)
    except KeyboardInterrupt as e:
        print()
    except ValueError as e:
        print('wrong input or / notation not supported')
        pass