import base64
import pytest
from IPoFB.pipeline.encoders import Base64Encoder
from IPoFB.pipeline.buffers import SimpleBinaryBuffer


@pytest.fixture
def pipeline_buffer():
    return SimpleBinaryBuffer()


class TestBase64Encoder:
    def test_send(self, pipeline_buffer):
        test_data = b'This is a test string'
        encoder = Base64Encoder(next_block=pipeline_buffer)
        encoder.send(test_data)
        assert pipeline_buffer._buffer == base64.b64encode(test_data)

    def test_recv(self, pipeline_buffer):
        test_data = b'This is a test string'
        pipeline_buffer._buffer = base64.b64encode(test_data)
        encoder = Base64Encoder(previous_block=pipeline_buffer)
        assert encoder.recv() == test_data
