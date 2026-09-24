import uuid
import random

from ..data.customers import FIRST_NAMES, LAST_NAMES
from ..data.locations import CITIES


def generate_id(prefix):
    return f"{prefix}-{uuid.uuid4().hex[:10].upper()}"


def random_customer():

    first_name = random.choice(FIRST_NAMES)
    last_name = random.choice(LAST_NAMES)

    city, postcode = random.choice(CITIES)

    unique_email = (
        f"{first_name.lower()}."
        f"{last_name.lower()}."
        f"{uuid.uuid4().hex[:8].lower()}"
        f"@example.com"
    )

    return {
        "customer_id": generate_id("CUS"),

        "first_name": first_name,

        "last_name": last_name,

        "email": unique_email,

        "shipping_address": {
            "city": city,
            "postcode": postcode,
            "country": "UK"
        }
    }