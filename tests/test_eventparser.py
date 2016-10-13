import unittest

from apamaeventparser.apamaevent import ApamaEvent

from apamaeventparser.eventparser import parse, _tokenize, _channel, _package_name, _event_name, _event_body, _sequence, _dictionary


class TestEvents(unittest.TestCase):

    def test_no_event(self):
        expected_event = None
        parsed_event = parse('')
        self.assertEqual(parsed_event, expected_event)

    def test_simple_event(self):
        expected_event = ApamaEvent(event_name='a')
        parsed_event = parse('a()')
        self.assertEqual(parsed_event, expected_event)

    def test_package_one_level(self):
        expected_event = ApamaEvent(package_name='heimdall', event_name='ragnarok')
        parsed_event = parse('heimdall.ragnarok()')
        self.assertEqual(parsed_event, expected_event)

    def test_package_two_levels(self):
        expected_event = ApamaEvent(package_name='heimdall.horn', event_name='ragnarok')
        parsed_event = parse('heimdall.horn.ragnarok()')
        self.assertEqual(parsed_event, expected_event)

    def test_package_many_levels(self):
        expected_event = ApamaEvent(package_name='heimdall.guard.rainbow.bridge.blow.horn', event_name='ragnarok')
        parsed_event = parse('heimdall.guard.rainbow.bridge.blow.horn.ragnarok()')
        self.assertEqual(parsed_event, expected_event)

    def test_simple_fields(self):
        expected_event = ApamaEvent(package_name='heimdall.horn',
                                    event_name='ragnarok',
                                    fields=['valhalla', 1, 3.14, 1.0e6, False, True])
        parsed_event = parse('heimdall.horn.ragnarok("valhalla", 1, 3.14, 1.0e6, false, true)')
        self.assertEqual(parsed_event, expected_event)

    def test_channel(self):
        expected_event = ApamaEvent(channel='channel',
                                    package_name='heimdall.horn',
                                    event_name='ragnarok',
                                    fields=['valhalla', 1, 3.14, 1.0e6, False, True])
        parsed_event = parse('"channel",heimdall.horn.ragnarok("valhalla", 1, 3.14, 1.0e6, false, true)')
        self.assertEqual(parsed_event, expected_event)

    def test_nested_event(self):
        expected_event = ApamaEvent(channel='channel',
                                    package_name='heimdall.horn',
                                    event_name='ragnarok',
                                    fields=[
                                        ApamaEvent(package_name='rainbow.bridge',
                                                   event_name='breached',
                                                   fields=[True])])
        parsed_event = parse('"channel",heimdall.horn.ragnarok(rainbow.bridge.breached(true))')
        self.assertEqual(parsed_event, expected_event)

    def test_readme_example(self):
        expected_event = ApamaEvent(package_name='com.apama',
                                    event_name='Event',
                                    fields=['Field', 1.234, 7, False, ['a', 'b', 'c'], {'key': 'value'}])
        parsed_event = parse('com.apama.Event("Field", 1.234, 7, false, ["a","b","c"], {"key": "value"})')
        self.assertEqual(parsed_event, expected_event)


