import responses
import pytest
from IPoFB.protocol.packets import (
    FBProtoFSM
)


@pytest.fixture
def fb_fsm():
    return FBProtoFSM()


@pytest.fixture
def fake_username(username='test'):
    responses.add(responses.GET,
                  'https://facebook.com/',
                  body=f'_2s25 _606w" href="https:'
                  '//www.facebook.com/{username}"',
                  status=200)
    return username

def fake_about(about, username='test'):
    responses.add(responses.GET,
                  'https://facebook.com/',
                  body=f'_5cds _2lcw _5cdt">{about}</div',
                  status=200)

class TestFBProtoFSM:
    @responses.activate
    def test_init_data_send(self, fb_fsm, fake_username):
        pass

    @responses.activate
    def test_init_data_recv(self, fb_fsm):
        pass

    @responses.activate
    def test_recv_chunk(self, fb_fsm):
        pass

    @responses.activate
    def test_send_chunk(self, fb_fsm):
        pass
