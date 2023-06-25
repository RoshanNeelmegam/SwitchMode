import re

def showLoggingLines(content, line_no):
    var = ''
    lines = content.split('\n')[-int(line_no):]
    for line in lines:
        var += line + '\n'
    return(var)

