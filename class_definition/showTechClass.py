import re
import readline
import subprocess 
import sys
import os
import gzip
from command_modules.routeLookup import *
from command_modules.ipv6_routeLookup import *
from command_modules.showRunSection import *
from command_modules.customCommandMapper import *
from command_modules.showLogging import *
from command_modules.lldpNeighbors import *
from io import StringIO
from command_modules.vlaninfo import *
from command_modules.bgpCommands import *


class ShowTech:
    def __init__(self, file):
        if os.path.isfile(file):
            file_type = os.path.splitext(file)[1]
            if file_type == '.gz':
                with gzip.open(file) as f:
                    self.file_content = f.read().decode()
            else:
                with open(file) as f:
                    self.file_content = f.read()
        else:
            print(f"wrong file provided or file doesn't exist")
            sys.exit()
        self.hostname = 'Switch'
        self.cmd_dictionary = {} # holds all the commands present in the show tech as a heirarchy 
        self.allCommands = [] # holds all the commands present in the show tech
        self.routes = {} # holds all vrf routes 
        self.lldp_dictionary = {} # holds lldp information
        try:
            lldpNeighborsInitialization(self.command_searcher('show lldp neighbors detail'), self.lldp_dictionary)
        except IndexError as e:
            print('"show lldp neighbors" is not accurate. Please use "show lldp neighbors detail" for proper info.')
            pass
    
    # gathers all commands and stores in a list, which is used later in autocomplete and when user presses ?
    def gather_commands(self):
        self.allCommands = re.findall('------------- (show.*|bash.*) -------------', self.file_content)
        self.newallCommands = [item + ' <cr>' for item in self.allCommands if item.startswith('show')]
        self.newallCommands += ['show running-config section <section to check for>', 'show running-config interfaces <ethernet or port-channel or svi> ', 'show ip interface brief <cr>', 'show interfaces ethernet <ethernet-no> status <cr>', 'show interfaces port-channel <port-channel no> status <cr>', 'show interfaces management <management no> status <cr>', 'show interfaces ethernet <ethernet-no> mac-detail <cr>', 'show interfaces ethernet <ethernet-no> phy-detail <cr>', 'show interfaces port-channel <port-channel no> <cr>', 'show interfaces vlan <vlan no> <cr>', 'show interfaces ethernet <ethernet no>', 'show ip route host', 'show ip route summary', 'show ip route vrf *word host', 'show ip route vrf *word summary']
        self.newallCommands += [item for item in self.allCommands if item.startswith('bash')]
        for cmd in self.newallCommands:
            parts = cmd.split() # splitting the commands => parts = ['show version detail', 'show interfaces status', ..]
            temp_dict = self.cmd_dictionary # using a temporary dictionay used later in the iteration. For each command iteration, temp_dict now points to the original cmd_dictionary
            for part in parts: # splitting the commmands itself => ['show' 'version', 'detail'] to check if element exists in dictionary. If not populates it
                if part not in temp_dict: 
                    temp_dict[part] = {}
                temp_dict = temp_dict[part] # now temp dict point to the empty dictionary of the key {part}. Eg cmd_dictionry = {show: {} <-- temp_dict}
        # some showtechs have a differnt command for show the interfaces status. Depending on what is present on the show tech, we will call that
        self.nz_commands = [item.replace(' | nz', '') for item in self.allCommands if '| nz' in item]
        mod_cmds = [re.sub(r'interfaces all', 'interfaces', item) for item in self.newallCommands]
        self.newallCommands = mod_cmds

    def show_tech_commands_modifier(self):
        # function to modify the commandds in the show tech for easier parsing
        self.file_content = re.sub(r'------------- show interface ', '------------- show interfaces ', self.file_content, flags=re.MULTILINE)
        self.file_content = re.sub(r'------------- show interfaces vxlan .* -------------', '------------- show interfaces vxlan1 -------------', self.file_content, flags=re.MULTILINE)
        self.file_content = re.sub(r'------------- show running-config sanitized -------------', '------------- show running-config -------------', self.file_content, flags=re.MULTILINE)

    def command_searcher(self, command):
        pattern = fr'------------- {command} -------------'
        first_match = re.search(pattern, self.file_content)
        # if there's any match for the command
        if first_match:
            next_pattern = r'------------- (show|bash).*'
            second_match = re.search(next_pattern, self.file_content[first_match.end():])
            if second_match:
                output = self.file_content[first_match.start():(first_match.end() + second_match.start() - 1)]
                return output
            else:
                output = self.file_content[first_match.start():]
                return output
        else:
            return ('wrong or incomplete command')
 
    # gets the hostname and gets it assigend to a variable
    def get_hostname(self):
        for line in self.command_searcher('show running-config').splitlines():
            searches = re.search(r'^hostname\s+(.+)$', line)
            if searches:
                self.hostname = searches.group(1)
                break

    # parses the routing table and returns a dictionary of vrf routes
    def routing_logic(self):
        # for ipv4
        # Route loookup Logic. Parsing the whole route output as follows vrf_routing_table = (vrf-default: {10.0.0.0/24: {binary-eq: 00001010.00000000.00000000.00000000, prefix: 24}})
        self.routing_contents = self.command_searcher('show ip route vrf all detail') # has the ouput of the command show ip route vrf all detail
        self.routing_contents += '\nVRF: Table_Ends_Here' # this line has been added for a regex match used when user inputs the last avaialble vrf on the device
        self.vrf_routing_table = {}
        self.matched_routes = [] # holds the matched ip's in a specifif vrf for an ip inputted by the user
        parsing_routing_table(self.routing_contents, self.routes)
        for vrf in self.routes:  
            self.vrf_routing_table[vrf] = creating_vrf_routing_table(self.routes[vrf])
        # for ipv6
        self.ipv6_routing_contents = self.command_searcher('show ipv6 route vrf all detail')
        self.ipv6_routing_contents += '\nVRF: Table_Ends_Here' 
        self.ipv6_vrf_routing_table = (creating_ipv6_vrf_routing_table(ipv6_route_parsing(self.ipv6_routing_contents)))

    # checks the user entered command against the condition and returns the output
    def command_processor(self, command):

        if command == '?':
            content = '\n'
            for keys in self.cmd_dictionary:
                content += keys + '\n'
            return content

        # for viewing all show/bash commands
        # optimized this part
        elif '??' in command:
            cmdlist = command.split()
            if not len(cmdlist) == 1:
                command = self.autocomplete(' '.join(cmdlist[:-1]))
                command += " " + cmdlist[-1]
            command = command.replace('??', '')
            print(f"?? for command {command}")
            question_pattern = re.compile(fr'.*{command}.*')
            question_matches = question_pattern.findall('\n'.join(self.newallCommands))
            content = ''
            question_matches = sorted(question_matches)
            for line in question_matches:
                if line != '':
                   content += line + '\n'
            return content.strip('\n')

        # is ? is pressed along with any previous string like show ip ?
        elif re.match(r'(.*[\s]\?)', command):
            temp_dict = {}
            try:
                cmdlist= command.split()
                command_gen = self.autocomplete(' '.join(cmdlist[:-1]))
                print(f"? for command {command_gen}")
                for cmd in command_gen.split():
                    if cmd in ['bash', 'show']:
                        temp_dict = self.cmd_dictionary[cmd]
                    else: # searching the inner dicitonary for the keys. For eg if user does show ip ?, temp_dict will be eventually {interfaces: {}, route {}, ..}
                        temp_dict1 = temp_dict.copy()
                        temp_dict = {}
                        temp_dict = temp_dict1[cmd].copy()
                content = ''
                for keys in sorted(temp_dict):
                    content += keys + '\n'
                return content.strip('\n')
            except KeyError as e:
                return('wrong command')

        # is ? is pressed along with any previous string like show ip?
        # optimized this part
        elif re.match(r'(.*[^\s]\?)', command):
            content = ''
            temp_dict = self.cmd_dictionary
            cmdlist= command.split()
            command_gen = self.autocomplete(' '.join(cmdlist[:-1]))
            if len(cmdlist) == 1:
                pass
            else: 
                for cmd in command_gen.split():
                    if cmd in ['bash', 'show']:
                        temp_dict = self.cmd_dictionary[cmd]
                    else:
                        temp_dict1 = temp_dict.copy()
                        temp_dict = {}
                        temp_dict = temp_dict1[cmd].copy() # we are not considering the last element in the command meaning in show ip?, we only are concerned with keys starting with ip in the dict['show'] returned dictionary
            for keys in temp_dict:
                if keys.startswith(cmdlist[-1].replace('?', '')):
                    content += keys + '\n'
            return content.strip('\n')   
            
        command = self.autocomplete(command)
        # Handle custom dynamic commands
        command_handlers = {
            r"show ip route( vrf (\w+))?( ([\d.]+))?": handle_ip_route,  # Combine patterns for efficiency 
            r"show ipv6 route( vrf (\w+))?( ([\d.]+))?": handle_ipv6_route, 
            r"show logging (\d+)": handle_show_logging,
            r"show running-config section": shrunsec,
            r"show running-config interfaces": shrunint,
            r"show interfaces(\s)((Et|Po|Vx|Ma)(.*)\s)?(status|switchport|mac-detail|phy-detail)": handle_show_interfaces_options, # more info on regex here: https://regex101.com/r/rPk0ov/1
            r"show interfaces(\s)?((et|po|vl|ma|lo)(.*[0-9]))?$": handle_individual_interfaces, # more info on regex here: https://regex101.com/r/LAY345/1
            r"show vlan \d+": handle_per_vlan,
            r"show ip(v(6)?)? bgp\s*\S*": handle_bgp_commands,
        }

        for pattern, handler in command_handlers.items():
            match = re.search(pattern, command, flags=re.IGNORECASE)
            if match:
                return handler(self, command=command, match=match) 

        # Handle static commands mapped in mapCommand 
        if command in mapCommand:
            return handle_mapped_command(self, command)
        
        # Handle nz commands
        for cmd in self.nz_commands:
            if cmd == command:
               print("Showing only non-zero values for this command")
               command = fr"{command} \| nz"
               return self.command_searcher(command)
        
        # Handle unmatched commands
        return self.command_searcher(command)

    # used in autocomplete 
    def complete(self, text, state):
        # autocompleter
        ori_command = readline.get_line_buffer().lower()
        cmd_first_key_dict = {
            'show': self.cmd_dictionary['show'],
            'bash': self.cmd_dictionary['bash']
        }
        splitted_command = ori_command.split()
        if len(splitted_command) <= 1 and not re.search(r'\s$', ori_command): # if no commands entered yet, show all options
            options = ['show', 'bash'] 
        else:
            split_ori_command = re.findall(r'(.+)\s(\w+)?$', ori_command)
            mod_ori_command = self.autocomplete(split_ori_command[0][0]).split()
            mod_ori_command.append(split_ori_command[0][1])
            if mod_ori_command[0] in ['show', 'bash']: # narrow down options based on 'show' or 'bash' command
                if len(mod_ori_command) == 2 and not re.search(r'\s$', ori_command):
                    options = [x for x in cmd_first_key_dict[mod_ori_command[0]] if x.startswith(mod_ori_command[1])]
                elif len(mod_ori_command) == 3 and not re.search(r'\s$', ori_command):
                    options = [x for x in cmd_first_key_dict[mod_ori_command[0]][mod_ori_command[1]] if x.startswith(mod_ori_command[2])]
                # next condition useful when per interface outputs are inputted (Eg: sh int et1 status, sh int et1 mac-detail)
                elif (len(mod_ori_command) == 4 or len(mod_ori_command) == 5) and re.search(r'\b(et|po|vx|ma)', mod_ori_command[2]) and not re.search(r'\s$', ori_command):
                    options = ['mac-detail', 'phy-detail', 'status', 'switchport']
                elif len(mod_ori_command) == 4 and not re.search(r'\s$', ori_command):
                    options = [x for x in cmd_first_key_dict[mod_ori_command[0]][mod_ori_command[1]][mod_ori_command[2]] if x.startswith(mod_ori_command[3])]
                elif len(mod_ori_command) == 5 and (mod_ori_command[1] == 'ip' or mod_ori_command[1] == 'ipv6') and (mod_ori_command[2] == 'route' or mod_ori_command[2] == 'bgp') and mod_ori_command[3] == 'vrf':
                    options = [x for x in self.vrf_routing_table]
                    options.append('all detail')
                    # options.append('all-detail')
                    # options.append('all-host')
                    # options.append('all-summary')
                elif len(mod_ori_command) == 5 and not re.search(r'\s$', ori_command):
                    options = [x for x in cmd_first_key_dict[mod_ori_command[0]][mod_ori_command[1]][mod_ori_command[2]][mod_ori_command[3]] if x.startswith(mod_ori_command[4])]
                elif len(mod_ori_command) == 6 and not re.search(r'\s$', ori_command) and mod_ori_command[3] == 'vrf' and (mod_ori_command[1] == 'ip' or mod_ori_command[1] == 'ipv6') and mod_ori_command[2] == 'route':
                    options = ['summary', 'host']
                elif len(mod_ori_command) == 6 and (mod_ori_command[1] == 'ip' or mod_ori_command[1] == 'ipv6') and mod_ori_command[2] == 'bgp' and (mod_ori_command[3] == 'summary' or mod_ori_command[3] == 'neighbor') and mod_ori_command[4] == 'vrf':
                    options = [x for x in self.vrf_routing_table]
                elif len(mod_ori_command) == 6 and not re.search(r'\s$', ori_command):
                    options = [x for x in cmd_first_key_dict[mod_ori_command[0]][mod_ori_command[1]][mod_ori_command[2]][mod_ori_command[3]][mod_ori_command[4]] if x.startswith(mod_ori_command[5])]
                elif len(mod_ori_command) == 7 and not re.search(r'\s$', ori_command):
                    options = [x for x in cmd_first_key_dict[mod_ori_command[0]][mod_ori_command[1]][mod_ori_command[2]][mod_ori_command[3]][mod_ori_command[4]][mod_ori_command[5]] if x.startswith(mod_ori_command[6])]
            else: # no options for other commands
                options = []
        results = [x for x in options if x.startswith(text)] + [None]
        return results[state]

    def autocomplete(self, command):
        actual_cmd = []
        cmdlist = command.split(' ')
        to_search = self.cmd_dictionary
        for cmd in cmdlist:
            for keys in to_search:
                match = re.search(rf'^{cmd}', keys, flags=re.IGNORECASE)
                if match:
                    actual_cmd.append(keys)
                    to_search = to_search[keys]
                    break
            else:
                actual_cmd.append(cmd)
        # print(f"actual command: {actual_cmd}")
        return ' '.join(actual_cmd)