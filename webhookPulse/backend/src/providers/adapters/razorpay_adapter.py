import hashlib
import hmac
import json

from src.providers.base import ProviderAdapter


class RazorpayAdapter(ProviderAdapter):

    def verify_signature(
        self,
        raw_body: bytes,
        headers: dict,
        secret: str,
    ) -> bool:

        signature = headers.get(
            "x-razorpay-signature"
        )

        if not signature:
            return False

        expected_signature = hmac.new(
            secret.encode(),
            raw_body,
            hashlib.sha256,
        ).hexdigest()

        return hmac.compare_digest(
            signature,
            expected_signature,
        )

    def get_event_id(
        self,
        raw_body: bytes,
        headers: dict,
        payload: dict,
    ) -> str | None:

        return headers.get(
            "x-razorpay-event-id"
        )

    def get_event_type(
        self,
        raw_body: bytes,
        headers: dict,
        payload: dict,
    ) -> str | None:

        return payload.get("event")

    def normalize_event(
        self,
        raw_body: bytes,
        headers: dict,
        payload: dict,
    ) -> dict:

        return {
            "provider": "razorpay",
            "provider_event_id": self.get_event_id(
                raw_body,
                headers,
                payload,
            ),
            "event_type": self.get_event_type(
                raw_body,
                headers,
                payload,
            ),
            "payload": payload,
        }