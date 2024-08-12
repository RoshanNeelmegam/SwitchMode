import re

def bgp_summary(contents, command):
    try:
        contents += '\n------------- EndsHere -------------'
        try: 
            vrf = re.findall(r'.+vrf\s*(.*)', command, re.IGNORECASE)[0]
        except IndexError as e:
            vrf = 'default'
        start_output = re.search(rf'BGP summary information for VRF {vrf}', contents).span()[1]
        end_output = re.search(rf'BGP summary information for VRF.*|------------- EndsHere -------------', contents[start_output:]).span()[0]
        end_output += start_output
        actual_output = f'\nBGP summary information for VRF {vrf}\n'
        actual_output += contents[start_output:end_output]
        return(actual_output)
    except Exception as e:
        print('Excception occurred (possibly vrf does not exists)')

def bgp_neighbor(contents, command):
    clist = command.split()
    contents += '\n------------- EndsHere -------------'
    if len(clist) == 4 or len(clist) == 6:
        try:
            try: 
                vrf = re.findall(r'.+vrf\s*(.*)', command, re.IGNORECASE)[0]
            except IndexError as e:
                vrf = 'default'
            output = f'\n------------- show ip(v6) bgp neighbor vrf {vrf} -------------\n'
            matched_output = re.findall (rf'BGP neighbor is.*\n.*\n.*VRF {vrf}\n(?:.*\n){{0,110}}', contents)
            output += '\n'.join(matched_output)
            return output
        except Exception as e:
            print('Excception occurred (possibly vrf does not exists)')
    elif len(clist) == 5 and re.search(r'.* \d+.\d+.\d+.\d+$', command):
        try:
            neighbor = re.findall(r'\s*(\d+\.\d+\.\d+\.\d+)', command)[0]
            vrf = 'default'
        except Exception as e:
            print('Exception in neighbour/vrf')
        output = f'\n------------- show ip(v6) bgp neighbor {neighbor} vrf default -------------\n'
        matched_output = re.findall (rf'BGP neighbor is {neighbor}, .*\n.*\n.*VRF {vrf}\n(?:.*\n){{0,110}}', contents)
        output += '\n'.join(matched_output)
        return output   
    elif len(clist) == 7 and re.search(r'.* \d+.\d+.\d+.\d+.*', command):
        try:
            neighbor = re.findall(r'\s(\d+\.\d+\.\d+\.\d+)', command)[0]
            vrf = re.findall(r'.+vrf\s*(.*)', command, re.IGNORECASE)[0]
        except Exception as e:
            print('Exception in neighbour/vrf')          
        output = f'\n------------- show ip(v6) bgp neighbor {neighbor} vrf {vrf} -------------\n'
        matched_output = re.findall (rf'BGP neighbor is {neighbor}, .*\n.*\n.*VRF {vrf}\n(?:.*\n){{0,110}}', contents)
        output += '\n'.join(matched_output)
        return output   
        
def bgp_routes(contents, command): 
    try:
        contents += '\n------------- EndsHere -------------'
        try: 
            vrf = re.findall(r'.+vrf\s*(.*)', command, re.IGNORECASE)[0]
        except IndexError as e:
            vrf = 'default'
        start_output = re.search(rf'BGP routing table information for VRF {vrf}', contents).span()[1]
        end_output = re.search(rf'BGP routing table information for VRF.*|------------- EndsHere -------------', contents[start_output:]).span()[0]
        end_output += start_output
        actual_output = f'\nBGP routing table information for VRF {vrf}\n'
        actual_output += contents[start_output:end_output]
        return(actual_output)    
    except Exception as e:
        print('Excception occurred (possibly vrf does not exists)')

def handle_bgp_commands(self, command, match):
    if command in ['show ip bgp neighbor vrf all', 'show ip bgp summary vrf all', 'show ip bgp vrf all']:
        return(self.command_searcher(command))
    handler_map = {
        'show ip bgp summary': bgp_summary,
        'show ip bgp neighbor': bgp_neighbor,
        'show ip bgp': bgp_routes,
        'show ipv6 bgp summary': bgp_summary,
        'show ipv6 bgp neighbor': bgp_neighbor,
        'show ipv6 bgp': bgp_routes,
    }
    for key in handler_map:
        if re.match(fr'{key}.*', command) and command not in 'show ipv6 bgp peers':
            return(handler_map[key](self.command_searcher(key+' vrf all'), command))
