import responses
import pytest
import time
from IPoFB.gateways.facebook import (
    Facebook
)


@pytest.fixture
def fb(cache_file='None'):
    return Facebook(cache_file)


class TestFacebook:
    def test_send():
        pass

    def test_recv():
        pass
