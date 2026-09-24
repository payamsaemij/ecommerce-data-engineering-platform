import psycopg


DATABASE_URL = (
    "postgresql://ecommerce_user:123456"
    "@localhost:5432/ecommerce_db"
)


def get_connection():
    return psycopg.connect(DATABASE_URL)