import time
import logging
from dataclasses import dataclass
from enum import IntEnum


# The less status codes the better
class StatusCodes(IntEnum):
    ACK = 0,
    INIT = 1,
    DATA = 2


class EmptyDataError(Exception):
    pass



class BusyChannelError(Exception):
    pass


class InvalidPacketDataError(Exception):
    pass


@dataclass
class Packet:
    status_code: StatusCodes

    @property
    def padded_status_code(self) -> str:
        # If less than 2 digits facebook won't accept it
        return f"{self.status_code:02}"


@dataclass
class InitPacket(Packet):
    number_of_chunks: int

    def __init__(self, number_of_chunks):
        super().__init__(StatusCodes.INIT)
        self.number_of_chunks = number_of_chunks


@dataclass
class DataPacket(Packet):
    data: bytes

    def __init__(self, data):
        super().__init__(StatusCodes.DATA)
        self.data = data


# Thanks SO
# https://stackoverflow.com/questions/312443/how-do-you-split-a-list-into-evenly-sized-chunks
def to_chunks(l, n):
    """Yield successive n-sized chunks from l."""
    for i in range(0, len(l), n):
        yield l[i:i + n]


def get_status_code(data) -> StatusCodes:
    if data:
        return StatusCodes(int(data.split()[0]))
    else:
        raise EmptyDataError("Packet is empty, no status code available")


def get_data(data) -> StatusCodes:
    if data:
        return (data.split()[1])


class PacketFactory:
    def decode_packet(self, data: bytes) -> Packet:
        data_str = data.decode('UTF-8')
        data_list = data_str.split()
        status_code = int(data_list[0])
        if status_code == StatusCodes.INIT:
            return InitPacket(int(data_list[1]))
        elif status_code == StatusCodes.ACK:
            return Packet(StatusCodes.ACK)
        elif status_code == StatusCodes.DATA:
            return DataPacket(data.split()[1])
        else:
            raise InvalidPacketDataError(f"Invalid status code: {status_code}")

    def encode_packet(self, packet: Packet) -> bytes:
        status_code = packet.status_code
        if status_code == StatusCodes.INIT:
            return f'{status_code:02} {packet.number_of_chunks}'\
                    .encode('UTF-8')
        elif status_code == StatusCodes.ACK:
            return f'{status_code:02}'.encode('UTF-8')
        elif status_code == StatusCodes.DATA:
            return f'{status_code:02} {packet.data}'.encode('UTF-8')
        else:
            raise InvalidPacketDataError(f"Invalid status code: {status_code}")
