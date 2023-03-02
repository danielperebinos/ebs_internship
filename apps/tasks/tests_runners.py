import os

from decouple import config
from django.test.runner import DiscoverRunner
from mongoengine import connect, disconnect, get_db
from django.conf import settings


class CustomTestRunner(DiscoverRunner):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def setup_databases(self, **kwargs):
        disconnect()
        connect(db=settings.MONGO_TEST_NAME, host=settings.MONGO_TEST_DATABASE_HOST)
        return super().setup_databases(**kwargs)

    def teardown_databases(self, old_config, **kwargs):
        if old_config is not None:
            super().teardown_databases(old_config, **kwargs)

        db = get_db()
        collections = db.list_collection_names()
        for name in collections:
            db.drop_collection(name)
        disconnect()

