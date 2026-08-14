import os
import ctypes
from typing import Optional

lib_path = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "../cmake-build-debug/ads_reader/libads_reader.so")
)

if not os.path.exists(lib_path):
    raise FileNotFoundError(f"Shared library not found at {lib_path}")

_lib = ctypes.CDLL(lib_path)
_lib.get_string.restype = ctypes.c_char_p


class _SpidevConfig(ctypes.Structure):
    _fields_ = [
        ("spi_speed_hz", ctypes.c_uint32),
        ("spi_mode",     ctypes.c_uint8),
        ("spi_bus",      ctypes.c_uint8),
        ("spi_bits",     ctypes.c_uint8),
        ("chip_select",  ctypes.c_uint8),
    ]

class _SpidevDevice(ctypes.Structure):
    pass

_lib.spidev_open.argtypes = [ctypes.POINTER(_SpidevConfig), ]
_lib.spidev_open.restype = ctypes.POINTER(_SpidevDevice)
_lib.spidev_close.argtypes = [ctypes.POINTER(_SpidevDevice), ]
_lib.spidev_close.restype = None
_lib.spidev_transfer.argtypes = [
    ctypes.POINTER(_SpidevDevice),
    ctypes.POINTER(ctypes.c_uint8),
    ctypes.POINTER(ctypes.c_uint8),
    ctypes.c_size_t,
]
_lib.spidev_transfer.restype = ctypes.c_int
_lib.spidev_get_config.argtypes = [ctypes.POINTER(_SpidevDevice), ]
_lib.spidev_get_config.restype = ctypes.POINTER(_SpidevConfig)


class _Ads1256Config(ctypes.Structure):
    _fields_ = [
        ("spidev",       ctypes.c_void_p),
        ("drate",        ctypes.c_uint8),
        ("gain",         ctypes.c_uint8),
        ("drdy_gpio",     ctypes.c_uint8),
        ("pdwn_gpio",    ctypes.c_uint8),
    ]

class _Ads1256Device(ctypes.Structure):
    pass

_lib.ads1256_open.argtypes = [ctypes.POINTER(_Ads1256Config), ]
_lib.ads1256_open.restype = ctypes.POINTER(_Ads1256Device)
_lib.ads1256_close.argtypes = [ctypes.POINTER(_Ads1256Device), ]
_lib.ads1256_close.restype = None
_lib.ads1256_reset_chip.argtypes = [ctypes.POINTER(_Ads1256Device), ]
_lib.ads1256_reset_chip.restype = ctypes.c_int
_lib.ads1256_read_channel.argtypes = [
    ctypes.POINTER(_Ads1256Device),
    ctypes.c_uint8,
    ctypes.POINTER(ctypes.c_int32),
]
_lib.ads1256_read_channel.restype = ctypes.c_int

class Ads1256Commands:
    WAKEUP   = 0x00
    RDATA    = 0x01
    RDATAC   = 0x03
    SDATAC   = 0x0F
    RREG     = 0x10
    WREG     = 0x50
    SELFCAL  = 0xF0
    SELFOCAL = 0xF1
    SELFGCAL = 0xF2
    SYSOCAL  = 0xF3
    SYSGCAL  = 0xF4
    SYNC     = 0xFC
    STANDBY  = 0xFD
    RESET    = 0xFE

class Ads1256Registers:
    STATUS = 0x00
    MUX    = 0x01
    ADCON  = 0x02
    DRATE  = 0x03
    IO     = 0x04
    OFC0   = 0x05
    OFC1   = 0x06
    OFC2   = 0x07
    FSC0   = 0x08
    FSC1   = 0x09
    FSC2   = 0x0A

def get_drate_value(drate: int) -> int:
    drate_dict = {
        2.5: 0x03,
        5: 0x13,
        10: 0x23,
        15: 0x33,
        25: 0x43,
        30: 0x53,
        50: 0x63,
        60: 0x72,
        100: 0x82,
        500: 0x92,
        1000: 0xA1,
        2000: 0xB0,
        3750: 0xC0,
        7500: 0xD0,
        15000: 0xE0,
        30000: 0xF0
    }
    return drate_dict.get(drate, None)

def get_gain_value(gain: int) -> int:
    gain_dict = {
        1: 0x00,
        2: 0x01,
        4: 0x02,
        8: 0x03,
        16: 0x04,
        32: 0x05,
        64: 0x06
    }
    return gain_dict.get(gain, None)


class SPIBus:
    def __init__(
        self,
        speed_hz: int = 1000000,
        mode: int = 1,
        bus: int = 0,
        bits: int = 8,
        chip_select: int = 0
    ):
        self._config = _SpidevConfig(
            spi_speed_hz=speed_hz,
            spi_mode=mode,
            spi_bus=bus,
            spi_bits=bits,
            chip_select=chip_select
        )
        self._dev: Optional[ctypes.POINTER(_SpidevDevice)] = None

    def open(self) -> None:
        self._dev = _lib.spidev_open(ctypes.byref(self._config))
        if not self._dev:
            raise RuntimeError("Failed to open SPI device")

    def close(self) -> None:
        if self._dev:
            _lib.spidev_close(self._dev)
            self._dev = None

    @property
    def raw_ptr(self) -> ctypes.c_void_p:
        if not self._dev:
            raise RuntimeError("SPI device is not open")
        return ctypes.cast(self._dev, ctypes.c_void_p)

    def __enter__(self):
        self.open()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()


class ADS1256:
    def __init__(
        self,
        spi_bus: SPIBus,
        drate: int = 0xB0,
        gain: int = 0x00,
        drdy_gpio: int = ...,
        pdwn_gpio: int = ...
    ):
        assert drdy_gpio != ..., "drdy_gpio must be specified"
        assert pdwn_gpio != ..., "pdwn_gpio must be specified"
        
        self._spi_bus = spi_bus
        self._config = _Ads1256Config(
            spidev=spi_bus.raw_ptr,
            drate=drate,
            gain=gain,
            drdy_gpio=drdy_gpio,
            pdwn_gpio=pdwn_gpio
        )
        self._dev: Optional[ctypes.POINTER(_Ads1256Device)] = None

    def open(self) -> None:
        self._dev = _lib.ads1256_open(ctypes.byref(self._config))
        if not self._dev:
            raise RuntimeError("Failed to initialize ADS1256 chip")

    def close(self) -> None:
        if self._dev:
            _lib.ads1256_close(self._dev)
            self._dev = None

    def reset(self) -> None:
        if not self._dev:
            raise RuntimeError("ADS1256 is not initialized")
        if _lib.ads1256_reset_chip(self._dev) < 0:
            raise RuntimeError("Failed to reset ADS1256 chip")

    def read_channel(self, channel: int) -> int:
        if not self._dev:
            raise RuntimeError("ADS1256 is not initialized")

        val = ctypes.c_int32(0)
        if _lib.ads1256_read_channel(self._dev, channel, ctypes.byref(val)) < 0:
            raise RuntimeError(f"Failed to read from channel {channel}")
        return val.value

    def __enter__(self):
        self.open()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()