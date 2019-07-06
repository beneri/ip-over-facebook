from ABC import ABC, abstractmethod


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

    def recv(self):
        data = None
        # This sends the data from one block to another in series
        for block in self.blocks[-1]:
            data = block.recv()
            block.send(data)

        return self.blocks[-1].recv()

    def send(self, data):
        new_data = data
        for block in self.blocks[-1]:
            block.send(new_data)
            new_data = block.recv()
        self.blocks[-1].send(new_data)


class PipelineBlock(ABC):
    """
    This class is a single processing unit that will modify the data
    """
    @abstractmethod
    def recv(self):
        pass

    @abstractmethod
    def send(self, data):
        pass
