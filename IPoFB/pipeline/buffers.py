from IPoFB.pipeline.pipeline import PipelineBlock


class SimpleBinaryBuffer(PipelineBlock):
    def __init__(self):
        super().__init__()
        self._buffer = b''

    def recv(self):
        return self._buffer

    def send(self, data):
        self._buffer += data
