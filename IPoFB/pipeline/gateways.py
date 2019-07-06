from IPoFB.pipeline.pipeline import PipelineBlock
from IPoFB.gateways.facebook import Facebook


class FacebookGatewayBlock(PipelineBlock):
    def __init__(self, username, password, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._fb = Facebook()
        self._fb.login(username, password)

    def recv(self):
        return self._fb.recv()

    def send(self, data):
        self._fb.send(data)
