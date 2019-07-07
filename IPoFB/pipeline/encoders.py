import base64
from IPoFB.pipeline.pipeline import PipelineBlock
from IPoFB.protocol.packets import Packet


class Base64Encoder(PipelineBlock):
    def recv(self):
        data = super().recv()
        return base64.b64decode(data)

    def send(self, data):
        encoded_data = base64.b64encode(data)
        super().send(encoded_data)


#class FBProtoPacketEncoder(PipelineBlock):
#    def decode_packet(self, data: bytes) -> Packet:
#        data = self.getAbout()
#        status_code = get_status_code(data)
#        if status_code == StatusCodes.DATA:
#            return DataPacket(status_code,
#                              get_data(data))
#        else:
#            return Packet(status_code)
#
#    def encode_packet(self, packet: Packet) -> bytes:
#        status_code = packet.status_code
#        if status_code == StatusCodes.DATA:
#            # Need to encode string
#            return f"{StatusCodes.DATA.value:02} {packet.data}"
#        else:
#            pass
#
