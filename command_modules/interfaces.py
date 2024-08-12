import re

def show_int_br(content):
    int1 = re.findall('(\\S*) is (.*), line protocol is ([\\S]*)', content)
    interface_ip = re.findall(".*Internet address.*|No Internet protocol address assigned|Internet protocol processing disabled|Address being determined by DHCP", content)
    interface_mtu = re.findall(".*IP MTU (\\S*) bytes", content)
    mtu_var = 0
    output = ("%-19s%-24s%-13s%-21s%-12s" % ("Interface", "IP Address","Status", "Protocol", "MTU"))
    output += '\n' + ("%-19s%-24s%-13s%-21s%-12s" % (18*"-", 23*"-",12*"-", 20*"-", 11*"-"))
    for i in range(0, len(int1)):
        if 'admin' in int1[i][1]:
            mtu_var += 1
            continue
        else:
            if 'assigned' in interface_ip[i].split():
                output += '\n' + ("%-19s%-24s%-13s%-21s%-12s " % (int1[i][0], interface_ip[i].split(" ")[4].replace('assigned', 'unassigned'),int1[i][1], int1[i][2],interface_mtu[i-mtu_var] ))  
            elif 'virtual' in interface_ip[i].split():
                output += '\n' + ("%-19s%-24s%-13s%-21s%-12s " % (int1[i][0], interface_ip[i].split(" ")[6].replace('assigned', 'unassigned'),int1[i][1], int1[i][2],interface_mtu[i-mtu_var] ))  

            else:
                try:
                    output += '\n' + ("%-19s%-24s%-13s%-21s%-12s" % (int1[i][0], interface_ip[i].split(" ")[5],int1[i][1], int1[i][2], interface_mtu[i-mtu_var]))
                except IndexError as e:
                    output += '\n' + ("%-19s%-24s%-13s%-21s%-12s" % (int1[i][0], 'Null',int1[i][1], int1[i][2], 'Null'))
    return(output)

def show_interfaces_status(content):
    return(content)

#per interface output functions here
def individual_interface_status(content, command):
    if re.search('show interfaces status$', command):
        return content
    else:
        output = content.splitlines()[2] + '\n'
        try:
            interface = re.findall(r'show interfaces (\w.+) status', command, re.IGNORECASE)
            interface = re.sub(' ', '', interface[0])
            interface = re.sub('Et(h(e(r(n(e(t?)?)?)?)?)?)?', 'Et', interface, flags=re.IGNORECASE)
            interface = re.sub('Po(r(t(-(c(h(a(n(n(e(l?)?)?)?)?)?)?)?)?)?)?', 'Po', interface, flags=re.IGNORECASE)
            interface = re.sub('Ma(n(a(g(e(m(e(n(t?)?)?)?)?)?)?)?)?', 'Ma', interface, flags=re.IGNORECASE)
            if not re.search(r'[0-9]', interface):
                return('Please enter a valid interface')
            for lines in content.splitlines():
                if re.search(rf'^{interface}\b', lines, re.IGNORECASE):
                    output += lines + '\n'
                    return output
            return('Interface does not exist')
        except IndexError as e:
            return('Please enter the interface number')   

def interfaces_switchport(content, command):
    if re.search('show interfaces switchport$', command):
        return content
    else:
        matched = False
        try:
            interface = re.findall(r'show interfaces (\w.+) switchport', command, re.IGNORECASE)
            interface = re.sub(' ', '', interface[0])
            interface = re.sub('Et(h(e(r(n(e(t?)?)?)?)?)?)?', 'Et', interface, flags=re.IGNORECASE)
            interface = re.sub('Po(r(t(-(c(h(a(n(n(e(l?)?)?)?)?)?)?)?)?)?)?', 'Po', interface, flags=re.IGNORECASE)
            if not re.search(r'[0-9]', interface):
                return('Please enter a valid interface')
            output = ''
            for lines in content.splitlines():
                if matched:
                    if re.search(r'^(Name:.*|\s+)', lines):
                        return (re.sub(r'\n\n', '\n', output))
                    output += lines + '\n'
                if not matched:
                    match = re.search(rf'^Name: {interface}\b', lines, re.IGNORECASE)
                    if match:
                        output += lines + '\n'
                        matched = True
            if output == '':
                return('Interface does not exists or is not a switchport')
            else:
                return (re.sub(r'\n\n', '\n', output))
        except IndexError as e:
            return('Please enter the interface number')      
        
