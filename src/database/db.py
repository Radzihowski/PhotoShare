import contextlib
from src.conf.config import settings

from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

PSQL_ASYNC_DB_URI = settings.sqlalchemy_database_url
class DatabaseSessionManager:
    def __init__(self, url: str):
        """
        The __init__ function is called when the class is instantiated.
        It sets up the database connection and sessionmaker, which will be used for all queries.

        :param self: Represent the instance of the class
        :param url: str: Create the engine
        :return: A new instance of the class
        :doc-author: Trelent
        """
        self._engine: AsyncEngine | None = create_async_engine(
            url,
            echo=False,
            pool_size=20,  # Set the pool size (max number of connections)
            max_overflow=40,  # Set the maximum number of connections that can exceed the pool_size
            pool_timeout=60,  # Timeout in seconds for getting a connection from the pool
            pool_recycle=1800,  # Time in seconds to recycle a connection (close and reopen)
            pool_pre_ping=True,
        )
        self._session_maker: async_sessionmaker = async_sessionmaker(
            autoflush=False, autocommit=False, bind=self._engine
        )

    @contextlib.asynccontextmanager
    async def session(self):
        """
        The session function is a coroutine that returns an async context manager.
        The context manager yields a session, and then closes it when the block ends.
        If there's an exception in the block, it rolls back any uncommitted changes to the database.

        :param self: Represent the instance of the class
        :return: A context manager, which is an object that has __enter__ and __exit__ methods
        :doc-author: Babenko Vladyslav
        """
        if self._session_maker is None:
            raise Exception("Session is not initialized")
        session = self._session_maker()
        try:
            yield session
        except SQLAlchemyError as err:  # SQLAlchemyError
            print(f"Database error: {err}")
            await session.rollback()
        finally:
            await session.close()


sessionmanager = DatabaseSessionManager(PSQL_ASYNC_DB_URI)


async def get_async_session():
    """
    The get_async_session function is a coroutine that returns an open database session.
    It will run the async with block, which ensures that the session will be closed when we are done with it.
    The yield from expression is similar to return in that it gives a value back to the caller of this function;
    the difference is that yield from delegates to another generator.

    :return: A context manager that can be used to interact with the database
    :doc-author: Babenko Vladyslav
    """
    async with sessionmanager.session() as session:
        yield session
