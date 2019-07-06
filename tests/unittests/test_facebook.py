import responses
import pytest
import time
from IPoFB.facebook import (
    Facebook,
    wait_for_status,
    StatusCodes,
    get_status_code
)


@pytest.fixture
def fb(cache_file='None'):
    return Facebook(cache_file)


def callback_assert_true():
    assert True


def sleep_and_return_ss(code: StatusCodes,
                        start_time=time.time(),
                        sleep_time: int = 5):

    current_time = time.time()
    if current_time - start_time > sleep_time:
        return code


class TestWaitForStatus():
    def test_function(self):
        try:
            wait_for_status(StatusCodes.ACK,
                            lambda: StatusCodes.ACK)
        except TimeoutError:
            assert False

    def test_callback(self):
        wait_for_status(StatusCodes.ACK,
                        lambda: StatusCodes.ACK,
                        callback_assert_true)

    def test_timeout(self):
        try:
            # Testing Timeout for right code
            start_time = time.time()
            wait_for_status(StatusCodes.ACK,
                            lambda: sleep_and_return_ss(StatusCodes.ACK,
                                                        start_time,
                                                        6))
            assert False
        except TimeoutError:
            assert True

        try:
            # Testing Timeout for wrong code
            start_time = time.time()
            wait_for_status(StatusCodes.ACK,
                            lambda: sleep_and_return_ss(StatusCodes.INIT,
                                                        start_time))
            assert False
        except TimeoutError:
            assert True


class TestStatusCodes:
    def test_zero_padded_init(self):
        assert StatusCodes(get_status_code('01')) == StatusCodes(1)

# class TestFacebookClass:
    #@responses.activate
    #def test_uncached_login(self, tmp_path, fb):
    #    def request_callback(request):
    #        valid_headers = {
    #            'origin': 'https://www.facebook.com',
    #            'accept-encoding': 'gzip',
    #            'accept-language': 'en-US,en;q=1.0',
    #            'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) '
    #            'AppleWebKit/537.36 '
    #            '(KHTML, like Gecko) Chrome/65.0.3325.162 Safari/537.36',
    #            'content-type': 'application/x-www-form-urlencoded',
    #            'accept': '*/*',
    #            'referer': 'https://www.facebook.com/',
    #            'authority': 'www.facebook.com',
    #        }

    #        assert valid_headers == request.headers

    #        r_headers = {"Set-Cookie": "adama_session=" + 1}
    #        r_body = 'Testing login phase 1'

    #        return (200, r_headers, r_body)

    #    responses.add_callback(
    #        responses.GET,
    #        'https://www.facebook.com/',
    #        callback=request_callback,
    #        cookies={'fr': 'fr_cookie',
    #                 'sb': 'sb_cookie'},
    #        status=200)

    #@responses.activate
    #def test_recv(self, tmp_path, fb):
    #    # Single chunk
    #    def request_callback(request):
    #        r_body = 'Testing login phase 1'

    #        params = {
    #            'section': 'bio'
    #        }

    #        return (200, None, r_body)

    #    responses.add_callback(
    #        responses.GET,
    #        'https://m.facebook.com/test/about',
    #        callback=request_callback,
    #        cookies={'fr': 'fr_cookie',
    #                 'sb': 'sb_cookie'},
    #        status=200)


    #    # Multichunk
    #    pass

    #@responses.activate
    #def test_send(self, tmp_path, fb):
    #    # Single chunk

    #    # Multichunk
    #    pass
