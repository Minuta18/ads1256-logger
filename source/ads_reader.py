import os
import ctypes
import typing
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
        ("gpio_name",    ctypes.c_char_p),
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

def _get_c_value(name: str, type: typing.Any) -> typing.Any:
    return type.in_dll(_lib, name).value

class Ads1256Commands:
    WAKEUP   = _get_c_value('ADS1256_CMD_WAKEUP', ctypes.c_uint8)
    RDATA    = _get_c_value('ADS1256_CMD_RDATA', ctypes.c_uint8)
    RDATAC   = _get_c_value('ADS1256_CMD_RDATAC', ctypes.c_uint8)
    SDATAC   = _get_c_value('ADS1256_CMD_SDATAC', ctypes.c_uint8)
    RREG     = _get_c_value('ADS1256_CMD_RREG', ctypes.c_uint8)
    WREG     = _get_c_value('ADS1256_CMD_WREG', ctypes.c_uint8)
    SELFCAL  = _get_c_value('ADS1256_CMD_SELFCAL', ctypes.c_uint8)
    SELFOCAL = _get_c_value('ADS1256_CMD_SELFOCAL', ctypes.c_uint8)
    SELFGCAL = _get_c_value('ADS1256_CMD_SELFGCAL', ctypes.c_uint8)
    SYSOCAL  = _get_c_value('ADS1256_CMD_SYSOCAL', ctypes.c_uint8)
    SYSGCAL  = _get_c_value('ADS1256_CMD_SYSGCAL', ctypes.c_uint8)
    SYNC     = _get_c_value('ADS1256_CMD_SYNC', ctypes.c_uint8)
    STANDBY  = _get_c_value('ADS1256_CMD_STANDBY', ctypes.c_uint8)
    RESET    = _get_c_value('ADS1256_CMD_RESET', ctypes.c_uint8)

class Ads1256Registers:
    STATUS = _get_c_value('ADS1256_REG_STATUS', ctypes.c_uint8)
    MUX    = _get_c_value('ADS1256_REG_MUX', ctypes.c_uint8)
    ADCON  = _get_c_value('ADS1256_REG_ADCON', ctypes.c_uint8)
    DRATE  = _get_c_value('ADS1256_REG_DRATE', ctypes.c_uint8)
    IO     = _get_c_value('ADS1256_REG_IO', ctypes.c_uint8)
    OFC0   = _get_c_value('ADS1256_REG_OFC0', ctypes.c_uint8)
    OFC1   = _get_c_value('ADS1256_REG_OFC1', ctypes.c_uint8)
    OFC2   = _get_c_value('ADS1256_REG_OFC2', ctypes.c_uint8)
    FSC0   = _get_c_value('ADS1256_REG_FSC0', ctypes.c_uint8)
    FSC1   = _get_c_value('ADS1256_REG_FSC1', ctypes.c_uint8)
    FSC2   = _get_c_value('ADS1256_REG_FSC2', ctypes.c_uint8)

def get_drate_value(drate: int) -> int:
    drate_list = [2.5, 5, 10, 15, 25, 30, 50, 60, 100, 500, 1000, 2000, 3750, 7500, 15000, 30000]
    if drate not in drate_list:
        return None
    if drate == 2.5:
        return _get_c_value('ADS1256_PARAM_DRATE_2_5', ctypes.c_uint8)
    return _get_c_value(f'ADS1256_PARAM_DRATE_{ drate }', ctypes.c_uint8)

def get_gain_value(gain: int) -> int:
    return _get_c_value(f'ADS1256_PARAM_GAIN_{ gain }', ctypes.c_uint8)


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
        pdwn_gpio: int = ...,
        gpio_name: str = "/dev/gpiochip0"
    ):
        assert drdy_gpio != ..., "drdy_gpio must be specified"
        assert pdwn_gpio != ..., "pdwn_gpio must be specified"
        
        self._spi_bus = spi_bus
        self._config = _Ads1256Config(
            spidev=spi_bus.raw_ptr,
            drate=drate,
            gain=gain,
            drdy_gpio=drdy_gpio,
            pdwn_gpio=pdwn_gpio,
            gpio_name=gpio_name.encode('utf-8')
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