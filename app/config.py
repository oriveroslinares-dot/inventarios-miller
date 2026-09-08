"""
Configuración central de la aplicación.

Todos los valores sensibles (credenciales, tokens) se leen EXCLUSIVAMENTE
desde variables de entorno. Nunca se deben escribir credenciales reales
directamente en el código fuente.
"""
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    # Aplicación
    APP_NAME: str = "TRIPLE AAA DE CARTAGENITA"
    ENVIRONMENT: str = "development"
    SECRET_KEY: str = "dev-secret-key-change-in-production"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 480

    # Base de datos
    DATABASE_URL: str = "sqlite:///./triple_aaa.db"

    # Archivos de evidencias
    UPLOAD_DIR: str = "./uploads"
    MAX_UPLOAD_SIZE_MB: int = 15

    # --- Integración WhatsApp / Meta Cloud API (se activa cuando existan credenciales) ---
    WHATSAPP_ACCESS_TOKEN: str | None = None
    WHATSAPP_PHONE_NUMBER_ID: str | None = None
    WHATSAPP_BUSINESS_ACCOUNT_ID: str | None = None
    WHATSAPP_VERIFY_TOKEN: str | None = None
    WHATSAPP_API_VERSION: str = "v21.0"

    # --- Integración SINFA (sistema financiero/facturación) ---
    SINFA_API_URL: str | None = None
    SINFA_API_KEY: str | None = None
    SINFA_SYNC_MODE: str = "NONE"  # NONE | API | CSV | EXCEL | DB_READONLY

    # --- Integración GBS (inventario/compras) ---
    GBS_API_URL: str | None = None
    GBS_API_KEY: str | None = None
    GBS_SYNC_MODE: str = "NONE"  # NONE | API | CSV | EXCEL | DB_READONLY

    # Datos de prueba
    LOAD_DEMO_DATA: bool = True

    @property
    def whatsapp_configured(self) -> bool:
        return bool(
            self.WHATSAPP_ACCESS_TOKEN
            and self.WHATSAPP_PHONE_NUMBER_ID
            and self.WHATSAPP_VERIFY_TOKEN
        )

    @property
    def sinfa_configured(self) -> bool:
        return self.SINFA_SYNC_MODE != "NONE"

    @property
    def gbs_configured(self) -> bool:
        return self.GBS_SYNC_MODE != "NONE"


settings = Settings()
