from IPoFB.pipeline.pipeline import PipelineBlock


class SimpleBinaryBuffer(PipelineBlock):
    def __init__(self):
        super().__init__()
        self._buffer = b''

    def recv(self):
        return self._buffer

    def send(self, data):
        self._buffer += data


class FileBinaryBuffer(PipelineBlock):
    def __init__(self, filename='buffer', *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.filename = filename
        self._buffer = b''

    def recv(self):
        with open(self.filename, 'rb') as f:
            return f.read()

    def send(self, data):
        with open(self.filename, 'wb') as f:
            f.write(data)
