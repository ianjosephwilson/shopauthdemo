import os
import logging

from dotenv import load_dotenv
from pyramid.config import Configurator
from sqlalchemy.orm import (
    sessionmaker,
)
from sqlalchemy import (
    create_engine,
)
import zope.sqlalchemy

from .model import Base


logger = logging.getLogger(__name__)


def get_tm_session(dbsession_factory, transaction_manager):
    """
    Get a ``sqlalchemy.orm.Session`` instance backed by a transaction.

    This function will hook the session to the transaction manager which
    will take care of committing any changes.

    - When using pyramid_tm it will automatically be committed or aborted
      depending on whether an exception is raised.

    - When using scripts you should wrap the session in a manager yourself.
      For example::

          import transaction

          engine = get_engine(settings)
          session_factory = get_session_factory(engine)
          with transaction.manager:
              dbsession = get_tm_session(session_factory, transaction.manager)

    """
    dbsession = dbsession_factory()
    zope.sqlalchemy.register(dbsession, transaction_manager=transaction_manager)
    return dbsession


def get_dbsession_factory(engine):
    return sessionmaker(engine, future=True)


def main():

    if not os.environ.get("DATABASE_URL", None):
        load_dotenv(os.path.join(os.path.dirname(os.path.dirname(__file__)), ".env"))

    db_url = os.environ.get("DATABASE_URL")
    engine = create_engine(db_url, echo=False)

    Base.metadata.create_all(engine, checkfirst=True)

    dbsession_factory = get_dbsession_factory(engine)

    def get_db(request):
        return get_tm_session(dbsession_factory, request.tm)

    with Configurator(settings={}) as config:
        config.include("pyramid_tm")
        config.add_request_method(get_db, "db", reify=True)
        config.include(".views")
        app = config.make_wsgi_app()
    return app
