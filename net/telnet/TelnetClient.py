from __future__ import annotations
from dataclasses import dataclass
from queue import Queue, Empty
from typing import Optional, Callable

import socket
import threading

IAC  = 255
DONT = 254
DO   = 253
WONT = 252
WILL = 251
SB   = 250
SE   = 240

ECHO = 1
SGA  = 3
TTYPE = 24
NAWS  = 31
LINEMODE = 34


@dataclass(frozen=True)
class TelnetConfig:
    host: str
    port: int = 23
    connect_timeout_s: float = 5.0
    recv_buf: int = 4096
    keepalive: bool = True


class TelnetClient:
    """
    Threaded telnet-ish client:
      - connect/disconnect
      - send_line(text)
      - poll_line() -> Optional[str]
      - handles basic IAC negotiation by refusing most options (safe default)
    """

    def __init__(self, cfg: TelnetConfig, *, on_status: Optional[Callable[[str], None]] = None):
        self.cfg = cfg
        self._on_status = on_status
        self._sock: Optional[socket.socket] = None
        self._rx_thread: Optional[threading.Thread] = None
        self._stop = threading.Event()
        self._in_lines: "Queue[str]" = Queue()
        self._out_lock = threading.Lock()
        self._text_buf = bytearray()
        self._iac_state = 0  # 0=none, 1=got IAC, 2=got IAC+cmd, 3=in SB
        self._iac_cmd = 0
        self._sb_opt = 0
        self._sb_buf = bytearray()

    @property
    def connected(self) -> bool:
        return self._sock is not None

    def connect(self) -> None:
        if self.connected:
            return

        self._stop.clear()
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(self.cfg.connect_timeout_s)
        s.connect((self.cfg.host, self.cfg.port))
        s.settimeout(None)

        if self.cfg.keepalive:
            try:
                s.setsockopt(socket.SOL_SOCKET, socket.SO_KEEPALIVE, 1)
            except OSError:
                pass

        self._sock = s
        self._rx_thread = threading.Thread(target=self._rx_loop, name="TelnetClient.rx", daemon=True)
        self._rx_thread.start()
        self._status(f"Connected to {self.cfg.host}:{self.cfg.port}")

    def close(self) -> None:
        if not self.connected:
            return
        self._status("Disconnecting...")
        self._stop.set()
        try:
            if self._sock:
                try:
                    self._sock.shutdown(socket.SHUT_RDWR)
                except OSError:
                    pass
                self._sock.close()
        finally:
            self._sock = None
        self._status("Disconnected")

    def send_line(self, text: str) -> None:
        """
        Sends a line terminated with CRLF (typical telnet servers).
        """
        if not self._sock:
            raise RuntimeError("Not connected")
        data = (text + "\r\n").encode("utf-8", errors="replace")
        with self._out_lock:
            self._sock.sendall(data)

    def poll_line(self) -> Optional[str]:
        try:
            return self._in_lines.get_nowait()
        except Empty:
            return None

    def _status(self, msg: str) -> None:
        if self._on_status:
            try:
                self._on_status(msg)
            except Exception:
                pass

    def _rx_loop(self) -> None:
        assert self._sock is not None
        s = self._sock

        try:
            while not self._stop.is_set():
                data = s.recv(self.cfg.recv_buf)
                if not data:
                    break
                self._feed(data)
        except OSError as e:
            self._status(f"Socket error: {e}")
        finally:
            # ensure we flip state even if remote closed
            try:
                s.close()
            except OSError:
                pass
            if self._sock is s:
                self._sock = None
            self._status("Connection closed")

    def _feed(self, data: bytes) -> None:
        for b in data:
            if self._iac_state == 0:
                if b == IAC:
                    self._iac_state = 1
                else:
                    self._text_buf.append(b)
                continue

            if self._iac_state == 1:
                if b == IAC:
                    # escaped 255
                    self._text_buf.append(IAC)
                    self._iac_state = 0
                elif b == SB:
                    self._iac_state = 3
                    self._sb_opt = 0
                    self._sb_buf.clear()
                else:
                    self._iac_cmd = b
                    self._iac_state = 2
                continue

            if self._iac_state == 2:
                opt = b
                self._handle_iac(self._iac_cmd, opt)
                self._iac_state = 0
                continue

            if self._iac_state == 3:
                # subnegotiation: IAC SB <opt> ... IAC SE
                if self._sb_opt == 0:
                    self._sb_opt = b
                    continue

                if b == IAC:
                    self._iac_state = 4  # possible SE
                    continue

                self._sb_buf.append(b)
                continue

            if self._iac_state == 4:
                if b == SE:
                    self._handle_sb(self._sb_opt, bytes(self._sb_buf))
                    self._iac_state = 0
                else:
                    # not SE; treat as data inside SB
                    self._sb_buf.append(IAC)
                    self._sb_buf.append(b)
                    self._iac_state = 3

        self._flush_text_lines()

    def _flush_text_lines(self) -> None:
        if not self._text_buf:
            return

        txt = self._text_buf.decode("utf-8", errors="replace")
        txt = txt.replace("\r\n", "\n").replace("\r", "\n")
        parts = txt.split("\n")
        complete = parts[:-1]
        tail = parts[-1]

        for line in complete:
            self._in_lines.put(line)

        self._text_buf.clear()
        if tail:
            self._text_buf.extend(tail.encode("utf-8", errors="replace"))

    def _send_iac(self, cmd: int, opt: int) -> None:
        if not self._sock:
            return
        with self._out_lock:
            self._sock.sendall(bytes([IAC, cmd, opt]))

    def _handle_iac(self, cmd: int, opt: int) -> None:
        if cmd == WILL:
            self._send_iac(DONT, opt)
        elif cmd == DO:
            self._send_iac(WONT, opt)
        elif cmd in (WONT, DONT):
            pass

    def _handle_sb(self, opt: int, payload: bytes) -> None:
        _ = (opt, payload)
