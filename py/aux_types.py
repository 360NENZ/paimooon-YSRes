# This is a generated file! Please edit source .ksy file and use kaitai-struct-compiler to rebuild

import kaitaistruct
from kaitaistruct import KaitaiStruct, KaitaiStream, BytesIO


if getattr(kaitaistruct, 'API_VERSION', (0, 9)) < (0, 9):
    raise Exception("Incompatible Kaitai Struct Python API: 0.9 or later is required, but you have %s" % (kaitaistruct.__version__))

class AuxTypes(KaitaiStruct):
    """Miscellaneous types used in serialization
    Credit for dynamic_* stuff goes to Raz
    """
    def __init__(self, _io, _parent=None, _root=None):
        self._io = _io
        self._parent = _parent
        self._root = _root if _root else self
        self._read()

    def _read(self):
        pass

    class LengthPrefixedBitfield(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.length = AuxTypes.VlqBase128LeU(self._io, self, self._root)
            self.bitfield = []
            for i in range(self.length.value):
                self.bitfield.append(self._io.read_u1())


        @property
        def value(self):
            if hasattr(self, '_m_value'):
                return self._m_value

            self._m_value = (((((((((self.bitfield[0] if self.length.value >= 1 else 0) + ((self.bitfield[1] << 8) if self.length.value >= 2 else 0)) + ((self.bitfield[2] << 16) if self.length.value >= 3 else 0)) + ((self.bitfield[3] << 24) if self.length.value >= 4 else 0)) + ((self.bitfield[4] << 32) if self.length.value >= 5 else 0)) + ((self.bitfield[5] << 40) if self.length.value >= 6 else 0)) + ((self.bitfield[6] << 48) if self.length.value >= 7 else 0)) + ((self.bitfield[7] << 56) if self.length.value >= 8 else 0)) + ((self.bitfield[8] << 64) if self.length.value >= 9 else 0))
            return getattr(self, '_m_value', None)


    class DynamicInt(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.is_string = self._io.read_u1()
            _on = self.is_string
            if _on == 0:
                self.data = AuxTypes.VlqBase128LeS(self._io, self, self._root)
            elif _on == 1:
                self.data = AuxTypes.String(self._io, self, self._root)


    class DynamicFormula(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.length = AuxTypes.VlqBase128LeS(self._io, self, self._root)
            self.elements = []
            for i in range(self.length.value):
                self.elements.append(AuxTypes.DynamicOperator(self._io, self, self._root))



    class DynamicString(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.is_dynamic = self._io.read_u1()
            self.data = AuxTypes.String(self._io, self, self._root)


    class VlqBase128Le(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.ks__groups = []
            i = 0
            while True:
                _ = AuxTypes.VlqBase128Le.Group(self._io, self, self._root)
                self.ks__groups.append(_)
                if not (_.has_next):
                    break
                i += 1

        class Group(KaitaiStruct):
            def __init__(self, _io, _parent=None, _root=None):
                self._io = _io
                self._parent = _parent
                self._root = _root if _root else self
                self._read()

            def _read(self):
                self.b = self._io.read_u1()

            @property
            def has_next(self):
                """If true, then we have more bytes to read."""
                if hasattr(self, '_m_has_next'):
                    return self._m_has_next

                self._m_has_next = (self.b & 128) != 0
                return getattr(self, '_m_has_next', None)

            @property
            def value(self):
                """The 7-bit (base128) numeric value chunk of this group."""
                if hasattr(self, '_m_value'):
                    return self._m_value

                self._m_value = (self.b & 127)
                return getattr(self, '_m_value', None)


        @property
        def value_unsigned(self):
            """Resulting unsigned value as normal integer."""
            if hasattr(self, '_m_value_unsigned'):
                return self._m_value_unsigned

            self._m_value_unsigned = (((((((self.ks__groups[0].value + ((self.ks__groups[1].value << 7) if self.len >= 2 else 0)) + ((self.ks__groups[2].value << 14) if self.len >= 3 else 0)) + ((self.ks__groups[3].value << 21) if self.len >= 4 else 0)) + ((self.ks__groups[4].value << 28) if self.len >= 5 else 0)) + ((self.ks__groups[5].value << 35) if self.len >= 6 else 0)) + ((self.ks__groups[6].value << 42) if self.len >= 7 else 0)) + ((self.ks__groups[7].value << 49) if self.len >= 8 else 0))
            return getattr(self, '_m_value_unsigned', None)

        @property
        def sign_bit(self):
            """Sign bit for Zigzag-encoded integer."""
            if hasattr(self, '_m_sign_bit'):
                return self._m_sign_bit

            self._m_sign_bit = (self.value_unsigned & 1)
            return getattr(self, '_m_sign_bit', None)

        @property
        def value_signed(self):
            """Resulting signed value as Zigzag-encoded integer."""
            if hasattr(self, '_m_value_signed'):
                return self._m_value_signed

            self._m_value_signed = (self.value_absolute ^ -(self.sign_bit))
            return getattr(self, '_m_value_signed', None)

        @property
        def value_absolute(self):
            """Absolute value for Zigzag-encoded integer."""
            if hasattr(self, '_m_value_absolute'):
                return self._m_value_absolute

            self._m_value_absolute = (self.value_unsigned >> 1)
            return getattr(self, '_m_value_absolute', None)

        @property
        def len(self):
            if hasattr(self, '_m_len'):
                return self._m_len

            self._m_len = len(self.ks__groups)
            return getattr(self, '_m_len', None)


    class VlqBase128LeS(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.data = AuxTypes.VlqBase128Le(self._io, self, self._root)

        @property
        def value(self):
            if hasattr(self, '_m_value'):
                return self._m_value

            self._m_value = self.data.value_signed
            return getattr(self, '_m_value', None)


    class String(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.length = AuxTypes.VlqBase128LeU(self._io, self, self._root)
            self.data = (self._io.read_bytes(self.length.value)).decode(u"UTF-8")


    class DynamicOperator(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.is_operator = self._io.read_u1()
            _on = self.is_operator
            if _on == 0:
                self.data = AuxTypes.BaseDynamicFloat(self._io, self, self._root)
            elif _on == 1:
                self.data = AuxTypes.VlqBase128LeS(self._io, self, self._root)


    class DynamicArgument(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.type_code = AuxTypes.VlqBase128LeU(self._io, self, self._root)
            _on = self.type_code.value
            if _on == 10:
                self.data = AuxTypes.String(self._io, self, self._root)
            elif _on == 4:
                self.data = self._io.read_u2le()
            elif _on == 6:
                self.data = self._io.read_u4le()
            elif _on == 7:
                self.data = self._io.read_f4le()
            elif _on == 1:
                self.data = self._io.read_s1()
            elif _on == 3:
                self.data = self._io.read_s2le()
            elif _on == 5:
                self.data = self._io.read_s4le()
            elif _on == 8:
                self.data = self._io.read_f8le()
            elif _on == 9:
                self.data = self._io.read_u1()
            elif _on == 2:
                self.data = self._io.read_u1()


    class DynamicFloat(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.is_formula = self._io.read_u1()
            _on = self.is_formula
            if _on == 0:
                self.data = AuxTypes.BaseDynamicFloat(self._io, self, self._root)
            elif _on == 1:
                self.data = AuxTypes.DynamicFormula(self._io, self, self._root)


    class Error(KaitaiStruct):
        """Type used in misc situations to signal about an error."""
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.message = self._io.read_bytes(60)
            if not self.message == b"\x54\x68\x65\x72\x65\x20\x77\x61\x73\x20\x61\x6E\x20\x65\x72\x72\x6F\x72\x20\x70\x61\x72\x73\x69\x6E\x67\x20\x64\x61\x74\x61\x3B\x20\x70\x6C\x65\x61\x73\x65\x20\x63\x68\x65\x63\x6B\x20\x4B\x53\x59\x20\x64\x65\x66\x69\x6E\x69\x74\x69\x6F\x6E":
                raise kaitaistruct.ValidationNotEqualError(b"\x54\x68\x65\x72\x65\x20\x77\x61\x73\x20\x61\x6E\x20\x65\x72\x72\x6F\x72\x20\x70\x61\x72\x73\x69\x6E\x67\x20\x64\x61\x74\x61\x3B\x20\x70\x6C\x65\x61\x73\x65\x20\x63\x68\x65\x63\x6B\x20\x4B\x53\x59\x20\x64\x65\x66\x69\x6E\x69\x74\x69\x6F\x6E", self.message, self._io, u"/types/error/seq/0")


    class BaseDynamicFloat(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.is_string = self._io.read_u1()
            _on = self.is_string
            if _on == 0:
                self.data = self._io.read_f4le()
            elif _on == 1:
                self.data = AuxTypes.String(self._io, self, self._root)


    class VlqBase128LeU(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.data = AuxTypes.VlqBase128Le(self._io, self, self._root)

        @property
        def value(self):
            if hasattr(self, '_m_value'):
                return self._m_value

            self._m_value = self.data.value_unsigned
            return getattr(self, '_m_value', None)



