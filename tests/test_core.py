"""Tests for the GBK character decoder library."""

import codecs
import unittest

from gbk_character_decoder import GBKDecoder, GBKEncoder, decode, encode


class TestGBKDecode(unittest.TestCase):
    def test_ascii_passthrough(self):
        # GBK is a strict superset of ASCII for byte values 0x00-0x7F.
        self.assertEqual(decode(b"Hello"), "Hello")

    def test_common_chinese_phrase(self):
        # "你好" in GBK is the four-byte sequence C4 E3 BA C3.
        self.assertEqual(decode(b"\xc4\xe3\xba\xc3"), "你好")

    def test_traditional_chinese(self):
        # GBK covers many Traditional characters not in GB2312's core set.
        # "中華" — 華 (U+83EF) is a traditional-specific glyph present in GBK.
        encoded = "中華".encode("gbk")
        self.assertEqual(decode(encoded), "中華")

    def test_mixed_ascii_and_chinese(self):
        raw = b"\xc4\xe3\xba\xc3 world"
        self.assertEqual(decode(raw), "你好 world")

    def test_empty_input(self):
        self.assertEqual(decode(b""), "")

    def test_strict_rejects_truncated_lead_byte(self):
        # 0x81 is a valid GBK lead byte; a trailing byte that never comes
        # is invalid under strict handling.
        with self.assertRaises(UnicodeDecodeError):
            decode(b"\x81")

    def test_strict_rejects_invalid_trailing_byte(self):
        # 0x80 is not a valid lead byte in GBK (it's the continuation
        # range / undefined).  Under strict this must raise.
        with self.assertRaises(UnicodeDecodeError):
            decode(b"\x80")

    def test_replace_error_policy(self):
        # With errors='replace' a bad byte becomes U+FFFD instead of raising.
        result = decode(b"\x80", errors="replace")
        self.assertEqual(result, "\ufffd")

    def test_bytearray_accepted(self):
        self.assertEqual(decode(bytearray(b"\xc4\xe3")), "你")

    def test_memoryview_accepted(self):
        self.assertEqual(decode(memoryview(b"\xc4\xe3")), "你")

    def test_non_bytes_rejected(self):
        with self.assertRaises(TypeError):
            decode("not bytes")  # type: ignore[arg-type]

    def test_invalid_error_handler_rejected_at_construction(self):
        # Unknown error scheme should fail fast, not at decode time.
        with self.assertRaises(LookupError):
            GBKDecoder(errors="bogus")

    def test_decoder_is_stateless_across_calls(self):
        # Two consecutive decodes of partial input must not influence each
        # other; the decoder holds no carry-over state.
        d = GBKDecoder()
        self.assertEqual(d.decode(b"\xc4\xe3"), "你")
        self.assertEqual(d.decode(b"\xba\xc3"), "好")


class TestGBKEncode(unittest.TestCase):
    def test_encode_ascii(self):
        self.assertEqual(encode("Hello"), b"Hello")

    def test_encode_chinese(self):
        self.assertEqual(encode("你好"), b"\xc4\xe3\xba\xc3")

    def test_encode_roundtrip_full_bmp_subset(self):
        # Deterministic round-trip for every character GBK can represent.
        # We source the character set from the codec itself so the test
        # never invents characters the implementation doesn't claim to
        # support.
        for cp in range(0x10000):
            ch = chr(cp)
            try:
                gbk_bytes = ch.encode("gbk")
            except UnicodeEncodeError:
                continue
            self.assertEqual(decode(gbk_bytes), ch)

    def test_encode_unsupported_char_strict(self):
        # U+1F600 (😀) is outside GBK's repertoire.
        with self.assertRaises(UnicodeEncodeError):
            encode("😀")

    def test_encode_unsupported_char_replace(self):
        result = encode("a😀b", errors="replace")
        # replacement under gbk codec yields '?' for the unmapped char
        self.assertEqual(result, b"a?b")

    def test_encode_non_str_rejected(self):
        with self.assertRaises(TypeError):
            encode(b"not a str")  # type: ignore[arg-type]

    def test_encoder_invalid_error_handler_rejected(self):
        with self.assertRaises(LookupError):
            GBKEncoder(errors="nope")


if __name__ == "__main__":
    unittest.main()
