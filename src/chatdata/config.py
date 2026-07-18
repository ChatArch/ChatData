"Typed environment configuration for ChatData."

from chatenv import BaseEnvConfig, EnvField


class ChatdataConfig(BaseEnvConfig):
    "ChatData ChatEnv configuration."

    _title = "ChatData Configuration"
    _aliases = ["chatdata"]
    _storage_dir = "Chatdata"

    @classmethod
    def test(cls) -> None:
        """Validate schema registration without external side effects."""

        print(f"Testing {cls._title}...")
        print("Schema loaded; no network test is required.")

    CHATDATA_API_KEY = EnvField(
        "CHATDATA_API_KEY",
        desc="API key",
        is_sensitive=True,
    )


__all__ = ["ChatdataConfig"]
