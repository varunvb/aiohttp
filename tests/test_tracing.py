import asyncio
from types import SimpleNamespace
from unittest.mock import Mock

import pytest

from aiohttp.tracing import Trace, TraceConfig


class TestTraceConfig:

    def test_trace_context_default(self):
        trace_config = TraceConfig()
        assert isinstance(trace_config.trace_context(), SimpleNamespace)

    def test_trace_context_class(self):
        trace_config = TraceConfig(trace_context_class=dict)
        assert isinstance(trace_config.trace_context(), dict)

    def test_freeze(self):
        trace_config = TraceConfig()
        trace_config.freeze()

        assert trace_config.on_request_start.frozen
        assert trace_config.on_request_end.frozen
        assert trace_config.on_request_exception.frozen
        assert trace_config.on_request_redirect.frozen
        assert trace_config.on_connection_queued_start.frozen
        assert trace_config.on_connection_queued_end.frozen
        assert trace_config.on_connection_create_start.frozen
        assert trace_config.on_connection_create_end.frozen
        assert trace_config.on_connection_reuseconn.frozen
        assert trace_config.on_dns_resolvehost_start.frozen
        assert trace_config.on_dns_resolvehost_end.frozen
        assert trace_config.on_dns_cache_hit.frozen
        assert trace_config.on_dns_cache_miss.frozen


class TestTrace:

    @pytest.mark.parametrize('signal', [
        'request_start',
        'request_end',
        'request_exception',
        'request_redirect',
        'connection_queued_start',
        'connection_queued_end',
        'connection_create_start',
        'connection_create_end',
        'connection_reuseconn',
        'dns_resolvehost_start',
        'dns_resolvehost_end',
        'dns_cache_hit',
        'dns_cache_miss'
    ])
    async def test_send(self, loop, signal):
        param = Mock()
        session = Mock()
        trace_context = Mock()
        callback = Mock(side_effect=asyncio.coroutine(Mock()))

        trace_config = TraceConfig()
        getattr(trace_config, "on_%s" % signal).append(callback)
        trace_config.freeze()
        trace = Trace(trace_config, session, trace_context)
        await getattr(trace, "send_%s" % signal)(param)

        callback.assert_called_once_with(
            session,
            trace_context,
            param
        )
