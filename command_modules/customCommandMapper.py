from command_modules.interfaces import *
from command_modules.showVersion import *
from command_modules.showRunSection import *
from command_modules.lldpNeighbors import *
from command_modules.showLogging import *

mapCommand = {
    'show ip interfaces brief': {'function': show_int_br, 'parent_command': 'show ip interfaces', 'is_static': True, 'dict_input': False},
    'show version': {'function': showVersion, 'parent_command': 'show version detail', 'is_static': True, 'dict_input': False},
    'show interfaces status': {'function': show_interfaces_status, 'parent_command': 'show interfaces status', 'is_static': True, 'dict_input': False},
    'show lldp neighbors': {'function': lldpOutput, 'parent_command': 'show lldp neighbors detail', 'is_static': True, 'dict_input': True},
}

