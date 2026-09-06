from abc import ABC, abstractmethod


class ProviderAdapter(ABC):

    @abstractmethod
    def verify_signature(
        self,
        raw_body: bytes,
        headers: dict,
        secret: str,
    ) -> bool:
        pass

    @abstractmethod
    def get_event_id(
        self,
        raw_body: bytes,
        headers: dict,
        payload: dict,
    ) -> str | None:
        pass

    @abstractmethod
    def get_event_type(
        self,
        raw_body: bytes,
        headers: dict,
        payload: dict,
    ) -> str | None:
        pass

    @abstractmethod
    def normalize_event(
        self,
        raw_body: bytes,
        headers: dict,
        payload: dict,
    ) -> dict:
        pass