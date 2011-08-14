from base import *
from pack import CommandPack
from make import CommandMake
from build import CommandBuild
from clean import CommandClean

from codega.ordereddict import OrderedDict

class CommandMain(CommandContainer):
    def __init__(self, name, helpstring = None):
        commands = OrderedDict()
        commands['help'] = CommandHelp(self, 'Display list of commands with their meaning')
        commands['make'] = CommandMake()
        commands['clean'] = CommandClean()
        commands['build'] = CommandBuild()
        commands['pack'] = CommandPack()

        super(CommandMain, self).__init__(name, commands, helpstring = helpstring)
