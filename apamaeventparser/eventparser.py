from tokenize import generate_tokens

try:
    from StringIO import StringIO
except ImportError:
    from io import StringIO
import token
from apamaevent import ApamaEvent
from funcparserlib.parser import some, a, many, skip, maybe, NoParseError, with_forward_decls, finished, forward_decl


class Token(object):
    def __init__(self, code, value, start=(0, 0), end=(0, 0), line=''):
        self.code = code
        self.value = value
        self.start = start
        self.end = end
        self.line = line

    @property
    def type(self):
        return token.tok_name[self.code]

    def __unicode__(self):
        pos = '-'.join('%d,%d' % x for x in [self.start, self.end])
        return "%s %s '%s'" % (pos, self.type, self.value)

    def __repr__(self):
        return 'Token(%r, %r, %r, %r, %r)' % (self.code, self.value, self.start, self.end, self.line)

    def __eq__(self, other):
        return (self.code, self.value) == (other.code, other.value)

    def __ne__(self, other):
        return not self.__eq__(other)


def _tokenize(s):
    """Take a string and return a list of Token objects"""
    return list(Token(*t)
                for t in generate_tokens(StringIO(s).readline))


def _token_value(t):
    """Get the value of a Token"""
    return t.value


def _make_number(x):
    """Cast a number to int or float"""
    try:
        return int(x)
    except ValueError:
        return float(x)


def _make_boolean(x):
    """Map event true/false to python True/False"""
    if x == 'true':
        return True
    elif x == 'false':
        return False
    raise NoParseError('Received boolean that is neither true or false', x)


def _strip_quotes(x):
    """Strip quotes from the channel name"""
    return x.strip('"')


def _make_package(x):
    """Get the package name and drop the last '.' """
    package = ''
    for p in x:
        package += p[0] + p[1]
    if package and package[-1] == '.':
        package = package[:-1]
    return package


def _make_sequence(x):
    """Convert an event _sequence to a python list"""
    s = []
    if x:
        s = [x[0]] + x[1]
    return s


def _make_dictionary(x):
    """Convert an event _dictionary to a dict"""
    d = {}
    if x:
        d.update({x[0]: x[1]})
        for t in x[2]:
            d.update({t[0]: t[1]})
    return d


def _make_event_body(x):
    """Convert the fields of an event to a list"""
    body = []
    if x:
        body = [x[0]] + x[1]
    return body


def _create_apama_event(x):
    """Create the ApamaEvent object"""
    try:
        c = x[0] if x[0] else ''
        return ApamaEvent(channel=c, package_name=x[1], event_name=x[2], fields=x[3])
    except TypeError:
        if x is None:
            return x
        raise TypeError


# Definitions of types from the tokenizer
_name = some(lambda tok: tok.type == 'NAME') >> _token_value
_string = some(lambda tok: tok.type == 'STRING') >> _token_value >> _strip_quotes
_number = some(lambda tok: tok.type == 'NUMBER') >> _token_value >> _make_number
_true = a(Token(token.NAME, 'true')) >> _token_value
_false = a(Token(token.NAME, 'false')) >> _token_value
_boolean = (_true | _false) >> _make_boolean
_endmarker = some(lambda tok: tok.type == 'ENDMARKER')


# Definition of operators
def _op(s):
    """Helper function for defining operators"""
    return a(Token(token.OP, s)) >> _token_value


_open_square_bracket = _op('[')
_close_square_bracket = _op(']')
_open_parenthesis = _op('(')
_close_parenthesis = _op(')')
_open_curly_bracket = _op('{')
_close_curly_bracket = _op('}')
_comma = _op(',')
_dot = _op('.')
_colon = _op(':')

# Declaration of recursive types so they can be used now
_sequence = forward_decl()
_dictionary = forward_decl()
_event_body = forward_decl()

# Definition of all the the Apama event parts
_simple_types = _number | _string | _boolean
_comparable_types = _number | _string  # _comparable_types are for dictionary keys
_abstract_data_types = _sequence | _dictionary
_channel = _string + skip(_comma) >> _strip_quotes
_package_name = many(_name + _dot) >> _make_package
_event_name = _name
_event = ((_endmarker + finished >> (lambda x: None)) |
          maybe(_channel) + maybe(_package_name) + _event_name + _event_body) >> _create_apama_event
_types = _simple_types | _abstract_data_types | _event

# Definition of recursive types which use the above definitions
_sequence.define(skip(_open_square_bracket) +
                 maybe(_types + many(skip(_comma) + _types)) +
                 skip(_close_square_bracket) >> _make_sequence)
_dictionary.define(skip(_open_curly_bracket) +
                   maybe(_comparable_types + skip(_colon) + _types +
                         many(skip(_comma) + _comparable_types + skip(_colon) + _types)) +
                   skip(_close_curly_bracket) >> _make_dictionary)
_event_body.define(skip(_open_parenthesis) +
                   maybe(_types + many(skip(_comma) + _types)) +
                   skip(_close_parenthesis) >> _make_event_body)

def parse(s):
    """Pass one event to be parsed"""
    tokens = _tokenize(s)
    return _event.parse(tokens)