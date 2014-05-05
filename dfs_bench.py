from pprint import pprint
from parsers.iozone import IOZoneOutputParser


with open('out.txt') as f:
    text = f.read()

pprint(IOZoneOutputParser.parse(text))

