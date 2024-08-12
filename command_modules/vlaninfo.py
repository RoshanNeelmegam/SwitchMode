import re

def handle_per_vlan(self, command, match=None):
    contents = self.command_searcher('show vlan')
    vlan = re.findall(r'show vlan (\w+)', command)[0]
    output = '''VLAN  Name                             Status    Ports
----- -------------------------------- --------- -------------------------------\n'''
    ptr = 0
    for lines in contents.splitlines():
        # if vlan is found and in case there are interfaces that extend mulitple lines
        if ptr != 0:
            if not re.search(r'^[\d]+.+|indicates a Dynamic VLAN', lines):
                output += lines + '\n'
            else:
                ptr = 0
                return output
        # checking if the vlan exists
        if re.search(fr'^{vlan}(\*)? .+', lines):
            output += lines + '\n'
            ptr = 1
    if output:
        return output
    return ('Vlan does not exists')