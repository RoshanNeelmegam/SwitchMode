import re
from ipaddress import IPv6Network, IPv6Address

def ipv6_route_parsing(contents):
    routes = {}
    vrfs_list_original = re.findall(r'VRF: (.+)', contents)
    collected_data = re.findall(r'\s+([0-9a-fA-F:]+\/\d+) \[\d+/\d+\]|(VRF: .*)', contents) # more info on regex: https://regex101.com/r/g7pVs8/1
    parsed_data = [item for sublist in collected_data for item in sublist if item]
    for vrf in vrfs_list_original:
        if vrf == 'Table_Ends_Here':
            break
        vrf_to_start_search = parsed_data.index(f'VRF: {vrf}') + 1
        vrf_to_end_search = parsed_data.index(f'VRF: {vrfs_list_original[vrfs_list_original.index(vrf) + 1]}')
        routes[vrf] = parsed_data[vrf_to_start_search:vrf_to_end_search]
    return routes

def creating_ipv6_vrf_routing_table(routes):
    ipv6_vrf_table = {}
    for vrf in routes:
            ipv6_vrf_table[vrf] = {}
            for prefix in routes[vrf]:
                ipv6Object = IPv6Network(prefix)
                ipv6_vrf_table[vrf][ipv6Object] = prefix
    return ipv6_vrf_table

def ipv6_route_lookup(ipv6_parsed_vrf_routing_table, ipv6_address, vrf = None):
     if vrf == None:
          vrf = 'default'
     matched_routes = []
     for prefix in ipv6_parsed_vrf_routing_table[vrf]:
          if IPv6Address(ipv6_address) in prefix:
               matched_routes.append(ipv6_parsed_vrf_routing_table[vrf][prefix])
     try: 
          maxPrefixLength = max([ int(item.split(r'/')[1]) for item in matched_routes ])
     except Exception as e:
          return('no ipv6 addresses matching for the provided address')
     return re.search(fr'.*/{maxPrefixLength}', '\n'.join(matched_routes)).group()

def ipv6_lookup_match(contents, address_match, vrf):
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

def ipv6_routing_table_ouput(contents, vrf):
    try:
        first_match = re.search(fr'VRF: {vrf}[\s].+', contents)
        first_line_no = first_match.span()[1]
        vrf_name = first_match.group()
        second_line_no = re.search("VRF:.*|------------- show.*", contents[first_line_no+1:]).span()[0]
        second_line_no += first_line_no
        return f'{vrf_name} + \n + {contents[first_line_no:second_line_no]}'
    except AttributeError as e:
         return 'vrf does not exist'

def ipv6_host_route(contents, command):
    try:
        contents += '\n------------- EndsHere -------------'
        try:
            vrf = re.findall(r'.+vrf\s*(.*)\shost', command, re.IGNORECASE)[0]
        except IndexError as e:
            vrf = 'default'
        start_output = re.search(rf'VRF: {vrf}', contents).span()[1]
        end_output = re.search(rf'VRF:.*|------------- EndsHere -------------', contents[start_output:]).span()[0]
        end_output += start_output
        actual_output = f'\nshow ipv6 route vrf {vrf} host\n'
        actual_output += contents[start_output:end_output]
        return(actual_output)
    except Exception as e:
        print('vrf does not exists')

def ipv6_summary_route(contents, command):
    try: 
        contents += '\n------------- EndsHere -------------'
        try:
            vrf = re.findall(r'.+vrf\s*(.*)\ssummary', command, re.IGNORECASE)[0]
        except IndexError as e:
            vrf = 'default'
        actual_output = f'\nshow ipv6 route vrf {vrf} summary\n\n'
        actual_output += '\n'.join(re.findall(r'Operating.*|Configured.*', contents, re.I))
        start_output = re.search(rf'VRF: {vrf}', contents).span()[1]
        end_output = re.search(rf'VRF:.*|------------- EndsHere -------------', contents[start_output:]).span()[0]
        end_output += start_output
        actual_output += '\n' + contents[start_output:end_output]
        return(actual_output)
    except Exception as e:
        print('vrf does not exists')

def handle_ipv6_route(self, command, match):
    if command in ['show ipv6 route kernel unprogrammed', 'show ipv6 route vrf all detail', 'show ipv6 route vrf all host', 'show ipv6 route vrf all summary']:
        return(self.command_searcher(command))
    elif command in ['show ipv6 route vrf all']:
        return(self.command_searcher(command+" detail"))
    else:
        clist = command.split(' ')
        clist_len = len(clist)
        if clist_len == 3:
                return(ipv6_routing_table_ouput(self.ipv6_routing_contents, 'default'))
        elif clist_len == 4:
                if clist[3] == 'host':
                     return(ipv6_host_route(self.command_searcher('show ipv6 route vrf all host'), command))
                elif clist[3] == 'summary':
                     return(ipv6_summary_route(self.command_searcher('show ipv6 route vrf all summary'), command))
                vrfc = 'default'
                ip_add = clist[-1]
        elif clist_len == 5:
                if clist[3] == 'vrf':
                    vrfc = clist[-1]
                    return(ipv6_routing_table_ouput(self.ipv6_routing_contents, vrfc))
                else:
                    return('invalid input')
        elif clist_len == 6:
                if clist[5] == 'host':
                     return(ipv6_host_route(self.command_searcher('show ipv6 route vrf all host'), command))
                elif clist[5] == 'summary':
                     return(ipv6_summary_route(self.command_searcher('show ipv6 route vrf all summary'), command))
                try:
                    vrfc = clist[-2]
                    ip_add = clist[-1]
                    if vrfc not in self.routes and (vrfc != 'all'):
                        return('vrf does not exist')
                except KeyError as e:
                        return('invalid input')
        else:
                return('invalid input')
        if (len(clist) == 6 or len(clist) == 4):
            if vrfc == "all":
                output = '\n'
                for vrf in self.routes:
                    route_ip = ipv6_route_lookup(self.ipv6_vrf_routing_table, ip_add, vrf)
                    output += ipv6_lookup_match(self.ipv6_routing_contents, route_ip, vrf) + '\n\n' 
                return output
            else:
                route_ip = ipv6_route_lookup(self.ipv6_vrf_routing_table, ip_add, vrfc)
                if route_ip == 'Invalid ipv6 address':
                    return 'Invalid ipv6 address'
                elif route_ip == 'no ipv6 addresses matching for the provided address':
                    return('no ipv6 addresses matching in the specified vrf for the provided address')
                else:
                    return ipv6_lookup_match(self.ipv6_routing_contents, route_ip, vrfc)