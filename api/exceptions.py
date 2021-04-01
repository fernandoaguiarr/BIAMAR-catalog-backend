class RequiredParam(Exception):
    def __init__(self, message):
        self.message = message


class UnsupportedFileType(Exception):
    def __init__(self, message):
        self.message = message
