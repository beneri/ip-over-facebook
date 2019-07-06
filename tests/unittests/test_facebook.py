import responses
import pytest
from IPoFB.facebook import Facebook


@pytest.fixture
def fb(cache_file='None'):
    return Facebook(cache_file)


class TestFacebookClass:
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
