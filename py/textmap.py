# This is a generated file! Please edit source .ksy file and use kaitai-struct-compiler to rebuild

import kaitaistruct
from kaitaistruct import KaitaiStruct, KaitaiStream, BytesIO

from aux_types import AuxTypes

if getattr(kaitaistruct, 'API_VERSION', (0, 9)) < (0, 9):
    raise Exception("Incompatible Kaitai Struct Python API: 0.9 or later is required, but you have %s" % (kaitaistruct.__version__))

class Textmap(KaitaiStruct):
    def __init__(self, _io, _parent=None, _root=None):
        self._io = _io
        self._parent = _parent
        self._root = _root if _root else self
        self._read()

    def _read(self):
        self.textmap = []
        i = 0
        while not self._io.is_eof():
            self.textmap.append(Textmap.Block(self._io, self, self._root))
            i += 1


    class Block(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.sus = AuxTypes.VlqBase128LeU(self._io, self, self._root)
            self.sus2 = AuxTypes.VlqBase128LeU(self._io, self, self._root)
            self.hash = AuxTypes.VlqBase128LeU(self._io, self, self._root)
            self.string = AuxTypes.String(self._io, self, self._root)



