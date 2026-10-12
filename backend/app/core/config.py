"""Application configuration loaded from environment variables."""

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    app_name: str = "AI Lead Generation API"
    version: str = "1.0.0"
    api_v1_prefix: str = "/api/v1"
    environment: str = "development"

    # Database: use a Neon (Postgres) URL in production, e.g.
    # postgresql+asyncpg://USER:PASSWORD@HOST/DB?ssl=require
    database_url: str = "sqlite+aiosqlite:///./leadgen.db"
    auto_create_tables: bool = True

    secret_key: str = "change-me-in-production"
    access_token_algorithm: str = "HS256"
    access_token_expire_minutes: int = 60 * 24
    cookie_name: str = "access_token"
    cookie_secure: bool = False
    cookie_samesite: str = "lax"
    cors_origins: list[str] = ["http://localhost:3000"]

    # LLM (Groq is OpenAI-compatible)
    llm_provider: str = "groq"
    groq_api_key: str | None = None
    groq_base_url: str = "https://api.groq.com/openai/v1"
    groq_model: str = "openai/gpt-oss-120b"
    llm_timeout_seconds: float = 30.0

    # Search / lead discovery provider ("mock" = offline sample, "serper" = live)
    search_provider: str = "mock"
    search_api_key: str | None = None
    search_base_url: str = "https://google.serper.dev"
    search_gl: str = "us"
    search_timeout_seconds: float = 20.0

    # Contact discovery (free): scrape the company website + Serper search.
    # Uses SEARCH_API_KEY when available; scraping needs no key.
    contact_finder_enabled: bool = True
    contact_finder_timeout_seconds: float = 12.0
    contact_finder_max_pages: int = 6
    contact_finder_user_agent: str = "Mozilla/5.0 (compatible; LeadGenBot/1.0)"

    # Email provider ("local" = record only, "resend" = live API, "smtp" = free SMTP)
    email_provider: str = "local"
    email_api_key: str | None = None
    email_base_url: str = "https://api.resend.com"
    email_from: str = "onboarding@resend.dev"
    email_from_name: str = "AI Lead Generation"
    email_timeout_seconds: float = 30.0

    # SMTP sending (Gmail App Password, Brevo, SMTP2GO, Zoho, ... all free tiers)
    smtp_host: str | None = None
    smtp_port: int = 587
    smtp_username: str | None = None
    smtp_password: str | None = None
    smtp_use_tls: bool = True
    smtp_use_ssl: bool = False

    # Email finder / contact enrichment ("hunter" | "enrich"; needs matching key)
    email_finder_provider: str = "hunter"
    hunter_api_key: str | None = None
    hunter_base_url: str = "https://api.hunter.io/v2"
    hunter_timeout_seconds: float = 20.0
    enrich_api_key: str | None = None
    enrich_base_url: str = "https://dev.enrich.so"
    enrich_timeout_seconds: float = 20.0

    crm_api_key: str | None = None

    embedding_dim: int = 1024

    page_size_default: int = 20
    page_size_max: int = 100

    @property
    def is_sqlite(self) -> bool:
        return self.database_url.startswith("sqlite")

    @property
    def llm_configured(self) -> bool:
        return bool(self.groq_api_key)

    @property
    def search_configured(self) -> bool:
        return self.search_provider == "serper" and bool(self.search_api_key)

    @property
    def email_configured(self) -> bool:
        if self.email_provider == "resend":
            return bool(self.email_api_key)
        if self.email_provider == "smtp":
            return bool(self.smtp_host and self.email_from)
        return False

    @property
    def contact_finder_configured(self) -> bool:
        return self.contact_finder_enabled

    @property
    def email_finder_configured(self) -> bool:
        if self.email_finder_provider == "hunter":
            return bool(self.hunter_api_key)
        if self.email_finder_provider == "enrich":
            return bool(self.enrich_api_key)
        return False


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
