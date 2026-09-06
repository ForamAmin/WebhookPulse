from src.providers.base import ProviderAdapter


class ProviderRegistry:

    def __init__(self):
        self._adapters: dict[str, ProviderAdapter] = {}

    def register(
        self,
        provider: str,
        adapter: ProviderAdapter,
    ):
        self._adapters[provider.lower()] = adapter

    def get(
        self,
        provider: str,
    ) -> ProviderAdapter:

        adapter = self._adapters.get(provider.lower())

        if not adapter:
            raise ValueError(
                f"Unsupported provider: {provider}"
            )

        return adapter