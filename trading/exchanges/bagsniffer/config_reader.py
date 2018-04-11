class ConfigReader(object):
    fields = []

    # Initialize: file = config file name (e.g. "exchanges.txt"), field_count=number of fields to
    # look for, e.g. 3. Can be less, but not more.
    def __init__(self, file, field_count):
        self.analyze(file, field_count)
        return

    # Dissect a single line
    def dissect_line(self, line, field_count):
        found = []
        line = line.strip()
        # bail if it's an empty line or a comment line
        if len(line) == 0 or line[0] == "#":
            return found
        word = ""
        in_quotes = False
        quote_character = ""
        for character in line:
            if character == '"' or character == "'":
                if in_quotes and quote_character == character:
                    in_quotes = False
                    found.append(word)
                    word = ""
                elif in_quotes and quote_character != character:
                    word = word + character
                else:
                    in_quotes = True
                    quote_character = character
            elif character == ' ' and not in_quotes:
                if len(word) > 0:
                    found.append(word)
                    word = ""
            else:
                word = word + character
            if len(found) == field_count:
                break
        if len(word) > 0:
            found.append(word)
        return found

    # Analyze the config file
    def analyze(self, file, field_count):
        self.fields = []
        try:
            with open('config/' + file, mode='r') as configuration_file:
                lines = configuration_file.readlines()
            for line in lines:
                found = self.dissect_line(line, field_count)
                if found:
                    self.fields.append(found)
        except:
            pass
        return

