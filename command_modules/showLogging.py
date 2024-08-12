# import re

# def showLoggingLines(content, line_no):
#     var = ''
#     lines = content.split('\n')[-int(line_no):]
#     for line in lines:
#         var += line + '\n'
#     return(var)

def handle_show_logging(self, command, match=None):
    splitted_command = command.split()
    if len(splitted_command) == 3:
        output = '\n'
        content = self.command_searcher('show logging')
        lines = content.split('\n')[-int(splitted_command[-1])-1:-1] # taking the last x lines. Last line is '' hence splitting from [line no - 1:-1]
        for line in lines:
            output += line + '\n'
        return(output)
    else:
        return('wrong command(too many inputs)')   
    