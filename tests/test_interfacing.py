import pytest

from future.interfacing import Interface


class IThing(Interface):
    def ping(self):
        raise NotImplementedError


class IAsyncThing(Interface):
    async def ping(self):
        raise NotImplementedError


class IStrictThing(Interface):
    __strict__ = True

    def ping(self):
        raise NotImplementedError


class IWithDefault(Interface):
    def ping(self):
        raise NotImplementedError

    def pong(self):
        return "pong"


def test_interface_rejects_missing_method():
    with pytest.raises(TypeError, match="must implement: ping"):
        class Bad(IThing):
            pass


def test_interface_rejects_signature_mismatch():
    with pytest.raises(TypeError, match="does not match interface"):
        class Bad(IThing):
            def ping(self, extra):
                return extra


def test_interface_accepts_matching_implementation():
    class Good(IThing):
        def ping(self):
            return "ok"

    assert Good().ping() == "ok"


def test_interface_accepts_async_stub_implementation():
    class Good(IAsyncThing):
        async def ping(self):
            return "ok"

    assert Good is not None


def test_interface_strict_rejects_extra_methods():
    with pytest.raises(TypeError, match="unsupported methods: boom"):
        class Bad(IStrictThing):
            def ping(self):
                return "ok"

            def boom(self):
                return "no"


def test_interface_allows_extra_methods_when_not_strict():
    class Good(IThing):
        def ping(self):
            return "ok"

        def boom(self):
            return "yes"

    assert Good().boom() == "yes"


def test_interface_default_method_is_not_required():
    class Good(IWithDefault):
        def ping(self):
            return "ok"

    assert Good().ping() == "ok"
    assert Good().pong() == "pong"
