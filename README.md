# Apama event parser

A parser for Apama epl events. 
[Apama](http://www.softwareag.com/corporate/products/apama_webmethods/analytics/overview/default.asp) 
is a complex event processor that uses a domain specific language for working with the event engine.
Testing is done using some apama specific extensions to [pysys](https://sourceforge.net/projects/pysys/).

This project provides a parser for apama events, with the intention to be used with the testing framework.

## How to use
See the tests for examples.

1. Get a list of tokens using the tokeneizer method in eventparser.py
2. Pass the list of tokens to event.parse() in eventparser.py
3. event.parse() returns an event object - defined in apamaevent.py


```
from eventparser import tokenize, event
tokens = tokenize('com.apama.Event("Field", 1.234, 7, false, ["a","b","c"], {"key": "value"})')
e = event.parse(tokens)
```

## Dependencies
See requirements.py
