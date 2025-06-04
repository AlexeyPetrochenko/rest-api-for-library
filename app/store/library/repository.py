import typing

if typing.TYPE_CHECKING:
    from app.store.store import Store

class LibraryRepository:
    def __init__(self, store: "Store") -> None:
        self.store = store

