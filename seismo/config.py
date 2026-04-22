import pipyadc.ADS1256_definitions as ads_defs
import pydantic
import pydantic_settings

VALID_GAINS = (1, 2, 4, 8, 16, 32, 64)
VALID_SPS = (2.5, 10, 50, 100, 500, 1000, 2000, 7500, 15000, 30000)

class SPIConfig(pydantic.BaseModel):
    spi_bus: int = 0
    spi_channel: int = 0
    spi_frequency: int = 976563

class ADSPinsConfig(pydantic.BaseModel):
    cs_pin: int = 22
    drdy_pin: int = 17
    reset_pin: int | None = 18
    pdwn_pin: int | None = 27
    chip_select_gpios_initialize: tuple[int, ...] = (22, 23)

class ADSChipConfig(pydantic.BaseModel):
    drdy_timeout: float = 2.0
    drdy_delay: float = 0.000001
    clkin_frequency: int = 7680000
    chip_hard_reset_on_start: bool = False
    chip_id: int = 3

class ADSConfig(pydantic.BaseModel):
    spi: SPIConfig = SPIConfig()
    pins: ADSPinsConfig = ADSPinsConfig()
    chip: ADSChipConfig = ADSChipConfig()

    v_ref: float = 2.5
    gain: int = 1
    drate: int = 2000

    active_channels: list[int] = pydantic.Field(default_factory=lambda: [0])

    @pydantic.field_validator("gain")
    def check_gain(cls, v):
        if v not in VALID_GAINS:
            raise ValueError(f"Gain must be one of {VALID_GAINS}")
        return v

    @pydantic.field_validator("drate")
    def check_sps(cls, v):
        if v not in VALID_SPS:
            raise ValueError(f"SPS (drate) must be one of {VALID_SPS}")
        return v

class GPSConfig(pydantic.BaseModel):
    gps_port: str = "/dev/ttyS0"
    gps_baudrate: int = 9600

    timeout: float = 120.0
    retry_interval: float = 5.0

class WebServerConfig(pydantic.BaseModel):
    host: str = "0.0.0.0"
    port: int = 8000
    password_set: bool = False
    password: str = "admin"
    data_update_interval: float = 20.0
    start_server: bool = True

class Config(pydantic_settings.BaseSettings):
    ads: ADSConfig = ADSConfig()
    gps: GPSConfig = GPSConfig()
    web_server: WebServerConfig = WebServerConfig()

    buffer_size: int = 20000
    output_folder: str = "./data"
    report_filename_format: str = "report_{timestamp}.csv"
    report_type: str = "csv"
    log_level: str = "INFO"

    model_config = pydantic_settings.SettingsConfigDict(
        env_file_encoding="utf-8",
    )

    @classmethod
    def settings_customise_sources(cls, settings_cls, *args, **kwargs):
        return (pydantic_settings.TomlConfigSettingsSource(
            settings_cls, "config.toml",
        ),)

GAIN_MAP = { i: getattr(ads_defs, f"GAIN_{i}") for i in VALID_GAINS }
SPS_MAP = {
    str(i): getattr(ads_defs, f"DRATE_{i}") for i in VALID_SPS if i != 2.5
}
SPS_MAP[str(2.5)] = ads_defs.DRATE_2_5

class LibConfigAdapter:
    def __init__(self, config: ADSConfig):
        self.SPI_BUS = config.spi.spi_bus
        self.SPI_CHANNEL = config.spi.spi_channel
        self.SPI_FREQUENCY = config.spi.spi_frequency

        self.CS_PIN = config.pins.cs_pin
        self.DRDY_PIN = config.pins.drdy_pin
        self.RESET_PIN = config.pins.reset_pin
        self.PDWN_PIN = config.pins.pdwn_pin
        self.CHIP_SELECT_GPIOS_INITIALIZE = \
            config.pins.chip_select_gpios_initialize

        self.DRDY_TIMEOUT = config.chip.drdy_timeout
        self.DRDY_DELAY = config.chip.drdy_delay
        self.CLKIN_FREQUENCY = config.chip.clkin_frequency
        self.CHIP_HARD_RESET_ON_START = config.chip.chip_hard_reset_on_start
        self.CHIP_ID = config.chip.chip_id

        self.v_ref = config.v_ref
        self.gain = getattr(ads_defs, GAIN_MAP[config.gain])
        self.gain_flags = self.gain
        self.drate = getattr(ads_defs, SPS_MAP[str(config.drate)])
        self.status = ads_defs.BUFFER_ENABLE
        self.adcon = ads_defs.CLKOUT_OFF | ads_defs.SDCS_OFF | self.gain_flags
        self.ch_sequence = [
            getattr(ads_defs, f"POS_AIN{i}") | ads_defs.NEG_AINCOM
            for i in config.active_channels
        ]
        self.mux = self.ch_sequence[0] if self.ch_sequence else ads_defs.POS_AIN0 | ads_defs.NEG_AINCOM
