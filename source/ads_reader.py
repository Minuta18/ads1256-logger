import os
import ctypes

lib_path = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "../cmake-build-debug/ads_reader/libads_reader.so")
)

if not os.path.exists(lib_path):
    raise FileNotFoundError(f"Shared library not found at {lib_path}")

ads_reader = ctypes.CDLL(lib_path)
ads_reader.get_string.restype = ctypes.c_char_p


class SpidevConfig(ctypes.Structure):
    _fields_ = [
        ("spi_speed_hz", ctypes.c_uint32),
        ("spi_mode",     ctypes.c_uint8),
        ("spi_bus",      ctypes.c_uint8),
        ("spi_bits",     ctypes.c_uint8),
        ("chip_select",  ctypes.c_uint8),
    ]

class SpidevDevice(ctypes.Structure):
    pass

ads_reader.spidev_open.argtypes = [ctypes.POINTER(SpidevConfig), ]
ads_reader.spidev_open.restype = ctypes.POINTER(SpidevDevice)
ads_reader.spidev_close.argtypes = [ctypes.POINTER(SpidevDevice), ]
ads_reader.spidev_close.restype = None
ads_reader.spidev_transfer.argtypes = [
    ctypes.POINTER(SpidevDevice),
    ctypes.POINTER(ctypes.c_uint8),
    ctypes.POINTER(ctypes.c_uint8),
    ctypes.c_size_t,
]
ads_reader.spidev_transfer.restype = ctypes.c_int
ads_reader.spidev_get_config.argtypes = [ctypes.POINTER(SpidevDevice), ]
ads_reader.spidev_get_config.restype = ctypes.POINTER(SpidevConfig)


class Ads1256Config(ctypes.Structure):
    _fields_ = [
        ("spidev",       ctypes.c_void_p),
        ("drate",        ctypes.c_uint8),
        ("gain",         ctypes.c_uint8),
        ("drdy_gpio",     ctypes.c_uint8),
        ("pdwn_gpio",    ctypes.c_uint8),
    ]

class Ads1256Device(ctypes.Structure):
    pass

ads_reader.ads1256_open.argtypes = [ctypes.POINTER(Ads1256Config), ]
ads_reader.ads1256_open.restype = ctypes.POINTER(Ads1256Device)
ads_reader.ads1256_close.argtypes = [ctypes.POINTER(Ads1256Device), ]
ads_reader.ads1256_close.restype = None
ads_reader.ads1256_reset_chip.argtypes = [ctypes.POINTER(Ads1256Device), ]
ads_reader.ads1256_reset_chip.restype = ctypes.c_int
ads_reader.ads1256_read_channel.argtypes = [
    ctypes.POINTER(Ads1256Device),
    ctypes.c_uint8,
    ctypes.POINTER(ctypes.c_int32),
]
ads_reader.ads1256_read_channel.restype = ctypes.c_int
