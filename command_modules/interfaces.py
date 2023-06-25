import re

def show_int_br(content):
    int1 = re.findall('(\\S*) is (.*), line protocol is ([\\S]*)', content)
    interface_ip = re.findall(".*Internet address.*|No Internet protocol address assigned|Internet protocol processing disabled", content)
    interface_mtu = re.findall(".*IP MTU (\\S*) bytes", content)

    mtu_var = 0
    content = ("%-19s%-24s%-13s%-21s%-12s" % ("Interface", "IP Address","Status", "Protocol", "MTU"))
    content += '\n' + ("%-19s%-24s%-13s%-21s%-12s" % (18*"-", 23*"-",12*"-", 20*"-", 11*"-"))
    for i in range(0, len(int1)):
        if 'admin' in int1[i][1]:
            mtu_var += 1
            continue
        else:
            if 'assigned' in interface_ip[i].split():
                content += '\n' + ("%-19s%-24s%-13s%-21s%-12s " % (int1[i][0], interface_ip[i].split(" ")[4].replace('assigned', 'unassigned'),int1[i][1], int1[i][2],interface_mtu[i-mtu_var] ))  
            elif 'virtual' in interface_ip[i].split():
                content += '\n' + ("%-19s%-24s%-13s%-21s%-12s " % (int1[i][0], interface_ip[i].split(" ")[6].replace('assigned', 'unassigned'),int1[i][1], int1[i][2],interface_mtu[i-mtu_var] ))  

            else:
                content += '\n' + ("%-19s%-24s%-13s%-21s%-12s" % (int1[i][0], interface_ip[i].split(" ")[5],int1[i][1], int1[i][2], interface_mtu[i-mtu_var]))
    return(content)

def show_interfaces_status(content):
    return(content)