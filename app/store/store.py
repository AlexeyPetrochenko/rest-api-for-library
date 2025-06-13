from app.web.config import Config


class Store:
    def __init__(self, config: Config) -> None:
        from app.admin.repository import AdminRepository
        from app.library.repository import LibraryRepository
        from app.store.db.sqlalchemy_db import Database

        self.config = config
        self.database = Database(self)
        self.library_repo = LibraryRepository(self)
        self.admin_repo = AdminRepository(self)


