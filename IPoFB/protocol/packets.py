from dataclasses import dataclass
from enum import IntEnum


class StatusCodes(IntEnum):
    ACK = 0,
    DATA = 1,
    INIT = 2,
    DONE = 3


# Thanks SO
# https://stackoverflow.com/questions/312443/how-do-you-split-a-list-into-evenly-sized-chunks
def to_chunks(l, n):
    """Yield successive n-sized chunks from l."""
    for i in range(0, len(l), n):
        yield l[i:i + n]


class EmptyDataError(Exception):
    pass


def get_status_code(data) -> StatusCodes:
    if data:
        return StatusCodes(int(data.split()[0]))
    else:
        raise EmptyDataError("Packet is empty, no status code available")


def get_data(data) -> StatusCodes:
    if data:
        return (data.split()[1])


@dataclass
class Packet:
    status_code: StatusCodes


@dataclass
class DataPacket:
    status_code: StatusCodes
    data: bytes


class PacketFactory:
    def __init__(self,
                 input_pipeline=None,
                 output_pipeline=None):
        self.input_pipeline = input_pipeline
        self.output_pipeline = output_pipeline

    def decode_packet(self, data: bytes) -> Packet:
        data = self.getAbout()
        status_code = get_status_code(data)
        if status_code == StatusCodes.DATA:
            return DataPacket(status_code,
                              get_data(data))
        else:
            return Packet(status_code)

    def encode_packet(self, packet: Packet) -> bytes:
        status_code = packet.status_code
        if status_code == StatusCodes.DATA:
            # Need to encode string
            return f"{StatusCodes.DATA.value:02} {packet.data}"
        else:
            pass

