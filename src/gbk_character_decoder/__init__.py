"""GBK Character Decoder.

Decodes and encodes Chinese text using the GBK character encoding standard,
a superset of GB2312. Pure standard-library implementation backed by
Python's codecs registry, which contains the full GBK mapping table.
"""

from .core import GBKDecoder, GBKEncoder, decode, encode

__all__ = ["GBKDecoder", "GBKEncoder", "decode", "encode"]
__version__ = "1.0.0"
