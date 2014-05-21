
class HTTPError(Exception):
    """Http Error Exception"""
    def __init__(self, *args, **kwargs):
        self.response = kwargs.pop('response', None)
        super(HTTPError, self).__init__(*args, **kwargs)
