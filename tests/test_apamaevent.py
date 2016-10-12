from unittest import TestCase
from eventparser import parse

class TestApamaEvent(TestCase):

    def test_unparse_event(self):
        event = 'com.apama.Event("Field", 1.234, 7, false, ["a","b","c"], ' \
                '{"key":"value","key1":"value1","key2":"value2"})'
        parsed_event = parse(event)
        self.assertEqual(parsed_event.unparse(), event)

    def test_unparse_event_with_channel(self):
        event = '"channel",heimdall.horn.ragnarok("valhalla", 1, 3.14, 1000000, false, true)'
        parsed_event = parse(event)
        self.assertEqual(parsed_event.unparse(), event)
