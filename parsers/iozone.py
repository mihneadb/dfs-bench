import re


class IOZoneOutputParser(object):
    @staticmethod
    def get_node_outputs(text):
        """
        Gets in all the output of the MPI exec,
        returns a list of texts, one per node.
        """
        pattern = re.compile(r'<<< OUTPUT (?P<id>\d+) >>>')

        lines = text.split('\n')
        outputs = []
        current_output = None

        for line in lines:
            line = line.strip()
            result = pattern.match(line)
            if result:
                if current_output is not None:
                    outputs.append(current_output)
                current_output = []
                continue
            current_output.append(line)
        # add the last one
        outputs.append(current_output)

        return ['\n'.join(o) for o in outputs]

    @staticmethod
    def keep_excel_data(text):
        """
        Throw away everything until "Excel output is below:".
        """
        lines = text.split('\n')
        pattern = re.compile('Excel output is below:')

        first_idx = None
        for i, line in enumerate(lines):
            if pattern.match(line):
                first_idx = i + 1
                break

        return '\n'.join(lines[first_idx:])

    @staticmethod
    def remove_blank_lines(text):
        lines = text.split('\n')
        return '\n'.join([line.strip() for line in lines if line.strip()])

    @staticmethod
    def remove_quotes(text):
        return text.replace('"', '')

    @staticmethod
    def make_dict_report(text):
        """
        "Writer report"
        "128"
        "1024"   197953
        "Re-writer report"
        "128"
        "1024"   133663
        =>
        {'writer': 197953, 're-writer': 133663}
        """
        lines = text.split('\n')
        r = {}

        count = len(lines)
        i = 0
        while i < count:
            line = lines[i]
            if 'report' in line:
                i += 2
                data_line = lines[i]
                key = line.split()[0].lower()
                value = int(data_line.split()[1])
                r[key] = value
            i += 1

        return r

    @staticmethod
    def count_totals(reports):
        if not reports:
            return {}
        totals = {}
        for key in reports[0].keys():
            s = 0
            for report in reports:
                s += report[key]
            totals[key] = s
        return totals

    @staticmethod
    def parse(text):
        outputs = IOZoneOutputParser.get_node_outputs(text)
        excels = [IOZoneOutputParser.keep_excel_data(output) for output in outputs]
        excels = [IOZoneOutputParser.remove_blank_lines(excel) for excel in excels]
        excels = [IOZoneOutputParser.remove_quotes(excel) for excel in excels]
        reports = [IOZoneOutputParser.make_dict_report(excel) for excel in excels]
        totals = IOZoneOutputParser.count_totals(reports)
        return {
            'individual': reports,
            'total': totals
        }

