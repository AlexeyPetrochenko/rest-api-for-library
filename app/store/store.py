from app.web.config import Config


class Store:
    def __init__(self, config: Config) -> None:
        from app.store.db.sqlalchemy_db import Database

        self.config = config
        self.database = Database(self)

