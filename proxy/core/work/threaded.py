# -*- coding: utf-8 -*-
"""
    proxy.py
    ~~~~~~~~
    ⚡⚡⚡ Fast, Lightweight, Pluggable, TLS interception capable proxy server focused on
    Network monitoring, controls & Application development, testing, debugging.

    :copyright: (c) 2013-present by Abhinav Singh and contributors.
    :license: BSD, see LICENSE for more details.
"""
import socket
import argparse
import threading
from typing import Optional, Tuple

from .work import Work

from ..connection import TcpClientConnection
from ..event import EventQueue, eventNames


def start_threaded_work(
        flags: argparse.Namespace,
        conn: socket.socket,
        addr: Optional[Tuple[str, int]],
        event_queue: Optional[EventQueue] = None,
        publisher_id: Optional[str] = None,
) -> Tuple[Work[TcpClientConnection], threading.Thread]:
    """Utility method to start a work in a new thread."""
    work = flags.work_klass(
        TcpClientConnection(conn, addr),
        flags=flags,
        event_queue=event_queue,
        upstream_conn_pool=None,
    )
    # TODO: Keep reference to threads and join during shutdown.
    # This will ensure connections are not abruptly closed on shutdown
    # for threaded execution mode.
    thread = threading.Thread(target=work.run)
    thread.daemon = True
    thread.start()
    work.publish_event(
        event_name=eventNames.WORK_STARTED,
        event_payload={'fileno': conn.fileno(), 'addr': addr},
        publisher_id=publisher_id or 'thread#{0}'.format(
            thread.ident,
        ),
    )
    return (work, thread)
