from generator.helpers import generate_id


def create_order_event(invoice):
    return {
        "event_id": generate_id("EVT"),
        "event_type": "order_created",
        "event_version": 1,
        "occurred_at": invoice["created_at"],
        "source": "ecommerce-generator",
        "customer_id": invoice["customer"]["customer_id"],
        "order_id": invoice["order_id"],
        "data": {
            "currency": invoice["currency"],
            "customer": invoice["customer"],
            "items": invoice["items"],
            "pricing": invoice["pricing"],
            "payment": invoice["payment"],
            "order_status": invoice["order_status"],
},
    }