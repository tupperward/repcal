"""Database operations for repcal."""
from sqlalchemy import create_engine, text
from sqlalchemy.orm import Session
from unidecode import unidecode
from .models import RepublicanDate
from .utils import ordinal


def get_database_engine(db_path: str):
    """Create and return a SQLAlchemy engine for the calendar database.

    Args:
        db_path: SQLAlchemy database URI (e.g., 'sqlite+pysqlite:///path/to/calendar.db')

    Returns:
        SQLAlchemy Engine instance
    """
    return create_engine(db_path)


def carpe_diem(time, engine):
    """Seize the day. Create a RepublicanDate and then queries the calendar.db to add the natural details.

    Args:
        time: datetime object representing the date to convert
        engine: SQLAlchemy engine connected to calendar.db

    Returns:
        RepublicanDate object enriched with calendar item information
    """
    today = RepublicanDate(time)
    if today.month == None:
        today.month = "Sansculottides"
    statement = 'SELECT id, month_of, item, item_url FROM calendar WHERE day == {} AND month LIKE "{}"'.format(today.day,unidecode(today.month))
    with Session(engine) as session:
        query = session.execute(text(statement)).fetchone()
    today.id = query.id
    today.month_of = query.month_of
    today.item = query.item
    today.item_url = query.item_url
    today.image = today.item.lower().replace('the ','').replace(' ','_').replace('-','_')
    today.ordinal = ordinal(today.day)

    return today
