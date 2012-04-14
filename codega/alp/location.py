class Location(object):
    '''Stores location information.'''

    source = None
    lineno = None
    column = None
    position = None

    def __init__(self, source, lineno, column, position):
        self.source = source
        self.lineno = lineno
        self.column = column
        self.position = position

    def clone(self):
        '''Clone the location object.'''

        return Location(self.source, self.lineno, self.column, self.position)

    def update(self, text):
        '''Update the postion information using text.'''

        self.position += len(text)

        counttext = text.replace('\r\n', '\n').replace('\r', '\n')
        self.lineno += counttext.count('\n')

        pos = counttext.rfind('\n')
        if pos == -1:
            self.column += len(counttext)

        else:
            self.column = len(counttext) - pos - 1

    def __str__(self):
        return '%s (line %s, column %d)' % (self.source, self.lineno + 1, self.column + 1)

    def __repr__(self):
        return 'Location(\'%s\', line %d, column %d, position %d)' % (self.source, self.lineno + 1, self.column + 1, self.position)
