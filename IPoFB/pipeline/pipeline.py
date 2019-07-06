from abc import ABC


class PipelineNotTerminatedError(Exception):
    pass


class Pipeline:
    """
    This class manages the data streams. basically it chains differents
    Pipeline blocks into a single pipeline so that data is processed
    before being sent or received
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
        return self.blocks[0].recv()

    def send(self, data):
        return self.blocks[-1].send(data)


class PipelineBlock(ABC):
    """
    This class is a single processing unit that will modify the data
    The pipeline terminator block MUST NOT call these recv and sed
    """
    def __init__(self,
                 previous_block=None,
                 next_block=None):
        self.previous_block = previous_block
        self.next_block = next_block

    def recv(self):
        if self.previous_block:
            data = self.previous_block.recv()
            # Process data here
            return data
        else:
            raise PipelineNotTerminatedError("Non terminator block used"
                                             "for terminating pipeline")

    def send(self, data):
        # Process data here
        if self.next_block:
            self.next_block.send(data)
        else:
            raise PipelineNotTerminatedError("Non terminator block used"
                                             "for terminating pipeline")
