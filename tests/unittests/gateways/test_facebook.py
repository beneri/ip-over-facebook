import responses
import pytest
from IPoFB.gateways.facebook import (
    Facebook
)


@pytest.fixture
def fb(cache_file='None'):
    return Facebook(cache_file)


def is_dict_contained_in_dict(a: dict, b: dict):
    """
    Checks if a is contained in b
    """
    try:
        for key, value in a.items():
            if b[key] != value:
                return False
    except KeyError:
        return False
    return True


class TestFacebook:
    @staticmethod
    def are_valid_headers(headers: dict):
        valid_headers = {
            'origin': 'https://www.facebook.com',
            'accept-encoding': 'gzip',
            'accept-language': 'en-US,en;q=1.0',
            'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) '
            'AppleWebKit/537.36 '
            '(KHTML, like Gecko) Chrome/65.0.3325.162 Safari/537.36',
            'content-type': 'application/x-www-form-urlencoded',
            'accept': '*/*',
            'referer': 'https://www.facebook.com/',
            'authority': 'www.facebook.com',
        }
        assert is_dict_contained_in_dict(valid_headers, headers)

    @staticmethod
    def logged_in_callback(request, ret_value=True):
        TestFacebook.are_valid_headers(request.headers)

        if ret_value:
            return (
                200,
                None,
                "")
        else:
            return (
                200,
                None,
                "You must log in to continue")

    @staticmethod
    def fake_username_callback(request, username='test'):
        TestFacebook.are_valid_headers(request.headers)
        return (200, None, username)

    @staticmethod
    def fake_login_callback(request, ret_value=True):
        TestFacebook.are_valid_headers(request.headers)

        params = {
            'login_attempt': '1',
            'lwv': '111'
        }
        assert is_dict_contained_in_dict(params, request.params)

        data = {
            'email': 'test',
            'pass': 'test'
        }
        assert is_dict_contained_in_dict(data, request.data)
        return (200, None, "")

    @staticmethod
    def fake_recv(request, expetected_value):
        TestFacebook.are_valid_headers(request.headers)
        assert request.data == expetected_value
        return (200, None, "")

    @staticmethod
    def fake_send(request, data):
        TestFacebook.are_valid_headers(request.headers)
        return (200, None, f'_5cds _2lcw _5cdt">{data}</div')

#    def test_logged_in_no_cache(self, fb):
#        responses.add_callback(
#            responses.GET,
#            'https://facebook.com/',
#            callback=lambda req: TestFacebook
#            .fake_username_callback(req, 'test'))
#
#        # Before login
#        responses.add_callback(
#            responses.GET,
#            'https://www.facebook.com/settings',
#            callback=lambda req: TestFacebook.logged_in_callback(req, True))
#
#        assert not fb.logged_in
#
#        # After login
#        responses.add_callback(
#            responses.GET,
#            'https://www.facebook.com/settings',
#            callback=lambda req: TestFacebook.fake_login_callback(req))
#        fb.login('test', 'test')
#
#        responses.add_callback(
#            responses.GET,
#            'https://www.facebook.com/settings',
#            callback=lambda req: TestFacebook.logged_in_callback(req, True))
#
#        assert fb.logged_in

    def test_send(self, fb):
        responses.add_callback(
            responses.GET,
            'https://facebook.com/',
            callback=lambda req: TestFacebook
            .fake_username_callback(req, 'test'))

        responses.add_callback(
            responses.GET,
            'https://m.facebook.com/test/about',
            callback=lambda req: TestFacebook.fake_recv(req, 'test'))
        fb.send('test')

#    def test_recv(self, fb):
#        responses.add_callback(
#            responses.GET,
#            'https://facebook.com/',
#            callback=lambda req: TestFacebook
#            .fake_username_callback(req, 'test'))
#
#        responses.add_callback(
#            responses.GET,
#            'https://m.facebook.com/test/about?section=bio',
#            callback=lambda req: TestFacebook.fake_send(req, 'test2'))
#        assert fb.recv() == 'test2'
