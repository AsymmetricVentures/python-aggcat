class HTTPError(Exception):
    """Http Error Exception"""
    def __init__(self, *args, **kwargs):
        self.response = kwargs.pop('response', None)
        objectify = kwargs.pop('objectify', None)
        self.err_obj = None
        self.status_code = None
        if self.response is not None:
            self.status_code = self.response.status_code
            if objectify is not None:
                try:
                    self.err_obj = objectify(self.response.content).get_object()
                except:
                    pass
        
        super(HTTPError, self).__init__(*args, **kwargs)
