import re

def parsing_routing_table(contents, routes):
    # optimized this part for faster parsing
    # creating a routes dictionary: routes = {'default': ['0.0.0.0/0', '0.0.0.0/8', '32.55.116.0/26', '32.55.178.20/31', 'mgmt': ['0.0.0.0/8']}
    vrfs_list_original = re.findall(r'\nVRF: (\S+)', contents)
    biglist = re.findall(r'(\nVRF: \S+|\d+\.\d+\.\d+\.\d+\/\d+)', contents)
    for vrf in vrfs_list_original:
        if vrf == 'Table_Ends_Here':
            break
        vrf_to_start_search = biglist.index(f'\nVRF: {vrf}') + 1
        vrf_to_end_search = biglist.index(f'\nVRF: {vrfs_list_original[vrfs_list_original.index(vrf) + 1]}')
        routes[vrf] = biglist[vrf_to_start_search:vrf_to_end_search]


def creating_vrf_routing_table(routes):
        # will return a format as follows: {'127.0.0.1/32': {'binary_equivalent': '01111111000000000000000000000001', 'prefix': '32'}}
        vrf_table = {}
        for route in routes:
            binary_equivalent = ''
            splitted_route = route.split('/')
            splitted_route_dot = splitted_route[0].split('.')
            for nums in splitted_route_dot:
                binary_equivalent = binary_equivalent + str(format(int(nums), '08b'))
            vrf_table[route] = { 'binary_equivalent': binary_equivalent, 'prefix': splitted_route[1] }
        # print(vrf_table)
        # print('------')
        return vrf_table


def lookup(table, ip_address, vrf, matched_routes):
    # Checking if the ip provided is a valid ip
    ip_regex = r'(?:2[0-4][0-9]|[01]?[0-9][0-9]?)\.(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.((?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?))'
    if re.match(ip_regex, ip_address) == None:
        return("Invalid ip address")
    else:
        ip_binary_equivalent = ''
        max_pl = 0
        splitted_address = ip_address.split('.')
        for nums in splitted_address:
            ip_binary_equivalent = ip_binary_equivalent + str(format(int(nums), '08b'))
        try:
           vrf_route = table[vrf]
        except KeyError as e:
            return('wrong vrf entered')
        for route in vrf_route:
                if ip_binary_equivalent.startswith(vrf_route[route]['binary_equivalent'][0:int(vrf_route[route]['prefix'])]):
                    if int(vrf_route[route]['prefix']) > max_pl:
                        max_pl = int(vrf_route[route]['prefix'])
                        matched_routes.append(route)
        if len(matched_routes) == 0:
             if re.match(ip_regex, '0.0.0.0') != None:
                  matched_routes.append('0.0.0.0')
        return matched_routes[-1]


def vrf_route_lookup(contents, address_match, vrf):
    lookup = '' 
    pfirst_match = re.search(fr'VRF: {vrf}', contents).span()[1] # matches the first line of the vrf routing entry
    pattern = re.compile("VRF:.*|------------- show.*") # pattern to know if the next show command start or if the next vrf in the routing entry starts
    psecond_match = pattern.search(contents[pfirst_match+1:]).span()[0] # match for the last line in the routing for that vrf
    psecond_match += pfirst_match - 1
    lookup = f'VRF: {vrf}' + '\n'
    match = re.findall(rf'( [A-Z]+.*{address_match}.*)(\n\s+via.*|\n\s+directly.*)?(\n\s+via.*|\n\s+directly.*)?(\n\s+via.*|\n\s+directly.*)?(\n\s+via.*|\n\s+directly.*)?(\n\s+via.*|\n\s+directly.*)?(\n\s+via.*|\n\s+directly.*)?(\n\s+via.*|\n\s+directly.*)?(\n\s+via.*|\n\s+directly.*)?(\n\s+via.*|\n\s+directly.*)?(\n\s+via.*|\n\s+directly.*)?', contents[pfirst_match:psecond_match])
    if match:
        match = match[0]
        lookup += ''.join(match)
    return lookup
                
                
