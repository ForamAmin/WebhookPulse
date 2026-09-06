from src.providers.registry import ProviderRegistry
from src.providers.adapters.razorpay_adapter import RazorpayAdapter


provider_registry = ProviderRegistry()

provider_registry.register(
    "razorpay",
    RazorpayAdapter(),
)