import time
import logging
from math import ceil
from dataclasses import dataclass
from enum import IntEnum
from IPoFB.gateways.facebook import Facebook


class StatusCodes(IntEnum):
    ACK = 0,
    INIT = 1,


class FSMStates(IntEnum):
    IDLE = 0,
    INITIALIZING = 1,
    SENDING = 2,
    RECEIVING = 3,


class EmptyDataError(Exception):
    pass


class InvalidStateError(Exception):
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


def wait_for_status(status: StatusCodes,
                    update_function,
                    callback_function=lambda x: True,
                    update_interval=0.2,
                    timeout=5):
    """
    Doesn't return until the update_function return the specified status.
    Before returning it calls the callback_function
    """
    start_time = time.time()
    current_time = start_time

    while current_time - start_time < timeout:
        logging.debug(f"Waiting for {status}")
        func_status = update_function()
        if func_status == status:
            return True

        time.sleep(update_interval)
        current_time = time.time()

    raise TimeoutError(f"{status} waiting timed out")


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


class FBProtoFSM:
    """
    Finite state machine that manages the communication protocol
    """
    def __init__(self):
        # Must be multiple of 4 to be streamable.
        # Other than that, the bigger the better.
        self.MAXSIZE = 4*259434
        self._number_of_chunks = 0
        self._gateway = Facebook()
        self._chunks = None
        self._state = FSMStates.IDLE

    def _init_data_send(self, data):
        """
        Initializes the data sending
        """
        # Check if channel is free
        if not self._gateway.about:
            logging.debug("Initializing data sending")
            self._state = FSMStates.INITIALIZING

            self._number_of_chunks = ceil(len(data)/self.MAXSIZE)
            logging.debug(f"Trying to send {len(data)} bytes")
            logging.debug("Splitting data into "
                          f"{self._number_of_chunks} chunks of max "
                          f"{self.MAXSIZE} bytes")
            self._chunks = to_chunks(data, self.MAXSIZE)

            # Send INIT
            init_pkt = InitPacket(self._number_of_chunks)
            logging.debug(f"Sending {init_pkt}")
            # If less than 2 digits facebook won't accept it
            self._gateway.about = f"{init_pkt.padded_status_code} "\
                "{self._number_of_chunks}"
            try:
                wait_for_status(StatusCodes.ACK,
                                lambda: get_status_code(self._gateway.about))
            except TimeoutError:
                logging.debug("Init ack timed out")
                self._state = FSMStates.IDLE
            logging.debug('Init acknowledged')
            self._state = FSMStates.SENDING
        else:
            raise Exception("Channel not free")

    def _send_chunk(self, chunk):
        logging.debug(f"Sending {len(chunk)} bytes")
        self._gateway.about = str(chunk)
        wait_for_status(StatusCodes.ACK,
                        lambda: get_status_code(self._gateway.about))
        logging.debug(f"Sent {len(chunk)} bytes")

    def _recv_chunk(self):
        logging.debug(f"Receiving chunk")
        chunk = self._gateway.about
        self._gateway.about = Packet(StatusCodes.ACK)
        logging.debug(f"Received {len(chunk)} bytes")

    def send(self, data):
        if self._state == FSMStates.IDLE:
            self._init_data_send(data)

        if self._state == FSMStates.RECEIVING:
            raise InvalidStateError("Can't send data while receiving")

        if self._state == FSMStates.SENDING:
            for chunk in self._chunks:
                self._send_chunk(chunk)
            logging.info("Data sending done")

    def recv(self):
        if self._state == FSMStates.IDLE:
            self._init_data_recv()

        if self._state == FSMStates.SENDING:
            raise InvalidStateError("Can't send data while receiving")

        if self._state == FSMStates.RECEIVING:
            buff = b''
            for chunk in self._chunks:
                self._send_chunk(chunk)
            logging.info("Data receiving done")

#
#
#
#def send(self, data):
#    logging.debug(f"Acting as a server, trying to send {len(data)} bytes")
#
#        about = self.getAbout()
#
#
#        # If is not null the channel is occupied
#        if not about:
#            encoded_data = base64.b64encode(data)
#
#            number_of_chunks = ceil(len(encoded_data)/self.MAXSIZE)
#            logging.debug("Splitting data into "
#                          f"{number_of_chunks} chunks of max "
#                          f"{self.MAXSIZE} bytes")
#            # We need UTF-8 strings because otherwise facebook will garble the
#            # data
#            chunks = to_chunks(encoded_data.decode('UTF-8'), self.MAXSIZE)
#
#            # Send INIT
#            logging.debug(f"Sending init {StatusCodes.INIT} "
#                          f"{number_of_chunks}")
#            # If less than 2 digits facebook won't accept it
#            self.changeAbout(f"{StatusCodes.INIT.value:02} {number_of_chunks}")
#            wait_for_status(StatusCodes.ACK,
#                            lambda: get_status_code(self.getAbout()))
#            for chunk in chunks:
#                logging.debug(f"Uploading {len(chunk)} bytes")
#
#                self.changeAbout(f"{StatusCodes.DATA:02} {chunk}")
#                wait_for_status(StatusCodes.ACK,
#                                lambda: get_status_code(self.getAbout()))
#
#            logging.info("Sending done")
#            self.changeAbout(f"{StatusCodes.DONE.value:02}")
#            return len(data)
#
#    def recv(self, num_of_bytes=None):
#        logging.debug("Receiving data")
#        recv_data = []
#        number_of_chunks = 0
#
#        # status_code number_of_chunks
#        data = self.getAbout()
#
#
#        try:
#            recv_pkt = self.packet_factory.decode(data)
#        except EmptyDataError:
#            pass
#
#        status_code = get_status_code(data)
#        if status_code:
#            message = data.split()
#
#            # It means that the data connection has not been
#            # initialized yet
#            if number_of_chunks == 0:
#                # we initialize the number of chunks
#                if status_code == StatusCodes.INIT.value:
#                    logging.debug("Receive initialized:"
#                                  f" {message[1]} chunks in total")
#                    self.changeAbout(f"{StatusCodes.ACK.value:02}")
#                    number_of_chunks = int(message[1])
#                    # the data transfer is done
#                elif status_code == StatusCodes.DONE.value:
#                    logging.debug("Done downloading data")
#                    # Cleanup
#                    self.changeAbout("")
#                    return b"".join(recv_data)
#            # Something went wrong
#        elif number_of_chunks < 0:
#            raise Exception("Chunks synchronization error")
#        # we're transferring data
#            elif number_of_chunks > 0:
#                # if we have more than 1 element in message something went
#                # wrong
#                if status_code == StatusCodes.DATA.value:
#                    data = message[1].encode("UTF-8")
#                    logging.debug(f"Downloading {len(data)} bytes")
#                    recv_data.append(base64.b64decode(data))
#
#                    self.changeAbout(f"{StatusCodes.ACK.value:02}")
#                    number_of_chunks -= 1
