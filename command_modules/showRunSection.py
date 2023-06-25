import re        

def shrunsec(contents, command):
    section_input = re.split('sec(?:t(?:i(?:on?)?)?)?', command)[-1].strip()
    section_output = ''
    relevant_section = False
    content = ''
    for line in contents.splitlines():
        if not line.startswith(' '):
            if relevant_section:
                content += section_output.rstrip() 
                if line.startswith('!'):
                    content += '\n' + line.rstrip() + '\n'
            relevant_section = False
            section_output = ''
        if re.match('.*' + section_input + '.*', line, re.I):
            relevant_section = True
        section_output += line +'\n'
    return content