def routing_table_ouput(contents, vrf):
    try:
        first_match = re.search(fr'VRF: {vrf}[\s].+', contents)
        first_line_no = first_match.span()[1]
        vrf_name = first_match.group()
        second_line_no = re.search("VRF:.*|------------- show.*", contents[first_line_no+1:]).span()[0]
        second_line_no += first_line_no
        return f'{vrf_name} + \n + {contents[first_line_no:second_line_no]}'
    except AttributeError as e:
         return 'vrf does not exist'
    
def ip_host_route(contents, command):
    try:
        contents += '\n------------- EndsHere -------------'
        try:
            vrf = re.findall(r'.+vrf\s*(.*)\shost', command, re.IGNORECASE)[0]
        except IndexError as e:
            vrf = 'default'
        start_output = re.search(rf'VRF: {vrf}', contents).span()[1]
        end_output = re.search(rf'VRF:.*|------------- EndsHere -------------', contents[start_output:]).span()[0]
        end_output += start_output
        actual_output = f'\nshow ip route vrf {vrf} host\n'
        actual_output += contents[start_output:end_output]
        return(actual_output)
    except Exception as e:
        print('vrf does not exists')

def ip_summary_route(contents, command):
    try: 
        contents += '\n------------- EndsHere -------------'
        try:
            vrf = re.findall(r'.+vrf\s*(.*)\ssummary', command, re.IGNORECASE)[0]
        except IndexError as e:
            vrf = 'default'
        actual_output = f'\nshow ip route vrf {vrf} summary\n\n'
        actual_output += '\n'.join(re.findall(r'Operating.*|Configured.*', contents, re.I))
        start_output = re.search(rf'VRF: {vrf}', contents).span()[1]
        end_output = re.search(rf'VRF:.*|------------- EndsHere -------------', contents[start_output:]).span()[0]
        end_output += start_output
        actual_output += '\n' + contents[start_output:end_output]
        return(actual_output)
    except Exception as e:
        print('vrf does not exists')

def handle_ip_route(self, command, match):
    if command in ['show ip route kernel unprogrammed', 'show ip route vrf all detail', 'show ip route vrf all host', 'show ip route vrf all summary']:
        return(self.command_searcher(command))
    elif command in ['show ip route vrf all']:
        return(self.command_searcher(command+" detail"))
    else:
        clist = command.split(' ')
        clist_len = len(clist)
        if clist_len == 3:
                return(routing_table_ouput(self.routing_contents, 'default'))
        elif clist_len == 4:
                if clist[3] == 'host':
                     return(ip_host_route(self.command_searcher('show ip route vrf all host'), command))
                elif clist[3] == 'summary':
                     return(ip_summary_route(self.command_searcher('show ip route vrf all summary'), command))
                vrfc = 'default'
                ip_add = clist[-1]
        elif clist_len == 5:
                if clist[3] == 'vrf':
                    vrfc = clist[-1]
                    return(routing_table_ouput(self.routing_contents, vrfc))
                else:
                    return('invalid input')
        elif clist_len == 6:
                if clist[5] == 'host':
                     return(ip_host_route(self.command_searcher('show ip route vrf all host'), command))
                elif clist[5] == 'summary':
                     return(ip_summary_route(self.command_searcher('show ip route vrf all summary'), command))
                try:
                    vrfc = clist[-2]
                    ip_add = clist[-1]
                    if (vrfc not in self.routes) and (vrfc != 'all'):
                        return('vrf does not exist')
                except KeyError as e:
                        return('invalid input')
        else:
                return('invalid input')
        if (len(clist) == 6 or len(clist) == 4):
            if vrfc == 'all':
                 output = '\n'
                 for vrf in self.routes:
                      route_ip = lookup(self.vrf_routing_table, ip_add, vrf, self.matched_routes)
                      self.matched_routes = []
                      output += vrf_route_lookup(self.routing_contents, route_ip, vrf) + '\n\n' 
                 return output
            else: 
                route_ip = lookup(self.vrf_routing_table, ip_add, vrfc, self.matched_routes)
                if route_ip == 'Invalid ip address':
                    return 'Invalid ip address'
                else:
                    self.matched_routes = []
                    return vrf_route_lookup(self.routing_contents, route_ip, vrfc)
                    