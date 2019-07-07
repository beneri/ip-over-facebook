import responses
import pytest
from IPoFB.protocol.state_machines import (
    FBProtoFSM,
    BusyChannelError
)
from IPoFB.protocol.packets import (
    Packet,
    StatusCodes
)


@pytest.fixture
def fb_fsm():
    return FBProtoFSM()


def fake_username(username='test'):
    responses.add(responses.GET,
                  'https://facebook.com/',
                  body=f'_2s25 _606w" href="https:'
                  f'//www.facebook.com/{username}"',
                  status=200)


def fake_about(about, username='test'):
    body = ''
    if about:
        body = f'_5cds _2lcw _5cdt">{about}</div',
    else:
        body = f'_5cds _2lcw _5cdt"></div',
    responses.add(responses.GET,
                  f'https://m.facebook.com/{username}/about?section=bio',
                  body=body,
                  status=200)


def fake_set_about(about, username='test'):
    responses.add(responses.POST,
                  f'https://www.facebook.com/profile/async/edit/infotab/save'
                  '/about_me/?dpr=1.5',
                  status=200)


#class TestFBProtoFSM:
#    @responses.activate
#    def test_init_data_send_busy_check(self, fb_fsm):
#        fake_username('test')
#        fake_about('Test')
#        try:
#            fb_fsm._init_data_send('dummy')
#            assert False
#        except BusyChannelError:
#            pass
#
#    @responses.activate
#    def test_init_data_send_not_busy_check(self, fb_fsm):
#        fake_username('test')
#        fake_about(None)
#        try:
#            fb_fsm._init_data_send('dummy')
#        except BusyChannelError:
#            assert False
#        except TimeoutError:
#            pass
#
#    @responses.activate
#    def test_init_data_send_timeout(self, fb_fsm):
#        fake_username('test')
#        fake_about(None)
#        try:
#            fb_fsm._init_data_send('dummy')
#        except TimeoutError:
#            assert True
#
#    def test_init_data_send_no_timeout(self, fb_fsm):
#        fake_username('test')
#        fake_about(None)
#        try:
#            fake_about(fb_fsm._packet_factory
#                       .encode_packet(Packet(StatusCodes.ACK)))
#            fb_fsm._init_data_send('dummy')
#        except TimeoutError:
#            assert False
#
#    @responses.activate
#    def test_init_data_recv(self, fb_fsm):
#        pass
#
#    @responses.activate
#    def test_recv_chunk(self, fb_fsm):
#        pass
#
#    @responses.activate
#    def test_send_chunk(self, fb_fsm):
#        pass
