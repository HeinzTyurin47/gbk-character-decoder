# GBK Character Decoder

Decodes and encodes Chinese text using the GBK character encoding standard, a superset of GB2312. Pure Python, standard library only.

```python
from gbk_character_decoder import GBKDecoder, GBKEncoder, decode, encode

# one-shot functions
text = decode(b"\xc4\xe3\xba\xc3")   # -> "你好"
raw = encode("你好")                   # -> b'\xc4\xe3\xba\xc3'

# reusable objects with an explicit error policy
decoder = GBKDecoder(errors="strict")     # default; raises on bad bytes
lenient = GBKDecoder(errors="replace")    # bad bytes become U+FFFD
encoder = GBKEncoder(errors="strict")

assert decoder.decode(b"\xc4\xe3\xba\xc3") == "你好"
assert encoder.encode("你好") == b'\xc4\xe3\xba\xc3'
```

## Why this exists

Some legacy Chinese systems still emit GBK bytes (the DOS-era mainland-China standard that extends GB2312 with Traditional characters and symbols). Python's standard library already carries a complete GBK mapping table through its codecs registry; this library does not re-derive that table. Instead it provides a small, typed, explicitly-documented surface around `bytes.decode('gbk')` and `str.encode('gbk')`, with strict error handling by default so that corrupted input surfaces as `UnicodeDecodeError` instead of being silently replaced with U+FFFD.

The trade-off: the mapping table is whatever your Python interpreter ships, so results may differ very slightly across CPython versions for a handful of rarely-used user-defined or vendor-assigned code points. If you need byte-for-byte stability across runtimes, vendor a specific table. Most real-world GBK text does not hit those code points.

## Edge you will hit

GBK is a double-byte encoding for Chinese text but a single-byte encoding for ASCII (0x00–0x7F). A lone byte in the lead-byte range (0x81–0xFE) without a trailing byte is malformed and raises under the default strict policy. Characters outside GBK's repertoire — which includes all emoji and most CJK Extension B ideographs — raise `UnicodeEncodeError` when encoding. Pass `errors='replace'` to either constructor if you want lenient `?`/U+FFFD substitution instead.

## Exports

- `GBKDecoder(errors='strict')` — class; `.decode(data: bytes) -> str`
- `GBKEncoder(errors='strict')` — class; `.encode(text: str) -> bytes`
- `decode(data, errors='strict') -> str` — convenience function
- `encode(text, errors='strict') -> bytes` — convenience function

Python 3.10+. No dependencies.