def mac_detail(content, command):
    matched = False
    if re.search('show interfaces mac-detail$', command):
        return content
    else:
        try:
            interface = re.findall(r'show interfaces (\w.+) mac-detail', command)
            interface = re.sub(' ', '', interface[0])
            interface = re.sub('Et(h(e(r(n(e(t?)?)?)?)?)?)?', 'Ethernet', interface, flags=re.IGNORECASE)
            if not re.search(r'[0-9]', interface):
                return('Please enter a valid interface')
            output = ''
            for lines in content.splitlines():
                if matched:
                    if re.search(r'^(Ethernet*|\s*\n)', lines):
                        return (re.sub(r'\n\n', '\n', output))
                    output += lines + '\n'
                if not matched:
                    match = re.search(rf'^{interface}\b', lines, re.IGNORECASE)
                    if match:
                        output += lines + '\n'
                        matched = True
            if output == '':
                return('Interface does not exist')
            else:
                return (re.sub(r'\n\n', '\n', output))
        except IndexError as e:
            return('Please enter the interface')
    
def phy_detail(content, command):
    matched = False
    if re.search('show interfaces mac-detail$', command):
        return content
    else:
        if re.search('show interfaces phy-detail$', command):
            return content
        try:
            interface = re.findall(r'show interfaces (\w.+) phy-detail', command)
            interface = re.sub(' ', '', interface[0])
            interface = re.sub('Et(h(e(r(n(e(t?)?)?)?)?)?)?', 'Ethernet', interface, flags=re.IGNORECASE)
            if not re.search(r'[0-9]', interface):
                return('Please enter a valid interface')
            output = ''
            for lines in content.splitlines():
                if matched:
                    if re.search(r'^(Ethernet*|\s*\n)', lines):
                        return (re.sub(r'\n\n', '\n', output))
                    output += lines + '\n'
                if not matched:
                    match = re.search(rf'^{interface}\b', lines, re.IGNORECASE)
                    if match:
                        output += lines + '\n'
                        matched = True
            if output == '':
                return('Interface does not exist')
            else: 
                return (re.sub(r'\n\n', '\n', output))
        except IndexError as e:
            return('Please enter the interface')
    
def handle_individual_interfaces(self, command, match):
    matched = False
    content = self.command_searcher('show interfaces.*')
    if re.search('show interfaces$', command):
        return content
    else:
        try:
            interface = re.findall(r'show interfaces (\w.+)', command)
            interface = re.sub(' ', '', interface[0])
            interface = re.sub('Et(h(e(r(n(e(t?)?)?)?)?)?)?', 'Ethernet', interface, flags=re.IGNORECASE)
            interface = re.sub('Po(r(t(-(c(h(a(n(n(e(l?)?)?)?)?)?)?)?)?)?)?', 'Port-Channel', interface, flags=re.IGNORECASE)
            interface = re.sub('vl(a(n?)?)?', 'Vlan', interface, flags=re.IGNORECASE)
            interface = re.sub('Ma(n(a(g(e(m(e(n(t?)?)?)?)?)?)?)?)?', 'Management', interface, flags=re.IGNORECASE)
            interface = re.sub('lo(o(p(b(a(c(k?)?)?)?)?)?)?', 'Loopback', interface, flags=re.IGNORECASE)
            if not re.search(r'[0-9]', interface):
                return('Please enter a valid interface')
            output = ''
            for lines in content.splitlines():
                if matched:
                    if re.search(r'^(Ethernet*|Port-Channel*|Vlan*|Vxlan*|Loopback*|Management*)', lines):
                        return (re.sub(r'\n\n', '\n', output))
                    output += lines + '\n'
                if not matched:
                    match = re.search(rf'^{interface}\b', lines, re.IGNORECASE)
                    if match:
                        output += lines + '\n'
                        matched = True
            if output == '':
                return('Interface does not exist')
            else: 
                return (re.sub(r'\n\n', '\n', output))
        except IndexError as e:
            return('Please enter the interface') 
    
def handle_show_interfaces_options(self, command, match):
    # more info on regex here: https://regex101.com/r/rPk0ov/1
    # optimized this for better handling
    interface_type = match.group(1)
    option = match.group(5)
    handler_map = {
        "status": [individual_interface_status, 'show interfaces.* status'],
        "switchport": [interfaces_switchport, 'show interfaces.* switchport'],
        "mac-detail": [mac_detail, 'show interfaces.* mac detail'],
        "phy-detail": [phy_detail, 'show interfaces.* phy detail']
    }
    return handler_map[option][0](self.command_searcher(handler_map[option][1]), command)   