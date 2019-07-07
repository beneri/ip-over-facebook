from IPoFB.pipeline.pipeline import PipelineBlock


class Passthrough(PipelineBlock):
    """
    Simple passthrough block, only relays data through the pipeline
    """
    def __init__(self):
        super().__init__()

    def recv(self):
        super().recv()

    def send(self, data):
        super().send(data)


class SimpleBinaryBuffer(PipelineBlock):
    def __init__(self):
        super().__init__()
        self._buffer = b''

    def recv(self):
        return self._buffer

    def send(self, data):
        self._buffer += data


# Should create a PipelineBlockTerminator class for clarity's sake
# This class has a strange working logic, must be made clearer
class FileBinaryBuffer(PipelineBlock):
    def __init__(self, filename='buffer', *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.filename = filename

    def recv(self):
        with open(self.filename, 'rb') as f:
            return f.read()

    def send(self, data):
        with open(self.filename, 'wb') as f:
            f.write(data)
