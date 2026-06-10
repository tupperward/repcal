import os, pytz
from repcal import RepublicanDate as rd
from datetime import datetime
from unidecode import unidecode
from sqlalchemy import create_engine, MetaData, text
from sqlalchemy.orm import Session
from atproto import Client, client_utils, models

db_path = os.environ.get('DB_PATH', 'calendar.db')
engine = create_engine(f"sqlite+pysqlite:///{db_path}")
meta = MetaData()

with engine.connect() as conn:
    conn.execute(text("""
        CREATE TABLE IF NOT EXISTS posts (
            gregorian_date TEXT PRIMARY KEY,
            at_uri TEXT,
            bsky_post_uri TEXT
        )
    """))
    conn.commit()


class RepublicanDate():
    def __init__(self, time):
        rd_date = rd.from_gregorian(time.date())
        self.day = rd.get_day(rd_date)
        self.weekday = rd.get_weekday(rd_date)
        self.month = rd.get_month(rd_date)
        self.year_arabic = rd.get_year_arabic(rd_date)
        self.year_roman = rd.get_year_roman(rd_date)
        self.week = rd.get_week_number(rd_date)
        self.month_of = None
        self.item = None
        self.item_url = None
        self.is_sansculottides = rd.is_sansculottides(rd_date)


def carpe_diem(time):
    today = RepublicanDate(time)
    ordinal = lambda n: f"{n}{['th', 'st', 'nd', 'rd'][((n//10%10!=1)*(n%10<4)*n%10)::4][0]}"
    if today.month == None:
        today.month = "Sansculottides"
    statement = 'SELECT id, month_of, item, item_url FROM calendar WHERE day == {} AND month LIKE "{}"'.format(today.day, unidecode(today.month))
    with Session(engine) as session:
        query = session.execute(text(statement)).fetchone()
    today.id = query.id
    today.month_of = query.month_of
    today.item = query.item
    today.item_url = query.item_url
    today.image = today.item.lower().replace('the ', '').replace(' ', '_').replace('-', '_')
    today.ordinal = ordinal(today.day)
    return today


def post_to_bsky(now):
    today = carpe_diem(now)
    handle = os.environ.get('BSKY_HANDLE')
    password = os.environ.get('BSKY_PASS')
    site_url = os.environ.get('SITE_URL')
    publication_uri = os.environ.get('BSKY_PUBLICATION_URI')

    gregorian_date = now.strftime("%Y-%m-%d")
    page_url = f"{site_url}/gregorian_date/{gregorian_date}"

    image_path = f"/images/{today.image}.jpg"
    alt_text = f"An old time-y illustration of a {today.item}."
    caption = (
        f"Today is {today.weekday.capitalize()} the {today.ordinal} of {today.month} "
        f"in the year {today.year_arabic}.\n"
        f"{today.month} is the month of {today.month_of.lower()}.\n"
        f"Today we celebrate {today.item.lower()}."
    )

    client = Client(base_url=os.environ.get('BSKY_PDS'))
    client.login(handle, password)

    doc_response = client.com.atproto.repo.create_record(
        models.ComAtprotoRepoCreateRecord.Data(
            repo=client.me.did,
            collection="site.standard.document",
            record={
                "$type": "site.standard.document",
                "site": publication_uri,
                "title": f"{today.weekday.capitalize()} the {today.ordinal} of {today.month}, Year {today.year_arabic}",
                "path": f"/gregorian_date/{gregorian_date}",
                "description": f"{today.month} is the month of {today.month_of.lower()}. Today we celebrate {today.item.lower()}.",
                "publishedAt": now.isoformat(),
                "textContent": caption,
            }
        )
    )
    at_uri = doc_response.uri

    text_builder = client_utils.TextBuilder()
    text_builder.text(caption)
    text_builder.tag(text=" #JacobinDay ", tag="JacobinDay")
    text_builder.link(f"\n\nSee today's page", page_url)

    with open(image_path, 'rb') as f:
        img_data = f.read()

    bsky_response = client.send_image(text=text_builder, image=img_data, image_alt=alt_text)
    bsky_post_uri = bsky_response.uri

    with Session(engine) as session:
        session.execute(
            text("INSERT OR REPLACE INTO posts (gregorian_date, at_uri, bsky_post_uri) VALUES (:date, :at_uri, :bsky_uri)"),
            {"date": gregorian_date, "at_uri": at_uri, "bsky_uri": bsky_post_uri}
        )
        session.commit()

    return True


if __name__ == "__main__":
    paris_timezone = pytz.timezone('Europe/Paris')
    timestamp = datetime.now(paris_timezone)
    response = post_to_bsky(timestamp)
    print(response)
