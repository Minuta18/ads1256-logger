import pydantic
import pydantic_settings

class SPIConfig(pydantic.BaseModel):
    spi_bus: int = 0
    spi_device: int = 0

class ADSConfig(pydantic.BaseModel):
    gain: int = 1
    drate: int = 2000
    v_ref: float = 2.5
    channels: list[int] = [0, 1, 2, 3, 4, 5, 6, 7]

class Config(pydantic_settings.BaseSettings):
    spi: SPIConfig = SPIConfig()
    ads: ADSConfig = ADSConfig()

    output_file: str = "seismic_data.csv"
    buffer_size: int = 1000

    model_config = pydantic_settings.SettingsConfigDict(
        env_file_encoding="utf-8",
    )

    @classmethod
    def settings_customise_sources(cls, settings_cls, **kwargs):
        return (pydantic_settings.TomlConfigSettingsSource(
            settings_cls, "config.toml"
        ),)
