import re
import sys
from pprint import pprint


class MDTestOutputParser(object):
    @staticmethod
    def get_relevant_chunk(text):
        # find first line
        lines = text.splitlines()
        start = 0
        for i, line in enumerate(lines):
            if line.startswith('SUMMARY'):
                # skip the summary line
                start = i + 1
                break
        end = 0
        for j, line in enumerate(lines[start:]):
            if not line.strip():
                end = start + j
                break
        return '\n'.join(lines[start:end])

    @staticmethod
    def make_dict(text):
        lines = text.splitlines()

        # first line has inner dict keys
        # max, min, mean, std dev
        inner_keys = re.split('\s\s+', lines[0].strip())[1:]

        # next line is bogus, just ------
        lines = lines[2:]

        # now every line looks like
        # key    :     v1    v2     .... vn
        data = {}
        for line in lines:
            line = line.strip()
            parts = line.split(':')
            key = parts[0].strip()
            values = parts[1].strip()
            values = re.split('\s\s+', values)
            data[key] = {}
            for i, v in enumerate(values):
                data[key][inner_keys[i]] = float(v)
        return data

    @staticmethod
    def parse(text):
        chunk = MDTestOutputParser.get_relevant_chunk(text)
        parsed = MDTestOutputParser.make_dict(chunk)
        return parsed

if __name__ == '__main__':
    with open(sys.argv[1]) as f:
        data = f.read()
    pprint(MDTestOutputParser.parse(data))

