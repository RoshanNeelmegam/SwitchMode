from command_modules.interfaces import *
from command_modules.showVersion import *
from command_modules.showRunSection import *
from command_modules.lldpNeighbors import *
from command_modules.showLogging import *

mapCommand = {
    'show ip interface brief': {'function': show_int_br, 'parent_command': 'show ip interface', 'is_static': True, 'dict_input': False},
    'show version': {'function': showVersion, 'parent_command': 'show version detail', 'is_static': True, 'dict_input': False},
    'show lldp neighbors': {'function': lldpOutput, 'parent_command': 'show lldp neighbors detail', 'is_static': True, 'dict_input': True},
}

def handle_mapped_command(self, command):
    map_info = mapCommand[command]
    if map_info['is_static']:
        input_data = self.command_searcher(map_info['parent_command']) if not map_info['dict_input'] else self.lldp_dictionary
        return map_info['function'](input_data)