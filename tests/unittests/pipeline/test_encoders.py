import base64
import pytest
from os.path import join
from IPoFB.pipeline.encoders import Base64Encoder
from IPoFB.pipeline.buffers import SimpleBinaryBuffer, FileBinaryBuffer


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
        encoder = Base64Encoder(next_block=pipeline_buffer)
        assert encoder.recv() == test_data


class TestFileBuffer:
    def test_send(self, tmp_path, pipeline_buffer):
        test_data = b'This is a test string'
        filename = join(tmp_path, 'buffer')
        buff = FileBinaryBuffer(filename=filename)
        buff.send(test_data)

        with open(filename, 'rb') as f:
            assert f.read() == test_data

    def test_recv(self, tmp_path, pipeline_buffer):
        test_data = b'This is a test string'
        filename = join(tmp_path, 'buffer')
        buff = FileBinaryBuffer(filename=filename)

        with open(filename, 'wb') as f:
            f.write(test_data)

        assert buff.recv() == test_data
