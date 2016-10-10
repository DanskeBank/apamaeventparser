from tokenize import generate_tokens
from StringIO import StringIO
import token
from apamaevent import ApamaEvent
from funcparserlib.parser import some, a, many, skip, maybe, NoParseError, with_forward_decls


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


def tokenize(s):
    return list(Token(*t)
                for t in generate_tokens(StringIO(s).readline))


def token_value(t):
    return t.value


def make_number(x):
    try:
        return int(x)
    except ValueError:
        return float(x)


def make_boolean(x):
    if x == 'true':
        return True
    elif x == 'false':
        return False
    raise NoParseError('Received boolean that is neither true or false', x)

name = some(lambda tok: tok.type == 'NAME') >> token_value
string = some(lambda tok: tok.type == 'STRING') >> token_value
number = some(lambda tok: tok.type == 'NUMBER') >> token_value >> make_number
true = a(Token(token.NAME, 'true')) >> token_value
false = a(Token(token.NAME, 'false')) >> token_value
boolean = (true | false) >> make_boolean
endmarker = some(lambda tok: tok.type == 'ENDMARKER')


def op(s):
    return a(Token(token.OP, s)) >> token_value
open_square_bracket = op('[')
close_square_bracket = op(']')
open_parenthesis = op('(')
close_parenthesis = op(')')
open_curly_bracket = op('{')
close_curly_bracket = op('}')
comma = op(',')
dot = op('.')
colon = op(':')


def make_channel(x):
    return x.strip('"')


def create_package(x):
    package = ''
    for p in x:
        package += p[0] + p[1]
    if package and package[-1] == '.':
        package = package[:-1]
    return package


def make_sequence(x):
    s = []
    if x:
        s = [x[0]] + x[1]
    return s


def make_dictionary(x):
    d = {}
    if x:
        d.update({x[0]: x[1]})
        for t in x[2]:
            d.update({t[0]: t[1]})
    return d


def make_body(x):
    body = []

    if x:
        body = [x[0]] + x[1]
    return body


def create_apama_event(x):
    print 'create_apama_event: ' + str(x)
    c = x[0] if x[0] else ''
    return ApamaEvent(channel=c, package_name=x[1], event_name=x[2], fields=x[3])

package_name = many(name + dot) >> create_package
event_name = name


@with_forward_decls
def sequence():
    return skip(open_square_bracket) + \
           maybe(types + many(skip(comma) + types)) + \
           skip(close_square_bracket) >> make_sequence


@with_forward_decls
def dictionary():
    return skip(open_curly_bracket) + \
           maybe(comparable_types + skip(colon) + types +
                 many(skip(comma) + comparable_types + skip(colon) + types)) + \
           skip(close_curly_bracket) >> make_dictionary


@with_forward_decls
def event_body():
    return skip(open_parenthesis) + maybe(types + many(skip(comma) + types)) + skip(close_parenthesis) >> make_body

simple_types = number | string | boolean
comparable_types = number | string
abstract_data_types = sequence | dictionary
channel = string + skip(comma) >> make_channel
event = maybe(channel) + maybe(package_name) + event_name + event_body >> create_apama_event
types = simple_types | abstract_data_types | event
