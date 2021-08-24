class RequiredParam(Exception):
    def __init__(self, message, status):
        self.message = message
        self.status = status


class UnsupportedFileType(Exception):
    def __init__(self, message):
        self.message = message
