from abc import ABC


class PipelineNotTerminatedError(Exception):
    pass


class Pipeline:
    """
    This class manages the data streams. basically it chains differents
    Pipeline blocks into a single pipeline so that data is processed
    before being sent or received
    Pipelines are bidirectionals, so when you recv it starts reading data
    from the last block and when you send it start sending data from the
    first block
    :field blocks: Contains the single PipelineBlocks
    EG:
        Receveing pipeline:
            [gateway] -> [decoder] -> [application]
            The application must be the last block
        Sending pipeline:
            [application] -> [encoder] -> [gateway]
            The gateway must be the last block
    """
    def __init__(self):
        self.blocks = []

    def append_block(self, block):
        if len(self.blocks) > 0:
            self.blocks[-1].next_block = block
            block.previous_block = self.blocks[-1]
        self.blocks.append(block)

    def prepend_block(self, block):
        if len(self.blocks) > 0:
            self.blocks[0].previous_block = block
            block.next_block = self.blocks[0]
        self.blocks.insert(0, block)

    def recv(self):
        """
        Read data from pipeline
        The data will be pulled from the last block automatically
        """
        return self.blocks[0].recv()

    def send(self, data=None):
        """
        Write data to pipeline
        The data will be sent to the first block, then it will be forwarded
        to all the successive blocks
        """
        return self.blocks[0].send(data)


class PipelineBlock(ABC):
    """
    This class is a single processing unit that will modify the data
    The pipeline terminator block MUST NOT call these recv and send
    """
    def __init__(self,
                 previous_block=None,
                 next_block=None):
        self.previous_block = previous_block
        self.next_block = next_block

    def recv(self):
        """
        Read data from block
        """
        if self.next_block:
            data = self.next_block.recv()
            # Process data here
            return data
        else:
            raise PipelineNotTerminatedError("Non terminator block used"
                                             "for terminating pipeline")

    def send(self, data=None):
        """
        Processe the sent data
        :param data: Data to be processed
        """
        # Process data here
        if self.next_block:
            self.next_block.send(data)
        else:
            raise PipelineNotTerminatedError("Non terminator block used"
                                             "for terminating pipeline")
