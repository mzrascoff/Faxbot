import hmac
import hashlib

from api.app.providers import phaxio as phx
from api.app.providers import sinch as snc


def test_phaxio_hmac_good():
    body = b'{"id":123}'
    secret = 's3cr3t'
    sig = hmac.new(secret.encode('utf-8'), body, hashlib.sha1).hexdigest()
    headers = {"X-Phaxio-Signature": sig}
    assert phx.verify_webhook(headers, body, secret, strict=True) is True


def test_phaxio_hmac_bad():
    body = b'{"id":123}'
    secret = 's3cr3t'
    headers = {"X-Phaxio-Signature": 'bad'}
    assert phx.verify_webhook(headers, body, secret, strict=True) is False


def test_sinch_hmac_good_when_present():
    body = b'{"id":"abc"}'
    secret = 'key'
    sig = hmac.new(secret.encode('utf-8'), body, hashlib.sha256).hexdigest()
    headers = {"X-Sinch-Signature": sig}
    assert snc.verify_webhook(headers, body, secret, strict=True) is True


def test_sinch_no_header_non_strict():
    body = b'{}'
    secret = 'key'
    headers = {}
    assert snc.verify_webhook(headers, body, secret, strict=False) is True
    assert snc.verify_webhook(headers, body, secret, strict=True) is False

