import re

def showVersion(content):
    lines = content.split('\n')
    content = ''
    for line in lines:
        if re.search(r'Installed software packages:', line):
            break
        else:
            content += '\n' + line 
    return content