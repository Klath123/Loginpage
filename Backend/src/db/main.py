from pymongo.mongo_client import MongoClient,CodecOptions
from src.config import Config
from datetime import datetime, timedelta, timezone

codec_options = CodecOptions(tz_aware=True, tzinfo= timezone.utc)
uri = Config.DATABASE_URL

client = MongoClient(uri)

db = client["auth"]

collection = db.get_collection("users", codec_options=codec_options)

collection.create_index(
    [("email", 1)],
    unique=True,
)

try:
    client.admin.command('ping')
    print("Pinged your deployment. You successfully connected to MongoDB!")
except Exception as e:
    print(e)