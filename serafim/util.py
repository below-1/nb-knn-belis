def compose(*decs):
    def _decorator(f):
        for dec in reversed(decs):
            dec(f)
    return _decorator
