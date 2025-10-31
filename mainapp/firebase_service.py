import os
from functools import lru_cache

import firebase_admin
from firebase_admin import credentials, firestore


@lru_cache(maxsize=1)
def get_db():
    """
    Returns a cached Firestore client.

    Configure credentials using one of:
    - FIREBASE_SERVICE_ACCOUNT_JSON=/path/to/serviceAccountKey.json
    - GOOGLE_APPLICATION_CREDENTIALS=/path/to/serviceAccountKey.json
    """
    if not firebase_admin._apps:
        service_account = os.environ.get("FIREBASE_SERVICE_ACCOUNT_JSON")
        if service_account:
            cred = credentials.Certificate(service_account)
        else:
            cred = credentials.ApplicationDefault()
        firebase_admin.initialize_app(cred)
    return firestore.client()