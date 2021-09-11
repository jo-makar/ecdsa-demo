from point import Curve, Point

import subprocess


class Privkey:
    def __init__(self, path: str):
        cmd = ['openssl', 'ec', '-in', path, '-text', '-noout', '-param_enc', 'explicit']
        output = subprocess.check_output(cmd, stderr=subprocess.STDOUT, encoding='utf-8')

        output_map = {}
        lines = output.splitlines()
        lineno = 0
        while lineno < len(lines):
            if lines[lineno][0] != ' ' and lines[lineno].rstrip()[-1] == ':':
                key = lines[lineno].rstrip()[:-1]
                val = ''

                lineno += 1
                while lineno < len(lines) and lines[lineno][0] == ' ':
                    val += lines[lineno].strip()
                    lineno += 1

                output_map[key] = val

            else:
                lineno += 1

        str_to_int = lambda s: int(s.replace(':', ''), 16)

        self.a = str_to_int(output_map['A'])
        self.b = str_to_int(output_map['B'])
        self.p = str_to_int(output_map['Prime'])
        self.n = str_to_int(output_map['Order'])

        self.d = str_to_int(output_map['priv'])

        curve = Curve(self.a, self.b, self.p)
        str_to_point = lambda s: Point(s.replace(':', ''), curve)

        self.g = str_to_point(output_map['Generator (uncompressed)'])
        self.pubkey = str_to_point(output_map['pub'])

        assert self.pubkey == self.d * self.g


class Pubkey:
    def __init__(self, path: str):
        cmd = ['openssl', 'ec', '-pubin', '-in', path, '-text', '-noout', '-param_enc', 'explicit']
        output = subprocess.check_output(cmd, stderr=subprocess.STDOUT, encoding='utf-8')

        output_map = {}
        lines = output.splitlines()
        lineno = 0
        while lineno < len(lines):
            if lines[lineno][0] != ' ' and lines[lineno].rstrip()[-1] == ':':
                key = lines[lineno].rstrip()[:-1]
                val = ''

                lineno += 1
                while lineno < len(lines) and lines[lineno][0] == ' ':
                    val += lines[lineno].strip()
                    lineno += 1

                output_map[key] = val

            else:
                lineno += 1

        str_to_int = lambda s: int(s.replace(':', ''), 16)

        self.a = str_to_int(output_map['A'])
        self.b = str_to_int(output_map['B'])
        self.p = str_to_int(output_map['Prime'])
        self.n = str_to_int(output_map['Order'])

        curve = Curve(self.a, self.b, self.p)
        str_to_point = lambda s: Point(s.replace(':', ''), curve)

        self.g = str_to_point(output_map['Generator (uncompressed)'])
        self.pubkey = str_to_point(output_map['pub'])
