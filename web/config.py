import pydantic
import pydantic_settings

class WebServerConfig(pydantic.BaseModel):
    host: str = '0.0.0.0'
    port: int = 8000
    password_set: bool = False
    password: str = "admin"
    data_update_interval: float = 20.0

class Config(pydantic_settings.BaseSettings):
    web_server: WebServerConfig = WebServerConfig()

    model_config = pydantic_settings.SettingsConfigDict(
        env_file_encoding="utf-8",
    )

    @classmethod
    def settings_customise_sources(cls, settings_cls, *args, **kwargs):
        return (pydantic_settings.TomlConfigSettingsSource(
            settings_cls, "config.toml"
        ),)
