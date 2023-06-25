import re
import readline
import subprocess 
import sys
import os
import gzip
from command_modules.routeLookup import *
from command_modules.showRunSection import *
from command_modules.customCommandMapper import *
from command_modules.showLogging import *
from command_modules.lldpNeighbors import *
from io import StringIO

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
    
    
    def show_tech_commands_modifier(self):
        # function to modify the commandds in the show tech for easier parsing
        self.file_content = re.sub('------------- show interface ', '------------- show interfaces ', self.file_content, flags=re.MULTILINE)
        self.file_content = re.sub('------------- show ip interface ', '------------- show ip interfaces ', self.file_content, flags=re.MULTILINE)
        self.file_content = re.sub('------------- bash dmesg.*', '------------- bash dmesg -------------', self.file_content, flags=re.MULTILINE)
        self.file_content = re.sub('------------- show ip route vrf all detail -------------', '------------- show ip route vrf all-detail -------------', self.file_content, flags=re.MULTILINE)
        self.file_content = re.sub('------------- show ip route vrf all host -------------', '------------- show ip route vrf all-host -------------', self.file_content, flags=re.MULTILINE)
        self.file_content = re.sub('------------- show ip route vrf all summary -------------', '------------- show ip route vrf all-summary -------------', self.file_content, flags=re.MULTILINE)
        self.file_content = re.sub('------------- show interfaces counters discards.*', '------------- show interfaces counters discards -------------', self.file_content, flags=re.MULTILINE)
        self.file_content = re.sub('queue \| nz', 'queue', self.file_content, flags=re.MULTILINE)
        self.file_content = re.sub('------------- show ip bgp summary vrf all -------------', '------------- show ip bgp summary -------------', self.file_content, flags=re.MULTILINE)
        self.file_content = re.sub('------------- show ip bgp neighbor vrf all -------------', '------------- show ip bgp neighbor -------------', self.file_content, flags=re.MULTILINE)
        self.file_content = re.sub('------------- show interfaces mac detail -------------', '------------- show interfaces mac-detail -------------', self.file_content, flags=re.MULTILINE)
        self.file_content = re.sub('------------- show interfaces phy detail -------------', '------------- show interfaces phy-detail -------------', self.file_content, flags=re.MULTILINE)
        self.file_content = re.sub('\| nz -------------', '-------------', self.file_content, flags=re.MULTILINE)
        self.file_content = re.sub(r'\bcounter\b', 'counters', self.file_content, flags=re.MULTILINE)
        self.file_content = re.sub(r'\bcount\b', 'counters', self.file_content, flags=re.MULTILINE)
        self.file_content = re.sub(r'vxlan 1-\$', 'vxlan', self.file_content, flags=re.MULTILINE)
        self.file_content = re.sub(r'\bneighbor\b', 'neighbors', self.file_content, flags=re.MULTILINE)

    def gather_commands(self):
        self.allCommands = re.findall('------------- (show.*|bash.*) -------------', self.file_content)
        for cmd in self.allCommands:
            parts = cmd.split() # splitting the commands => parts = ['show version detail', 'show interfaces status', ..]
            temp_dict = self.cmd_dictionary # using a temporary dictionay used later in the iteration. For each command iteration, temp_dict now points to the original cmd_dictionary
            for part in parts: # splitting the commmands itself => ['show' 'version', 'detail'] to check if element exists in dictionary. If not populates it
                if part not in temp_dict: 
                    temp_dict[part] = {}
                temp_dict = temp_dict[part] # now temp dict point to the empty dictionary of the key {part}. Eg cmd_dictionry = {show: {} <-- temp_dict}
        # some showtechs have a differnt command for show the interfaces status. Depending on what is present on the show tech, we will call that
        if 'show interfaces all status' in self.allCommands:
            mapCommand['show interfaces status']['parent_command'] = 'show interfaces all status'
        else:
            mapCommand['show interfaces status']['parent_command'] = 'show interfaces status'


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
            return ('wrong command')
 

    def get_hostname(self):
        for line in self.command_searcher('show running-config sanitized').splitlines():
            searches = re.search(r'^hostname\s+(.+)$', line)
            if searches:
                self.hostname = searches.group(1)
                break


    def sed(self, command):
        # sanitizing the output
        sanitized_command = re.sub(r"\b^sh(o(w?)?)?\b", "show", command)
        sanitized_command = re.sub(r"\b^ba(s(h?)?)?\b", "bash", sanitized_command)
        sanitized_command = re.sub(r"\bver(s(i(o(n?)?)?)?)?\b", "version", sanitized_command)
        sanitized_command = re.sub(r"\bint(e(r(f(a(c(e(s?)?)?)?)?)?)?)?\b", "interfaces", sanitized_command)
        sanitized_command = re.sub(r"\badd(r(e(s(s?)?)?)?)?$\b", "address-table", sanitized_command)
        sanitized_command = re.sub(r"\bvx(l(a(n(1?)?)?)?)?\b", "vxlan", sanitized_command)
        sanitized_command = re.sub(r"\brun(n(i(n(g(-(c(o(n(f(i(g?)?)?)?)?)?)?)?)?)?)?)?\b", "running-config sanitized", sanitized_command)
        sanitized_command = re.sub(r"\b st(a(t(u(s?)?)?)?)?\b", " status", sanitized_command)
        sanitized_command = re.sub(r"\berr(d(i(s(a(b(l(e(d?)?)?)?)?)?)?)?)?\b", "errdisabled", sanitized_command)
        sanitized_command = re.sub(r"\bbr(i(e(f?)?)?)?\b", "brief", sanitized_command)
        sanitized_command = re.sub(r"\bshow log(g(i(n(g?)?)?)?)?\b", "show logging", sanitized_command)
        sanitized_command = re.sub(r"\bsec(t(i(o(n?)?)?)?)?\b", "section", sanitized_command)
        sanitized_command = re.sub(r"\bst(a(t(u(s?)?)?)?)?\b", "status", sanitized_command)
        sanitized_command = re.sub(r"\bnei(g(h(b(o(r(s?)?)?)?)?)?)?\b", "neighbors", sanitized_command)
        sanitized_command = re.sub(r"\btrans(c(e(i(v(e(r?)?)?)?)?)?)?\b", "transceiver", sanitized_command)
        return sanitized_command


    def routing_logic(self):
        # Route loookup Logic. Parsing the whole route output as follows vrf_routing_table = (vrf-default: {10.0.0.0/24: {binary-eq: 00001010.00000000.00000000.00000000, prefix: 24}})
        self.routing_contents = self.command_searcher('show ip route vrf all-detail') # has the ouput of the command show ip route vrf all detail
        self.routing_contents += '\n------------- show ip route vrf all host -------------' # this line has been added for a regex match used when user inputs the last avaialble vrf on the device
        self.vrf_routing_table = {}
        self.matched_routes = [] # holds the matched ip's in a specifif vrf for an ip inputted by the user
        parsing_routing_table(self.routing_contents, self.routes)
        for vrf in self.routes:  
            self.vrf_routing_table[vrf] = creating_vrf_routing_table(self.routes[vrf])


    def command_processor(self, command):
        if command == 'exit':
            sys.exit()

        elif command == '?':
            content = '\n'
            for keys in self.cmd_dictionary:
                content += keys + '\n'
            return content

        # for viewing all show/bash commands
        elif '??' in command:
            command = command.replace('??', '')
            question_pattern = re.compile(fr'.*{command}.*')
            question_matches = question_pattern.findall('\n'.join(self.allCommands))
            content = ''
            question_matches = sorted(question_matches)
            for line in question_matches:
                if line != '':
                   content += line + '\n'
            return content.strip('\n')

        # is ? is pressed along with any previous string like show ip ?
        elif re.match('(.*[\s]\?)', command):
            temp_dict = {}
            try:
                for cmd in command.split()[:-1]:
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
        elif re.match('(.*[^\s]\?)', command):
            temp_dict = {}
            for cmd in command.split()[:-1]:
                if cmd in ['bash', 'show']:
                    temp_dict = self.cmd_dictionary[cmd]
                else:
                    temp_dict1 = temp_dict.copy()
                    temp_dict = {}
                    temp_dict = temp_dict1[cmd.replace('?', '')].copy() # we are not considering the last element in the command meaning in show ip?, we only are concerned with keys starting with ip in the dict['show'] returned dictionary
            content = ''
            for keys in temp_dict:
                if keys.startswith(command.split()[-1].replace('?', '')):
                    content += keys + '\n'
            return content.strip('\n')   
            
        # if user performs route lookup        
        elif ('show ip route vrf' in command or 'show ip route' in command) and not ('all-detail' in command or 'all-host' in command or 'all-summary' in command or 'host' in command or 'kernel unprogrammed' in command):
            clist = command.split(' ')
            clist_len = len(clist)
            match clist_len:
                case 3:
                    return(routing_table_ouput(self.routing_contents, 'default'))
                case 4:
                    vrfc = 'default'
                    ip_add = clist[-1]
                case 5:
                    if clist[3] == 'vrf':
                        vrfc = clist[-1]
                        return(routing_table_ouput(self.routing_contents, vrfc))
                    else:
                        return('invalid input')
                case 6:
                    try:
                        vrfc = clist[-2]
                        ip_add = clist[-1]
                        if vrfc not in self.routes:
                            return('vrf does not exist')
                    except KeyError as e:
                            return('invalid input')
                case _:
                    return('invalid input')
            if (len(clist) == 6 or len(clist) == 4):
                route_ip = lookup(self.vrf_routing_table, ip_add, vrfc, self.matched_routes)
                if route_ip == 'Invalid ip address':
                    return 'Invalid ip address'
                else:
                    self.matched_routes = []
                    return vrf_route_lookup(self.routing_contents, route_ip, vrfc)
                    
        # if user wants to print the last few lines of show logging.
        elif re.search('show logging [\d]', command):
            splitted_command = command.split()
            if len(splitted_command) == 3:
                print()
                return(showLoggingLines(self.command_searcher(splitted_command[0] + ' ' + splitted_command[1]), splitted_command[-1]))
            else:
                return('wrong command(too many inputs)')

        # if user runs show run section
        elif 'show running-config sanitized section' in command:
            return(shrunsec(self.command_searcher('show running-config sanitized'), command))

        elif command in mapCommand:
            if (mapCommand[command]['is_static'] == True and mapCommand[command]['dict_input'] == False): 
                return(mapCommand[command]['function'](self.command_searcher(mapCommand[command]['parent_command'])))
            elif (mapCommand[command]['is_static'] == True and mapCommand[command]['dict_input'] == True): 
                return(mapCommand[command]['function'](self.lldp_dictionary))

        else:
            return(self.command_searcher(command))


    def complete(self, text, state):
        # autocompleter
        ori_command = readline.get_line_buffer().lower()
        mod_ori_command = ori_command.split() # get the previously entered commands
        cmd_first_key_dict = {
            'show': self.cmd_dictionary['show'],
            'bash': self.cmd_dictionary['bash']
        }
        mod_ori_command[0] = re.sub(r'\b^sh\b', 'show', mod_ori_command[0])
        mod_ori_command[0] = re.sub(r'\b^sho\b', 'show', mod_ori_command[0])
        mod_ori_command[0] = re.sub(r'\b^bas\b', 'bash', mod_ori_command[0])
        if len(mod_ori_command) > 2:
            mod_ori_command[-2] = self.sed(mod_ori_command[-2])
        if len(mod_ori_command) <= 1 and not re.search('\s$', ori_command): # if no commands entered yet, show all options
            options = ['show', 'bash'] 
        elif mod_ori_command[0] in ['show', 'bash']: # narrow down options based on 'show' or 'bash' command
            if len(mod_ori_command) == 2 and not re.search('\s$', ori_command):
                options = [x for x in cmd_first_key_dict[mod_ori_command[0]] if x.startswith(mod_ori_command[1])]
            elif len(mod_ori_command) == 3 and not re.search('\s$', ori_command):
                options = [x for x in cmd_first_key_dict[mod_ori_command[0]][mod_ori_command[1]] if x.startswith(mod_ori_command[2])]
            elif len(mod_ori_command) == 4 and not re.search('\s$', ori_command):
                options = [x for x in cmd_first_key_dict[mod_ori_command[0]][mod_ori_command[1]][mod_ori_command[2]] if x.startswith(mod_ori_command[3])]
            elif len(mod_ori_command) == 5 and mod_ori_command[1] == 'ip' and mod_ori_command[2] == 'route' and mod_ori_command[3] == 'vrf':
                options = [x for x in self.vrf_routing_table]
                options.append('all-detail')
                options.append('all-host')
                options.append('all-summary')
            elif len(mod_ori_command) == 5 and not re.search('\s$', ori_command):
                options = [x for x in cmd_first_key_dict[mod_ori_command[0]][mod_ori_command[1]][mod_ori_command[2]][mod_ori_command[3]] if x.startswith(mod_ori_command[4])]
            elif len(mod_ori_command) == 6 and not re.search('\s$', ori_command):
                options = [x for x in cmd_first_key_dict[mod_ori_command[0]][mod_ori_command[1]][mod_ori_command[2]][mod_ori_command[3]][mod_ori_command[4]] if x.startswith(mod_ori_command[5])]
            elif len(mod_ori_command) == 7 and not re.search('\s$', ori_command):
                options = [x for x in cmd_first_key_dict[mod_ori_command[0]][mod_ori_command[1]][mod_ori_command[2]][mod_ori_command[3]][mod_ori_command[4]][mod_ori_command[5]] if x.startswith(mod_ori_command[6])]
            else:
                options = []

        else: # no options for other commands
            options = []
        results = [x for x in options if x.startswith(text)] + [None]
        return results[state]




