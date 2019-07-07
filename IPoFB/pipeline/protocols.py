from IPoFB.pipeline.pipeline import PipelineBlock
from IPoFB.protocol.packets import FBProtoFSM


class FBProto(PipelineBlock):
    """
    FBProto protocol
    """
    def __init__(self):
        super().__init__()
        self._protocol = FBProtoFSM()

    def recv(self):
        super().recv()

    def send(self, data):
        self._protocol.init_data_send(data)
        super().send(data)
