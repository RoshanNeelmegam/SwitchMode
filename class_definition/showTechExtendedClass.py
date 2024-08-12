import re
import sys
import os
import gzip
import readline
from command_modules.routeLookup import *

class showTechExtended:
    def __init__(self, file):
        self.cmd_dictionary = {}
        self.allCommands = []
        self.routes = {}
        if os.path.isfile(file):
            file_type = os.path.splitext(file)[1]
            if file_type == '.gz':
                with gzip.open(file) as f:
                    self.file_content = f.read().decode()
            else:
                with open(file) as f:
                    self.file_content = f.read()
            self.file_content = re.sub(r'vxlan \$', 'vxlan', self.file_content, flags=re.MULTILINE)
        else:
            print(f"wrong file provided or file doesn't exist")
            sys.exit()

    def command_collector(self):
        self.allCommands = re.findall(r'------------- (show .*) -------------', self.file_content)
        mod_commands = ['show bgp evpn route-type <route-type> rd <rd> vni <vni> next-hop <next-hop>', 'show bgp evpn route-type <route-type> rd <rd> next-hop <next-hop> vni <vni>', 'show bgp evpn route-type <route-type> vni <vni> rd <rd> next-hop <next-hop>', 'show bgp evpn route-type <route-type> vni <vni> next-hop <next-hop> rd <rd>', 'show bgp evpn route-type <route-type> next-hop <next-hop> vni <vni> rd <rd>', 'show bgp evpn route-type <route-type> next-hop <next-hop> rd <rd> vni <vni>', 'show bgp evpn route-type <route-type> detail', 'show bgp evpn route-type <route-type> rd <rd> detail', 'show bgp evpn route-type <route-type> <route> next-hop <next-hop> vni <vni> rd <rd>', 'show bgp evpn route-type <route-type> <route> next-hop <next-hop> rd <rd> vni <vni>', 'show bgp evpn route-type <route-type> <route> vni <vni> rd <rd> next-hop <next-hop>', 'show bgp evpn route-type <route-type> <route> vni <vni> next-hop <next-hop> rd <rd>', 'show bgp evpn route-type <route-type> <route> rd <rd> vni <vni> next-hop <next-hop>', 'show bgp evpn route-type <route-type> <route> rd <rd> next-hop <next-hop> vni <vni>', 'show bgp evpn route-type <route-type> <route> detail', 'show bgp evpn route-type <route-type> <route> rd <rd> detail',
            'show bgp evpn vni <vni>', 'show bgp evpn vni <vni> next-hop <next-hop> rd <rd>', 'show bgp evpn vni <vni> rd <rd> next-hop <next-hop>',
            'show bgp evpn rd <rd> detail', 'show bgp evpn rd <rd> vni <vni>', 'show bgp evpn rd <rd> vni <vni> next-hop <next-hop>',
            'show bgp evpn next-hop <next-hop>']
        self.allCommands.extend(mod_commands)
        for command in self.allCommands:
            temp = self.cmd_dictionary
            for part in command.split(' '):
                if part not in temp:
                    temp[part] = {}
                    temp = temp[part]
                else:
                    temp = temp[part]

    def sed(self, commands):
        # sanitizing the output
        sanitized_command = re.sub(r"\b^sh(o(w?)?)?\b", "show", commands)
        sanitized_command = re.sub(r"\bevp(n?)?\b", "evpn", sanitized_command)
        sanitized_command = re.sub(r"show bgp evpn \brout(e(-(t(y(p(e?)?)?)?)?)?)?\b", "show bgp evpn route-type", sanitized_command)
        sanitized_command = re.sub(r"\bnext(-(h(o(p?)?)?)?)?\b", "next-hop", sanitized_command)
        sanitized_command = re.sub(r"\bint(e(r(f(a(c(e(s?)?)?)?)?)?)?)?\b", "interface", sanitized_command)
        sanitized_command = re.sub(r"\bvx(l(a(n(1?)?)?)?)?\b", "vxlan", sanitized_command)
        return sanitized_command
    
    def command_modifier(self, commands):
        mod_commands = commands.split()
        if 'show bgp evpn' in commands:
            for command in mod_commands[:-1]:
                current_ind = mod_commands.index(command)
                if command not in ['show', 'bgp', 'evpn', 'route-type', 'rd', 'vni', 'detail', 'next-hop']:
                    if mod_commands[current_ind - 1] == '<route-type>':
                        mod_commands[current_ind] = '<route>'
                    else:
                        mod_commands[current_ind] = f'<{mod_commands[current_ind-1]}>'
        return mod_commands
        
    def command_searcher(self, commands):
        pattern = fr'------------- {commands} -------------'
        first_match = re.search(pattern, self.file_content)
        # if there's any match for the command
        if first_match:
            next_pattern = r'------------- (show).*'
            second_match = re.search(next_pattern, self.file_content[first_match.end():])
            if second_match:
                output = self.file_content[first_match.start():(first_match.end() + second_match.start() - 1)]
                return output
            else:
                output = self.file_content[first_match.start():]
                return output
        else:
            return ('wrong command')

    def routing_logic(self):
        # Route loookup Logic. Parsing the whole route output as follows vrf_routing_table = (vrf-default: {10.0.0.0/24: {binary-eq: 00001010.00000000.00000000.00000000, prefix: 24}})
        self.routing_contents = self.command_searcher('show ip route') # has the ouput of the command show ip route vrf all detail
        self.routing_contents += '\nVRF: Table_Ends_Here'# this line has been added for a regex match used when user inputs the last avaialble vrf on the device
        self.vrf_routing_table = {}
        self.matched_routes = [] # holds the matched ip's in a specifif vrf for an ip inputted by the user
        parsing_routing_table(self.routing_contents, self.routes)
        for vrf in self.routes:  
            self.vrf_routing_table[vrf] = creating_vrf_routing_table(self.routes[vrf])
        
    def EvpnOutput(self, route_type=None, route=None, vni=None, RD=None, next_hop=None, detail=False):
        if (next_hop != '' and route_type=='' and route=='' and vni=='' and RD=='' and detail==False):
            output = ''
            match = re.findall(rf'.*RD:.*\n.*{next_hop}.*', self.file_content)
            for line in match:
                output += line + '\n'
            return output
        elif detail:
            output = ''
            ptr = 0
            for lines in self.file_content.splitlines():
                if ptr == 1:
                    if re.search(fr'BGP routing table entry for .*', lines) or re.search(r'------------- show.*', lines):
                        ptr = 0
                        if re.search(fr'BGP routing table entry for {route_type}.*{route}.*Route Distinguisher: {RD}.*', lines):
                            ptr = 1
                        else:
                            continue
                    output += lines + '\n'
                else:
                    match = re.search(fr'BGP routing table entry for {route_type}.*{route}.*Route Distinguisher: {RD}.*', lines)
                    if match:
                        ptr = 1
                        output += lines + '\n'    
            return output              
        else:
            output = ''
            match = re.findall(rf'.*RD: {RD}.*{route_type}.*{vni}.*{route}.*\n.*{next_hop}.*', self.file_content)
            for line in match:
                output += line + '\n'
            return output  
  
    def command_processor(self, commands):
        if commands.lower() == 'exit':
            sys.exit()
        # if user presses ?
        elif commands == '?':
            content = '\n'
            for keys in self.cmd_dictionary:
                content += keys + '\n'
            return content
        # for viewing all show/bash commands
        elif '??' in commands:
            if self.command_modifier(commands):
                commands = ' '.join(self.command_modifier(commands))
            commands = commands.replace('??', '')
            question_pattern = re.compile(fr'.*{commands}.*')
            question_matches = question_pattern.findall('\n'.join(self.allCommands))
            content = ''
            question_matches = sorted(question_matches)
            for line in question_matches:
                if line != '':
                   content += line + '\n'
            return content.strip('\n')
        # is ? is pressed along with any previous string like show ip ?
        elif re.match(r'(.*[\s]\?)', commands):
            mod_commands = self.command_modifier(commands)
            temp_dict = {}
            try:
                for cmd in mod_commands[:-1]:
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
        elif re.match(r'(.*[^\s]\?)', commands):
            temp_dict = {}
            for cmd in commands.split()[:-1]:
                if cmd in ['bash', 'show']:
                    temp_dict = self.cmd_dictionary[cmd]
                else:
                    temp_dict1 = temp_dict.copy()
                    temp_dict = {}
                    temp_dict = temp_dict1[cmd.replace('?', '')].copy() # we are not considering the last element in the command meaning in show ip?, we only are concerned with keys starting with ip in the dict['show'] returned dictionary
            content = ''
            for keys in temp_dict:
                if keys.startswith(commands.split()[-1].replace('?', '')):
                    content += keys + '\n'
            return content.strip('\n')   
        commands = self.autocomplete(commands)
        if re.search(r'show bgp evpn (route-type|vni|rd|next-hop|detail).+', commands ) and not 'summary' in commands and not 'instance' in commands:
            route_type = ''; route = ''; vni = ''; RD = ''; next_hop = ''; detail = False
            if ('detail' in commands and ('next-hop' in commands or 'vni' in commands)):
                return('detail ouput not supported with keywords vni and nexthop')
            if commands.lower() == 'exit':
                sys.exit()
            elif (re.search(r'show bgp evpn .*', commands)):
                try:
                    route_type = re.findall(r'.*route-type (\S+).*', commands)[0]
                except IndexError as e:
                    route_type = ''
                try:
                    next_hop = re.findall(r'.*next-hop (\S+).*', commands)[0]
                except IndexError as e:
                    next_hop = ''
                try:
                    vni = re.findall(r'.*vni (\S+).*', commands)[0]
                except IndexError as e:
                    vni = ''
                try:
                    RD = re.findall(r'.*rd (\S+).*', commands)[0]
                except IndexError as e:
                    RD = ''
                if 'detail' in commands:
                    detail = True
                if re.findall(r"show bgp evpn route-type (\S*) (\S*) detail", commands) or re.findall(r"show bgp evpn route-type (\S*) (\S*) next-hop.*", commands) or re.findall(r"show bgp evpn route-type (\S*) (\S*) vni.*", commands) or re.findall(r"show bgp evpn route-type (\S*) (\S*) rd.*", commands):
                    route = re.findall(r"show bgp evpn route-type (\S*) (\S*).*", commands)[0][1]
                elif ('detail' not in commands and 'next-hop' not in commands and 'vni' not in commands and 'rd' not in commands and re.findall(r"show bgp evpn route-type (\S*) (\S*)$", commands)):
                    route = re.findall(r"show bgp evpn route-type (\S*) (\S*)$", commands)[0][1]
                return(self.EvpnOutput(route_type=route_type, route=route, vni=vni, RD=RD, next_hop=next_hop, detail=detail))
            # if user performs route lookup        
        elif ('show ip route vrf' in commands or 'show ip route' in commands):
            clist = commands.split(' ')
            clist_len = len(clist)
            if clist_len == 3:
                    # print(self.routing_contents)
                    return(routing_table_ouput(self.routing_contents, 'default'))
            elif clist_len == 4:
                    vrfc = 'default'
                    ip_add = clist[-1]
            elif clist_len == 5:
                    if clist[3] == 'vrf':
                        vrfc = clist[-1]
                        return(routing_table_ouput(self.routing_contents, vrfc))
                    else:
                        return('invalid input')
            elif clist_len == 6:
                    try:
                        vrfc = clist[-2]
                        ip_add = clist[-1]
                        if vrfc not in self.routes:
                            return('vrf does not exist')
                    except KeyError as e:
                            return('invalid input')
            else:
                    return('invalid input')
            if (clist_len == 6 or clist_len == 4):
                route_ip = lookup(self.vrf_routing_table, ip_add, vrfc, self.matched_routes)
                if route_ip == 'Invalid ip address':
                    return 'Invalid ip address'
                else:
                    self.matched_routes = []
                    return vrf_route_lookup(self.routing_contents, route_ip, vrfc)
        else:
            return(self.command_searcher(self.sed(commands)))

    def complete(self, text, state):
        # autocompleter
        ori_command = readline.get_line_buffer().lower()
        # mod_ori_command = self.command_modifier(self.sed(ori_command))
        # mod_ori_command[0] = self.sed(mod_ori_command[0]) 
        cmd_first_key_dict = {
            'show': self.cmd_dictionary['show'],
        }
        splitted_command = ori_command.split()
        if len(splitted_command) <= 1 and not re.search(r'\s$', ori_command): # if no commands entered yet, show all options
            options = ['show'] 
        else:
            split_ori_command = re.findall(r'(.+)\s(\w+)?$', ori_command)
            mod_ori_command = self.autocomplete(split_ori_command[0][0]).split()
            mod_ori_command.append(split_ori_command[0][1])
            if len(mod_ori_command) <= 1 and not re.search(r'\s$', ori_command): # if no commands entered yet, show all options
                options = ['show'] 
            elif mod_ori_command[0] in ['show']: # narrow down options based on 'show' or 'bash' command
                if len(mod_ori_command) == 2 and not re.search(r'\s$', ori_command):
                    options = [ x for x in cmd_first_key_dict[mod_ori_command[0]] if x.startswith(mod_ori_command[1]) ]
                elif len(mod_ori_command) == 3 and not re.search(r'\s$', ori_command):
                    options = [x for x in cmd_first_key_dict[mod_ori_command[0]][mod_ori_command[1]] if x.startswith(mod_ori_command[2])]
                elif len(mod_ori_command) == 4 and not re.search(r'\s$', ori_command):
                    options = [x for x in cmd_first_key_dict[mod_ori_command[0]][mod_ori_command[1]][mod_ori_command[2]] if x.startswith(mod_ori_command[3])]
                elif len(mod_ori_command) == 5 and mod_ori_command[3] == 'route-type' and not re.search(r'\s$', ori_command):
                    options = ['auto-discovery', 'ethernet-segment', 'imet', 'ip-prefix', 'mac-ip', 'smet', 'join-sync', 'leave-sync', 'spmsi']
                elif len(mod_ori_command) == 5 and not re.search(r'\s$', ori_command):
                    options = [x for x in cmd_first_key_dict[mod_ori_command[0]][mod_ori_command[1]][mod_ori_command[2]][mod_ori_command[3]] if x.startswith(mod_ori_command[4])]
                elif len(mod_ori_command) == 6 and not re.search(r'\s$', ori_command):
                    options = [x for x in cmd_first_key_dict[mod_ori_command[0]][mod_ori_command[1]][mod_ori_command[2]][mod_ori_command[3]][mod_ori_command[4]] if x.startswith(mod_ori_command[5])]
                elif len(mod_ori_command) == 7 and mod_ori_command[3] == 'route-type' and 'next-hop' not in mod_ori_command and 'detail' not in mod_ori_command and not re.search(r'\s$', ori_command):
                    options = [x for x in cmd_first_key_dict[mod_ori_command[0]][mod_ori_command[1]][mod_ori_command[2]][mod_ori_command[3]][mod_ori_command[4]][mod_ori_command[5]] if x.startswith(mod_ori_command[6])]
            else:
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
