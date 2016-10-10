from eventparser import event, tokenize, channel, package_name, event_name, event_body, sequence, dictionary
from apamaevent import ApamaEvent
import unittest


class TestApamaEvents(unittest.TestCase):
    def test_simple_event(self):
        expected_event = ApamaEvent(event_name='a')
        tokens = tokenize('a()')
        parsed_event = event.parse(tokens)
        self.assertEqual(parsed_event, expected_event)

    def test_package_one_level(self):
        expected_event = ApamaEvent(package_name='heimdall', event_name='ragnarok')
        tokens = tokenize('heimdall.ragnarok()')
        parsed_event = event.parse(tokens)
        self.assertEqual(parsed_event, expected_event)

    def test_package_two_levels(self):
        expected_event = ApamaEvent(package_name='heimdall.horn', event_name='ragnarok')
        tokens = tokenize('heimdall.horn.ragnarok()')
        parsed_event = event.parse(tokens)
        self.assertEqual(parsed_event, expected_event)

    def test_package_many_levels(self):
        expected_event = ApamaEvent(package_name='heimdall.guard.rainbow.bridge.blow.horn', event_name='ragnarok')
        tokens = tokenize('heimdall.guard.rainbow.bridge.blow.horn.ragnarok()')
        parsed_event = event.parse(tokens)
        self.assertEqual(parsed_event, expected_event)

    def test_simple_fields(self):
        expected_event = ApamaEvent(package_name='heimdall.horn',
                                    event_name='ragnarok',
                                    fields=['"valhalla"', 1, 3.14, 1.0e6, False, True])
        tokens = tokenize('heimdall.horn.ragnarok("valhalla", 1, 3.14, 1.0e6, false, true)')
        parsed_event = event.parse(tokens)
        self.assertEqual(parsed_event, expected_event)

    def test_channel(self):
        expected_event = ApamaEvent(channel='channel',
                                    package_name='heimdall.horn',
                                    event_name='ragnarok',
                                    fields=['"valhalla"', 1, 3.14, 1.0e6, False, True])
        tokens = tokenize('"channel",heimdall.horn.ragnarok("valhalla", 1, 3.14, 1.0e6, false, true)')
        parsed_event = event.parse(tokens)
        self.assertEqual(parsed_event, expected_event)

    def test_nested_event(self):
        expected_event = ApamaEvent(channel='channel',
                                    package_name='heimdall.horn',
                                    event_name='ragnarok',
                                    fields=[
                                        ApamaEvent(package_name='rainbow.bridge',
                                                   event_name='breached',
                                                   fields=[True])])
        tokens = tokenize('"channel",heimdall.horn.ragnarok(rainbow.bridge.breached(true))')
        parsed_event = event.parse(tokens)
        self.assertEqual(parsed_event, expected_event)

    def test_readme_example(self):
        expected_event = ApamaEvent(package_name='com.apama',
                                    event_name='Event',
                                    fields=['"Field"', 1.234, 7, False, ['"a"', '"b"', '"c"'], {'"key"': '"value"'}])
        tokens = tokenize('com.apama.Event("Field", 1.234, 7, false, ["a","b","c"], {"key": "value"})')
        parsed_event = event.parse(tokens)
        self.assertEqual(parsed_event, expected_event)


