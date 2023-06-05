from __future__ import annotations

import ctypes as ct
import os
import platform
import sys
from base64 import b64decode

VERBOSE = False
SYSTEM = platform.system()
SYS64 = sys.maxsize > 2**32
DEFAULT_ENCODING = "utf-8"

PWStore = list[dict[str, str]]


def find_nss(locations, nssname) -> ct.CDLL:
    for loc in locations:
        nsslib = os.path.join(loc, nssname)

        nss: ct.CDLL = ct.CDLL(nsslib)
        return nss


def load_libnss():
    nssname = "libnss3.so"
    if SYS64:
        locations = ("",)
    return find_nss(locations, nssname)


class c_char_p_fromstr(ct.c_char_p):
    def from_param(self):
        return self.encode(DEFAULT_ENCODING)


class NSSProxy:
    class SECItem(ct.Structure):
        _fields_ = [
            ('type', ct.c_uint),
            ('data', ct.c_char_p),
            ('len', ct.c_uint),
        ]

        def decode_data(self):
            _bytes = ct.string_at(self.data, self.len)
            return _bytes.decode(DEFAULT_ENCODING)

    class PK11SlotInfo(ct.Structure):
        pass

    def __init__(self):
        self.libnss = load_libnss()

        SlotInfoPtr = ct.POINTER(self.PK11SlotInfo)
        SECItemPtr = ct.POINTER(self.SECItem)

        self._set_ctypes(ct.c_int, "NSS_Init", c_char_p_fromstr)
        self._set_ctypes(ct.c_int, "NSS_Shutdown")
        self._set_ctypes(SlotInfoPtr, "PK11_GetInternalKeySlot")
        self._set_ctypes(None, "PK11_FreeSlot", SlotInfoPtr)
        self._set_ctypes(ct.c_int, "PK11_NeedLogin", SlotInfoPtr)
        self._set_ctypes(ct.c_int, "PK11_CheckUserPassword",
                         SlotInfoPtr, c_char_p_fromstr)
        self._set_ctypes(ct.c_int, "PK11SDR_Decrypt",
                         SECItemPtr, SECItemPtr, ct.c_void_p)
        self._set_ctypes(None, "SECITEM_ZfreeItem", SECItemPtr, ct.c_int)

        self._set_ctypes(ct.c_int, "PORT_GetError")
        self._set_ctypes(ct.c_char_p, "PR_ErrorToName", ct.c_int)
        self._set_ctypes(ct.c_char_p, "PR_ErrorToString",
                         ct.c_int, ct.c_uint32)

    def _set_ctypes(self, restype, name, *argtypes):
        res = getattr(self.libnss, name)
        res.argtypes = argtypes
        res.restype = restype

        if restype == ct.c_char_p:
            def _decode(result, func, *args):
                return result.decode(DEFAULT_ENCODING)
            res.errcheck = _decode

        setattr(self, "_" + name, res)

    def initialize(self, profile: str):
        profile_path = "sql:" + profile
        self._NSS_Init(profile_path)

    def shutdown(self):
        self._NSS_Shutdown()

    def decrypt(self, data64):
        data = b64decode(data64)
        inp = self.SECItem(0, data, len(data))
        out = self.SECItem(0, None, 0)

        self._PK11SDR_Decrypt(inp, out, None)

        try:
            res = out.decode_data()
        finally:
            self._SECITEM_ZfreeItem(out, 0)

        return res
