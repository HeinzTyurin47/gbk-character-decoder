"""GBK codec helpers built on Python's standard-library GBK table.

Python ships a complete GBK mapping table in its codecs registry.  Rather
than re-deriving that table from GB2312 + extension blocks (which is error-
prone and duplicates work the CPython maintainers have already done and
validated against ICU), we delegate to the registered ``gbk`` codec.  The
value this module adds is a small, explicitly-typed surface with strict
error handling, so callers get predictable ``UnicodeDecodeError`` /
``UnicodeEncodeError`` propagation instead of Python's lenient default
replacement behaviour.
"""

import codecs
from typing import List


class GBKDecoder:
    """Decode GBK-encoded bytes into a Python ``str``.

    The decoder is stateless across calls; each ``decode`` call is
    independent.  ``errors='strict'`` is the default because silent
    replacement with U+FFFD hides real data corruption in text that is
    usually machine-generated; callers who want lenient behaviour can
    pass ``errors='replace'`` explicitly.
    """

    def __init__(self, errors: str = "strict") -> None:
        # Resolve the error handler once so an invalid name fails fast at
        # construction rather than on the first decode call.
        codecs.lookup_error(errors)
        self._errors = errors

    def decode(self, data: bytes) -> str:
        """Decode *data* from GBK to text.

        Raises ``UnicodeDecodeError`` under the default ``strict`` policy
        when *data* contains a byte sequence that is not valid GBK.
        """
        if not isinstance(data, (bytes, bytearray, memoryview)):
            raise TypeError(
                f"GBKDecoder.decode expects a bytes-like object, got {type(data).__name__}"
            )
        # materialize memoryview/bytearray to plain bytes for the codec call
        raw = bytes(data)
        return raw.decode("gbk", errors=self._errors)


class GBKEncoder:
    """Encode Python ``str`` into GBK bytes.

    Mirrors :class:`GBKDecoder`.  ``errors='strict'`` by default so that
    attempting to encode a character outside the GBK repertoire raises
    rather than silently dropping it.
    """

    def __init__(self, errors: str = "strict") -> None:
        codecs.lookup_error(errors)
        self._errors = errors

    def encode(self, text: str) -> bytes:
        """Encode *text* to GBK bytes.

        Raises ``UnicodeEncodeError`` under ``strict`` when *text* contains
        a character that has no GBK representation (for example most
        emoji or rarely-used CJK Extension B ideographs).
        """
        if not isinstance(text, str):
            raise TypeError(
                f"GBKEncoder.encode expects a str, got {type(text).__name__}"
            )
        return text.encode("gbk", errors=self._errors)


def decode(data: bytes, errors: str = "strict") -> str:
    """Module-level convenience wrapper around :meth:`GBKDecoder.decode`."""
    return GBKDecoder(errors=errors).decode(data)


def encode(text: str, errors: str = "strict") -> bytes:
    """Module-level convenience wrapper around :meth:`GBKEncoder.encode`."""
    return GBKEncoder(errors=errors).encode(text)


def _load_all_gbk_chars() -> List[str]:
    """Materialise every character representable in GBK.

    Used only by tests to exercise the full mapping.  Iterating the BMP
    and attempting strict encode is the simplest deterministic way to
    collect the set without depending on private codec internals.
    """
    out: List[str] = []
    for cp in range(0x10000):
        ch = chr(cp)
        try:
            ch.encode("gbk")
        except UnicodeEncodeError:
            continue
        out.append(ch)
    return out