class TestEventParts(unittest.TestCase):
    def test_channel(self):
        expected_result = 'channel'
        tokens = _tokenize('"channel",')
        parsed_channel = _channel.parse(tokens)
        self.assertEqual(parsed_channel, expected_result)

    def test_package_name(self):
        expected_result = 'heimdall.guard.rainbow.bridge.blow.horn'
        tokens = _tokenize('heimdall.guard.rainbow.bridge.blow.horn.')
        parsed_package = _package_name.parse(tokens)
        self.assertEqual(parsed_package, expected_result)

    def test_event_name(self):
        expected_result = 'ragnarok'
        tokens = _tokenize('ragnarok')
        parsed_package = _event_name.parse(tokens)
        self.assertEqual(parsed_package, expected_result)

    def test_event_body_simple_types(self):
        expected_result = ['valhalla', 1, 3.14, 1.0e6, True, False]
        tokens = _tokenize('("valhalla", 1, 3.14, 1.0e6, true, false)')
        parsed_package = _event_body.parse(tokens)
        self.assertEqual(parsed_package, expected_result)

    def test_event_body_all_types(self):
        expected_result = ['valhalla', 1, 3.14, 1.0e6, True, False, [1, 2, 3, 4],
                           {'Thor': 'Mjolner', 'Odin': 'Gungnir', 'Freja': 'Falkedragt'}]
        tokens = _tokenize('("valhalla", 1, 3.14, 1.0e6, true, false,[1,2,3,4],'
                           '{"Thor": "Mjolner", "Odin": "Gungnir", "Freja": "Falkedragt"})')
        parsed_package = _event_body.parse(tokens)
        self.assertEqual(parsed_package, expected_result)

    def test_sequence_string(self):
        expected_result = ['a', 'b', 'c']
        tokens = _tokenize('["a","b","c"]')
        parsed_package = _sequence.parse(tokens)
        self.assertEqual(parsed_package, expected_result)

    def test_sequence_numbers(self):
        expected_result = [1, 2, 3, 4]
        tokens = _tokenize('[1,2,3,4]')
        parsed_package = _sequence.parse(tokens)
        self.assertEqual(parsed_package, expected_result)

    def test_one_item_sequence(self):
        expected_result = ['Thor']
        tokens = _tokenize('["Thor"]')
        parsed_package = _sequence.parse(tokens)
        self.assertEqual(parsed_package, expected_result)

    def test_empty_sequence(self):
        expected_result = []
        tokens = _tokenize('[]')
        parsed_package = _sequence.parse(tokens)
        self.assertEqual(parsed_package, expected_result)

    def test_sequence_in_sequence(self):
        expected_result = [[1, 2, 3], [4, 5, 6], [7, 8], [9]]
        tokens = _tokenize('[[1,2,3],[4,5,6],[7,8],[9]]')
        parsed_package = _sequence.parse(tokens)
        self.assertEqual(parsed_package, expected_result)

    def test_empty_sequence_in_sequence(self):
        expected_result = [[]]
        tokens = _tokenize('[[]]')
        parsed_package = _sequence.parse(tokens)
        self.assertEqual(parsed_package, expected_result)

    def test_sequence_in_sequence_in_sequence(self):
        # This is not a legal event type since sequences need to all be the same type, however it still parses...
        expected_result = [1, 2, 3, ['a', 'b', 'c'], [['aa', 'bb'], ['cc', 'dd']]]
        tokens = _tokenize('[1,2,3,["a","b","c"],[["aa","bb"],["cc","dd"]]]')
        parsed_package = _sequence.parse(tokens)
        self.assertEqual(parsed_package, expected_result)

    def test_empty_sequence_in_sequence_in_sequence(self):
        expected_result = [[[]]]
        tokens = _tokenize('[[[]]]')
        parsed_package = _sequence.parse(tokens)
        self.assertEqual(parsed_package, expected_result)

    def test_empty_dictionary(self):
        expected_result = {}
        tokens = _tokenize('{}')
        parsed_package = _dictionary.parse(tokens)
        self.assertEqual(parsed_package, expected_result)

    def test_dictionary(self):
        expected_result = {'Thor': 'Mjolner', 'Odin': 'Gungnir', 'Freja': 'Falkedragt'}
        tokens = _tokenize('{"Thor": "Mjolner", "Odin": "Gungnir", "Freja": "Falkedragt"}')
        parsed_package = _dictionary.parse(tokens)
        self.assertEqual(parsed_package, expected_result)

    def test_dictionary_in_dictionary(self):
        expected_result = {'other': {},
                           'Weapons': {'Thor': 'Mjolner', 'Odin': 'Gungnir', 'Freja': 'Falkedragt'},
                           'Transportation': {'Odin': 'Sleipner', 'Thor': 'Goats'}}
        tokens = _tokenize('{"other":{}, '
                           '"Weapons": {"Thor": "Mjolner", "Odin": "Gungnir", "Freja": "Falkedragt"}, '
                           '"Transportation": {"Odin": "Sleipner", "Thor": "Goats"}}')
        parsed_package = _dictionary.parse(tokens)
        self.assertEqual(parsed_package, expected_result)