class TestApamaEventParts(unittest.TestCase):
    def test_channel(self):
        expected_result = 'channel'
        tokens = tokenize('"channel",')
        parsed_channel = channel.parse(tokens)
        self.assertEqual(parsed_channel, expected_result)

    def test_package_name(self):
        expected_result = 'heimdall.guard.rainbow.bridge.blow.horn'
        tokens = tokenize('heimdall.guard.rainbow.bridge.blow.horn.')
        parsed_package = package_name.parse(tokens)
        self.assertEqual(parsed_package, expected_result)

    def test_event_name(self):
        expected_result = 'ragnarok'
        tokens = tokenize('ragnarok')
        parsed_package = event_name.parse(tokens)
        self.assertEqual(parsed_package, expected_result)

    def test_event_body_simple_types(self):
        expected_result = ['"valhalla"', 1, 3.14, 1.0e6, True, False]
        tokens = tokenize('("valhalla", 1, 3.14, 1.0e6, true, false)')
        parsed_package = event_body.parse(tokens)
        self.assertEqual(parsed_package, expected_result)

    def test_event_body_all_types(self):
        expected_result = ['"valhalla"', 1, 3.14, 1.0e6, True, False, [1, 2, 3, 4],
                           {'"Thor"': '"Mjolner"', '"Odin"': '"Gungnir"', '"Freja"': '"Falkedragt"'}]
        tokens = tokenize('("valhalla", 1, 3.14, 1.0e6, true, false,[1,2,3,4],'
                          '{"Thor": "Mjolner", "Odin": "Gungnir", "Freja": "Falkedragt"})')
        parsed_package = event_body.parse(tokens)
        self.assertEqual(parsed_package, expected_result)

    def test_sequence_string(self):
        expected_result = ['"a"', '"b"', '"c"']
        tokens = tokenize('["a","b","c"]')
        parsed_package = sequence.parse(tokens)
        self.assertEqual(parsed_package, expected_result)

    def test_sequence_numbers(self):
        expected_result = [1, 2, 3, 4]
        tokens = tokenize('[1,2,3,4]')
        parsed_package = sequence.parse(tokens)
        self.assertEqual(parsed_package, expected_result)

    def test_one_item_sequence(self):
        expected_result = ['"Thor"']
        tokens = tokenize('["Thor"]')
        parsed_package = sequence.parse(tokens)
        self.assertEqual(parsed_package, expected_result)

    def test_empty_sequence(self):
        expected_result = []
        tokens = tokenize('[]')
        parsed_package = sequence.parse(tokens)
        self.assertEqual(parsed_package, expected_result)

    def test_sequence_in_sequence(self):
        expected_result = [[1, 2, 3], [4, 5, 6], [7, 8], [9]]
        tokens = tokenize('[[1,2,3],[4,5,6],[7,8],[9]]')
        parsed_package = sequence.parse(tokens)
        self.assertEqual(parsed_package, expected_result)

    def test_empty_sequence_in_sequence(self):
        expected_result = [[]]
        tokens = tokenize('[[]]')
        parsed_package = sequence.parse(tokens)
        self.assertEqual(parsed_package, expected_result)

    def test_sequence_in_sequence_in_sequence(self):
        # This is not a legal event type since sequences need to all be the same type, however it still parses...
        expected_result = [1, 2, 3, ['"a"', '"b"', '"c"'], [['"aa"', '"bb"'], ['"cc"', '"dd"']]]
        tokens = tokenize('[1,2,3,["a","b","c"],[["aa","bb"],["cc","dd"]]]')
        parsed_package = sequence.parse(tokens)
        self.assertEqual(parsed_package, expected_result)

    def test_empty_sequence_in_sequence_in_sequence(self):
        expected_result = [[[]]]
        tokens = tokenize('[[[]]]')
        parsed_package = sequence.parse(tokens)
        self.assertEqual(parsed_package, expected_result)

    def test_empty_dictionary(self):
        expected_result = {}
        tokens = tokenize('{}')
        parsed_package = dictionary.parse(tokens)
        self.assertEqual(parsed_package, expected_result)

    def test_dictionary(self):
        expected_result = {'"Thor"': '"Mjolner"', '"Odin"': '"Gungnir"', '"Freja"': '"Falkedragt"'}
        tokens = tokenize('{"Thor": "Mjolner", "Odin": "Gungnir", "Freja": "Falkedragt"}')
        parsed_package = dictionary.parse(tokens)
        self.assertEqual(parsed_package, expected_result)

    def test_dictionary_in_dictionary(self):
        expected_result = {'"other"': {},
                           '"Weapons"': {'"Thor"': '"Mjolner"', '"Odin"': '"Gungnir"', '"Freja"': '"Falkedragt"'},
                           '"Transportation"': {'"Odin"': '"Sleipner"', '"Thor"': '"Goats"'}}
        tokens = tokenize('{"other":{}, '
                          '"Weapons": {"Thor": "Mjolner", "Odin": "Gungnir", "Freja": "Falkedragt"}, '
                          '"Transportation": {"Odin": "Sleipner", "Thor": "Goats"}}')
        parsed_package = dictionary.parse(tokens)
        self.assertEqual(parsed_package, expected_result)
