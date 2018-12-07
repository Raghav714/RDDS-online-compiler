"""Scanner module

With any attached file, the Scanner class will scan the file token-by-token
until an end-of-file is encountered.

Author: RDDS TEAM

Classes:
    Scanner: An implementation of a scanner for the source language.
"""

from os.path import isfile

from lib.data_type import Token


class Scanner:
    """1"""
    # Define all language keywords
    keywords = [
        'str', 'int', 'bool', 'float', 'global', 'is', 'in', 'out',
        'if', 'then', 'else', 'for', 'and', 'or', 'not', 'program',
        'function', 'body', 'return', 'finish', 'true', 'false','the','define',
    ]

    # Define all language symbols
    symbols = [
        ':', ';', ',', '+', '-', '*', '/', '(', ')', '<', '<=', '>', '>=',
        '!', '!=', '=', '==', '[', ']', '&', '|',
    ]

    def __init__(self):
        super().__init__()

        # Holds the file path of the attached source file
        self._src_path = ''

        # Holds all source file data (code) to be scanned
        self._src = ''

        # Holds the location of the next character to scan in the source file
        self._line_pos = 0
        self._char_pos = 0

        return

    def attach_source(self, src_path):
        """2"""
        # Make sure the inputted file is a actual file
        if not isfile(src_path):
            print('Error: "%s"' % src_path)
            print('    Inputted path is not a file')
            return False

        # Try to read all data from the file and split by line
        try:
            with open(src_path) as f:
                keepends = True
                self._src = f.read().splitlines(keepends)
        except IOError:
            print('Error: "%s"' % src_path)
            print('    Could not read inputted file')
            return False

        # The file was attached and read successfully, store the path
        self._src_path = src_path

        return True

    def next_token(self):
        """3"""
        # Get the first character, narrow down the data type possibilities
        char = self._next_word()

        if char is None:
            return Token('eof', None, self._line_pos)

        # Use the first character to choose the token type to expect
        if char == '"':
            value, token_type = self._expect_string()
        elif char.isdigit():
            value, token_type = self._expect_number(char)
        elif char.isalpha():
            value, token_type = self._expect_identifier(char)
        elif char in self.symbols:
            value, token_type = self._expect_symbol(char)
        else:
            # We've run across a character that shouldn't be here
            msg = 'Invalid character \'%s\' encountered' % char
            self._scan_warning(msg, hl=self._char_pos-1)

            # Run this function again until we find something good
            return self.next_token()

        if token_type == 'comment':
            # If we find a comment, get a token on the next line
            self._next_line()
            return self.next_token()

        # Build the new token object
        new_token = Token(token_type, value, self._line_pos+1)

        return new_token

    def _get_line(self, line_number):
        """4"""
        if 0 < line_number <= len(self._src):
            return self._src[line_number-1].strip()

    def _scan_warning(self, msg, hl=-1):
        """5"""
        line = self._src[self._line_pos][0:-1]

        print('Warning: "', self._src_path, '", ', sep='', end='')
        print('line ', self._line_pos+1, sep='')
        print('    ', msg, '\n    ', line.strip(), sep='')

        if hl != -1:
            left_spaces = line.find(line.strip()[0])
            print('    %s^' % (' '*(abs(hl)-left_spaces)))

        return

    def _next_word(self):
        """6"""
        char = ''

        while True:
            char = self._src[self._line_pos][self._char_pos]

            # React according to spaces and newlines
            if char == '\n':
                if not self._next_line():
                    return None
            elif char in ' \t':
                self._char_pos += 1
            else:
                break

        # Increment to the next character
        self._char_pos += 1
        return char

    def _next_line(self):
        """7"""
        self._line_pos += 1
        self._char_pos = 0

        # Check to make sure this isn't the end of file
        if self._line_pos == len(self._src):
            return False

        return True

    def _next_char(self, peek=False):
        """8"""
        # Get the next pointed character
        char = self._src[self._line_pos][self._char_pos]

        # Return None if we hit a line ending
        if char == '\n':
            return None

        # Increment to the next character
        if not peek:
            self._char_pos += 1

        return char

    def _expect_string(self):
        """9"""
        hanging_quote = False

        # We know this is a string. Find the next quotation and return it
        string_end = self._src[self._line_pos].find('"', self._char_pos)

        # If we have a hanging quotation, assume quote ends at end of line
        if string_end == -1:
            hanging_quote = True
            string_end = len(self._src[self._line_pos]) - 1
            self._scan_warning('No closing quotation in string', hl=string_end)

        value = self._src[self._line_pos][self._char_pos:string_end]

        # Check for illegal characters, send a warning if encountered
        for i, char in enumerate(value):
            if not char.isalnum() and char not in ' _,;:.\'':
                value = value.replace(char, ' ', 1)
                msg = 'Invalid character \'%s\' in string' % char
                self._scan_warning(msg, hl=self._char_pos+i)

        self._char_pos += len(value)
        if not hanging_quote:
            self._char_pos += 1

        return value, 'str'

    def _expect_number(self, char):
        """10"""
        value = '' + char
        token_type = 'int'

        is_float = False

        while True:
            char = self._next_char(peek=True)

            if char is None:
                break
            elif char == '.' and not is_float:
                # We found a decimal point. Move to float mode
                is_float = True
                token_type = 'float'
            elif not char.isdigit() and char != '_':
                break

            value += char
            self._char_pos += 1

        # Remove all underscores in the int/float. These serve no purpose
        value = value.replace('_', '')

        # If nothing was given after the decimal point assume 0
        if is_float and value.split('.')[-1] == '':
            value += '0'

        return value, token_type

    def _expect_identifier(self, char):
        """11"""
        value = '' + char
        token_type = 'identifier'

        while True:
            char = self._next_char(peek=True)

            if char is None:
                break
            elif not char.isalnum() and char != '_':
                break

            value += char
            self._char_pos += 1

        if value in self.keywords:
            token_type = 'keyword'

        return value, token_type

    def _expect_symbol(self, char):
        """12"""
        value = '' + char

        while True:
            char = self._next_char(peek=True)

            if char is None:
                break
            elif value + str(char) == '//':
                return None, 'comment'
            elif value + str(char) not in self.symbols:
                break

            value += char
            self._char_pos += 1

        return value, 'symbol'
