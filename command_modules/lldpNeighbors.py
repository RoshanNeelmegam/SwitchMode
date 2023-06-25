import re

def lldpNeighborsInitialization(contents, lldp_dict):
    interface_match_list = re.findall('Interface ([\\S]+) detected [^0]', contents)
    neighbor_id_list = re.findall('- System Name: "([\\S]+)"', contents)
    neighbor_port_id_list = re.findall('Port ID     : ([\\S]+)', contents)
    neighbor_mac_address = re.findall('Chassis ID     : ([\\S]+)', contents)
    # print(len(interface_match_list), len(neighbor_id_list), len(neighbor_port_id_list), len(neighbor_mac_address))
    for interface_no in range(0, len(interface_match_list)):
        lldp_dict[interface_match_list[interface_no]] = {'neighbor_id': neighbor_id_list[interface_no], 'neighor_port_id': neighbor_port_id_list[interface_no], 'neighbor_mac': neighbor_mac_address[interface_no]}
    return lldp_dict

def lldpOutput(lldp_dict):
    content = ("%-20s%-40s%-30s%-20s" % ("Port", "Neighbor Device ID", "Neighbor Port ID", "Neighbor System MAC"))
    for interface in lldp_dict:
            content += '\n' + ("%-20s%-40s%-30s%-20s" % (interface, lldp_dict[interface]['neighbor_id'], lldp_dict[interface]['neighor_port_id'].replace('"',''), lldp_dict[interface]['neighbor_mac']))
    return content
