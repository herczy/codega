class Context(object):
    '''Generator context object

    Members:
    _source -- Source config entry used by generator
    _target -- Target config entry used by generator
    '''

    _source = None
    _target = None

    _generator = None
    _parser = None

    _settings = None

    def __init__(self, source, target, generator, parser, settings):
        self._source = source
        self._target = target
        self._generator = generator
        self._parser = parser
        self._settings = dict(settings)

    @property
    def source(self):
        return self._source

    @property
    def target(self):
        return self._target

    @property
    def generator(self):
        return self._source

    @property
    def parser(self):
        return self._source

    @property
    def settings(self):
        return self._settings

    def map(self, generator, sources, filt_expr=lambda node: True):
        return map(lambda source: generator(source, self), filter(filt_expr, sources))
