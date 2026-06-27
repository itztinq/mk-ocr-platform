from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase


class Database:
    client: AsyncIOMotorClient | None = None
    db: AsyncIOMotorDatabase | None = None
    _jobs_collection_name: str = "jobs"

    async def connect(self, uri: str, db_name: str, jobs_collection: str = "jobs") -> None:
        self.client = AsyncIOMotorClient(uri)
        self.db = self.client[db_name]
        self._jobs_collection_name = jobs_collection

    async def close(self) -> None:
        if self.client:
            self.client.close()
            self.client = None
            self.db = None

    def get_jobs_collection(self):
        if self.db is None:
            raise RuntimeError("Database not connected. Call connect() first.")
        return self.db[self._jobs_collection_name]

    def get_database(self) -> AsyncIOMotorDatabase:
        if self.db is None:
            raise RuntimeError("Database not connected. Call connect() first.")
        return self.db


db = Database()
