from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import AnyUrl, SecretStr

class Settings(BaseSettings):
    # auth for this API (optional)
    basic_user: str = "accounting"
    basic_pass: SecretStr = SecretStr("changeInProd")


    # file storage
    file_storage_url: str = "http://localhost:9091"
    file_get_endpoint: str = "/files-uploader/file"
    file_upload_endpoint: str = "/file-storage/"
    file_user: str = "api-user"
    file_pass: SecretStr = SecretStr("v07lvt6Z")

    accounting_user: str = "api-user"
    accounting_pass: SecretStr = SecretStr("v07lvt6Z")

    # HTTP behaviour
    request_timeout_s: float = 10.0

    model_config = SettingsConfigDict(env_prefix="RED_", env_file=".env", extra="ignore")

settings = Settings()  # import from others
