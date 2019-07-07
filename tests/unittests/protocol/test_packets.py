import responses
import pytest
from IPoFB.protocol.packets import (
    PacketFactory,
    StatusCodes,
    Packet,
    InitPacket,
    DataPacket
)


@pytest.fixture
def packet_factory():
    return PacketFactory()


class TestPacketFactory:
    def test_decode_init(self, packet_factory):
        data = f'{StatusCodes.INIT:02} 200'.encode('UTF-8')
        assert InitPacket(200) == packet_factory.decode_packet(data)

    def test_encode_init(self, packet_factory):
        data = f'{StatusCodes.INIT:02} 200'.encode('UTF-8')
        assert packet_factory.encode_packet(InitPacket(200)) == data

    def test_decode_data(self, packet_factory):
        test_data = 'ABCD'
        data = f'{StatusCodes.DATA:02} {test_data}'.encode('UTF-8')
        assert DataPacket(b'ABCD') == packet_factory.decode_packet(data)

    def test_encode_data(self, packet_factory):
        test_data = b'ABCD'
        data = f'{StatusCodes.DATA:02} {test_data}'.encode('UTF-8')
        assert packet_factory.encode_packet(DataPacket(b'ABCD')) == data

    def test_decode_ack(self, packet_factory):
        data = f'{StatusCodes.ACK:02}'.encode('UTF-8')
        assert Packet(StatusCodes.ACK) == packet_factory.decode_packet(data)

    def test_encode_ack(self, packet_factory):
        data = f'{StatusCodes.ACK:02}'.encode('UTF-8')
        assert packet_factory.encode_packet(Packet(StatusCodes.ACK)) == data
