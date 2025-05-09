from database import db_client
from object_storage import os_client

class Resources:
    def __init__(self):
        self.db_client = db_client
        self.os_client = os_client

resources = Resources()
