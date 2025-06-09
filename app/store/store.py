from app.web.config import Config


class Store:
    def __init__(self, config: Config) -> None:
        from app.store.db.sqlalchemy_db import Database
        from app.store.library.repository import LibraryRepository

        self.config = config
        self.database = Database(self)
        self.library_repo = LibraryRepository(self)

