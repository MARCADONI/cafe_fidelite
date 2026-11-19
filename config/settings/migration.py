
from .local import *
from .base import BASE_DIR


DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "migration_data" / "db_migration.sqlite3",
        "ATOMIC_REQUESTS": True,
    }
}
