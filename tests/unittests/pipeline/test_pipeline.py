import pytest
from IPoFB.pipeline.pipeline import Pipeline
from IPoFB.pipeline.buffers import (SimpleBinaryBuffer,
                                    FileBinaryBuffer,
                                    Passthrough)
from IPoFB.pipeline.encoders import Base64Encoder


@pytest.fixture
def pipeline_buffer():
    test_data = b''
    buff = SimpleBinaryBuffer()
    buff._buffer = test_data
    return buff


@pytest.fixture
def pipeline_passthrough():
    return Passthrough


@pytest.fixture
def pipeline():
    return Pipeline()


class TestPipeline:
    def test_append(self, pipeline, pipeline_buffer):
        pipeline.append_block(pipeline_buffer)
        assert pipeline.blocks[-1] == pipeline_buffer
        assert not pipeline.blocks[-1].next_block
        assert not pipeline.blocks[-1].previous_block

    def test_prepend(self, pipeline, pipeline_buffer):
        pipeline.prepend_block(pipeline_buffer)
        assert pipeline.blocks[-1] == pipeline_buffer
        assert not pipeline.blocks[-1].next_block
        assert not pipeline.blocks[-1].previous_block

    def test_append_multi(self, pipeline):
        for i in range(10):
            pipeline.append_block(Passthrough())

        assert len(pipeline.blocks) == 10
        assert not pipeline.blocks[0].previous_block
        assert not pipeline.blocks[-1].next_block

    def test_prepend_multi(self, pipeline):
        for i in range(10):
            pipeline.prepend_block(Passthrough())

        assert len(pipeline.blocks) == 10
        assert not pipeline.blocks[0].previous_block
        assert not pipeline.blocks[-1].next_block

    def test_recv(self, pipeline, pipeline_buffer):
        for i in range(10):
            pipeline.append_block(Passthrough())
        pipeline.prepend_block(pipeline_buffer)
        pipeline_buffer._buffer = b'Test data'
        assert pipeline.recv() == b'Test data'

    def test_send(self, pipeline, pipeline_buffer):
        for i in range(10):
            pipeline.append_block(Passthrough())
        pipeline.append_block(pipeline_buffer)
        pipeline.send(b'Test data')
        assert pipeline_buffer._buffer == b'Test data'
