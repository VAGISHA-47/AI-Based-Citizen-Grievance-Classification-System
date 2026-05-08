from motor.motor_asyncio import AsyncIOMotorClient

from app.config import settings

client = AsyncIOMotorClient(settings.MONGO_URI)
db = client.get_default_database()
grievances_collection = db["grievances"]
