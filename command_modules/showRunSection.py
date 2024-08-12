import re        

def shrunsec(self, command, match=None):
    section_input = re.split('sec(?:t(?:i(?:on?)?)?)?', command)[-1].strip()
    section_output = ''
    relevant_section = False
    contents = self.command_searcher('show running-config')
    output = ''
    for line in contents.splitlines():
        if not line.startswith(' '):
            if relevant_section:
                output += section_output.rstrip() 
                if line.startswith('!'):
                    output += '\n' + line.rstrip() + '\n'
            relevant_section = False
            section_output = ''
        if re.match('.*' + section_input + '.*', line, re.I):
            relevant_section = True
        section_output += line +'\n'
    return output

def shrunint(self, command, match=None):
    matched = False
    contents = self.command_searcher('show running-config')
    try:
        interface = re.findall(r'show running-config interfaces (\w.+)', command)
        interface = re.sub(' ', '', interface[0])
        interface =  re.sub('et(h(e(r(n(e(t?)?)?)?)?)?)?', 'Ethernet', interface, flags=re.IGNORECASE)
        interface =  re.sub('po(r(t(-(c(h(a(n(n(e(l?)?)?)?)?)?)?)?)?)?)?', 'Port-Channel', interface, flags=re.IGNORECASE)
        interface =  re.sub('vl(a(n?)?)?', 'Vlan', interface, flags=re.IGNORECASE)
        interface =  re.sub('lo(o(p(b(a(c(k?)?)?)?)?)?)?', 'Loopback', interface, flags=re.IGNORECASE)
        interface = re.sub('Ma(n(a(g(e(m(e(n(t?)?)?)?)?)?)?)?)?', 'Management', interface, flags=re.IGNORECASE)        
        if not re.search(r'[0-9]', interface):
            return('Please enter a valid interface')
        content = ''
        for lines in contents.splitlines():
            if matched:
                if re.search(r'^!', lines):
                    return content
                content += lines + '\n'
            if not matched:
                matches = re.search(rf'^interface\b {interface}\b', lines, re.IGNORECASE)
                if matches:
                    content += lines + '\n'
                    matched = True
        if content == '':
            return('interface does not exist')
    except IndexError as e:
        return('Please enter the interface')



