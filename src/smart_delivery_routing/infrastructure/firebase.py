import firebase_admin
from firebase_admin import credentials

from smart_delivery_routing.config import FIREBASE_CREDENTIALS


def initialize_firebase() -> None:
    if firebase_admin._apps:
        return
    if not FIREBASE_CREDENTIALS:
        return
    cred = credentials.Certificate(FIREBASE_CREDENTIALS)
    firebase_admin.initialize_app(cred)
