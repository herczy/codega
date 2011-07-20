from stringio import StringIO

class Context(object):
    '''Generator context object

    Members:
    _builder -- The builder object
    _config -- The configuration used
    _source -- Source config entry used by generator
    _target -- Target config entry used by generator
    '''

    _builder = None
    _config = None
    _source = None
    _target = None

    def __init__(self, builder, config, source, target):
        self._builder = builder
        self._config = config
        self._source = source
        self._target = target

    @property
    def builder(self):
        return self._builder

    @property
    def config(self):
        return self._config

    @property
    def source(self):
        return self._source

    @property
    def target(self):
        return self._target

    @property
    def settings(self):
        return self._target.settings

    def map(self, generator, sources):
        return map(lambda source: generator(source, self), sources)
