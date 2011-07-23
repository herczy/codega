'''Helps put together command-line interface commands'''

import os
import sys
import optparse

import traceback

from codega import logger

class CommandBase(object):
    '''Abstract base class for commands

    Members:
    _name -- Command name
    _helpstring -- Command help
    '''

    _name = None
    _helpstring = None

    @property
    def helpstring(self):
        return self._helpstring

    @property
    def name(self):
        return self._name

    def __init__(self, name, helpstring = None):
        self._name = name
        self._helpstring = helpstring if helpstring else '<no help supplied>'

    def prepare(self, argv):
        '''Prepare the argument list'''

        raise NotImplementedError("CommandBase.prepare is abstract")

    def execute(self):
        '''Run the command'''

        raise NotImplementedError("CommandBase.execute is abstract")

    def handle_exception(self, desc_short, desc_long):
        '''Handle some exception that occured during the execution

        Arguments:
        exception -- Caught exception
        '''

        for line in desc_long.split('\n'):
            logger.debug(line)

        logger.error('An error occured during the execution of %s: %s', self.name, desc_short)

    def run(self, argv):
        try:
            logger.info('Running command %s with arguments (%s)', self.name, ', '.join(map(repr, argv)))
            if not self.prepare(argv):
                return False

            return self.execute()

        except Exception, e:
            self.handle_exception(str(e), traceback.format_exc())
            return False

        except:
            self.handle_exception('unknown error', traceback.format_exc())
            return False

class OptparsedCommand(CommandBase):
    '''A command with optparse-style options

    Members:
    _option_list -- List of accepted command options
    _opts -- Optparse output, options
    _args -- Optparse output, extra arguments
    '''

    _option_list = None
    _opts = None
    _args = None

    @property
    def opts(self):
        return self._opts

    @property
    def args(self):
        return self._args

    def __init__(self, name, options = [], **kwargs):
        super(OptparsedCommand, self).__init__(name, **kwargs)

        self._option_list = options

    def prepare(self, argv):
        logger.debug('Preparing arguments')
        try:
            parser = optparse.OptionParser(option_list = self._option_list)
            self._opts, self._args = parser.parse_args(argv)
            return True

        except SystemExit, e:
            if e.code:
                logger.error('Option parser exited with error code %d', e.code)

            return False

class CommandContainer(CommandBase):
    '''A command that has further subcommands

    Members:
    _commands -- List of subcommands
    _args -- Arguments
    '''

    _commands = None
    _args = None

    def __init__(self, name, commands, **kwargs):
        super(CommandContainer, self).__init__(name, **kwargs)

        self._commands = commands

    def prepare(self, argv):
        self._args = argv
        return True

    def execute(self):
        if len(self._args) == 0:
            print >>sys.stderr, "Missing command"
            return False

        cmd, passon = self._args[0], self._args[1:]

        if not self._commands.has_key(cmd):
            logger.error('Command %s not found', cmd)
            return False

        return self._commands[cmd].run(passon)

    def __iter__(self):
        return iter(self._commands.iteritems())

class CommandHelp(CommandBase):
    '''A generic help command

    Members:
    _container -- Command container to use for collecting helps
    '''

    _container = None

    def __init__(self, container):
        super(CommandHelp, self).__init__('help', helpstring = 'Display help for command %s' % container.name)

        self._container = container

    def prepare(self, argv):
        if len(argv) != 0:
            critical("Help takes no arguments")
            return False

        return True

    def execute(self):
        lst = []
        maxcmd = 0
        for (cmd, obj) in self._container:
            if len(cmd) > maxcmd:
                maxcmd = len(cmd)

            lst.append((cmd, obj.helpstring))

        print >>sys.stderr, self._container.helpstring
        print >>sys.stderr
        for cmd, helpstring in lst:
            print >>sys.stderr, ' %s%s %s' % (cmd, ' ' * (maxcmd + 3), helpstring)

        return True
