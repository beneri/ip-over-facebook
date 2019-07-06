import base64
from IPoFB.pipeline.pipeline import PipelineBlock


class Base64Encoder(PipelineBlock):
    def recv(self):
        data = super().recv()
        return base64.b64decode(data)

    def send(self, data):
        encoded_data = base64.b64encode(data)
        super().send(encoded_data)
