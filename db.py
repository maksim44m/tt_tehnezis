from typing import List, Tuple

from pandas import DataFrame
from sqlalchemy import Column, Integer, create_engine, String, DECIMAL, text
from sqlalchemy.orm import DeclarativeBase, sessionmaker

from config import DB_URL


class Base(DeclarativeBase):
    pass


class ParsingData(Base):
    __tablename__ = "parsing_data"

    id = Column(Integer, primary_key=True)
    title = Column(String, nullable=False)
    url = Column(String, nullable=False)
    xpath = Column(String, nullable=False)
    avg_price = Column(DECIMAL, nullable=True)

    def __repr__(self) -> str:
        return (f'{self.__class__.__name__}'
                f'(id={self.id!r}, '
                f'title={self.title!r}, '
                f'url={self.url!r}, '
                f'xpath={self.xpath}!r)')


# синхронная работа бд, чтобы избежать проблем с sqlite
engine = create_engine(DB_URL)

Base.metadata.create_all(engine)

Session = sessionmaker(bind=engine)


def save_to_db(data: DataFrame):
    with Session() as session:
        with session.begin():
            for row in data.itertuples():
                session.execute(
                    text("""INSERT INTO parsing_data(title, url, xpath)
                            VALUES(:title, :url, :xpath)"""),
                    {'title': row[1], 'url': row[2], 'xpath': row[3]}
                )


def get_all_id_url_xpath() -> Tuple[Tuple[int, str, str], ...]:
    with Session() as session:
        with session.begin():
            data = session.execute(
                text("""SELECT id, url, xpath
                        FROM parsing_data""")
            )
    return tuple(data.tuples())


def update_avg_price(data: Tuple[Tuple[int, float]]):
    with Session() as session:
        with session.begin():
            for row in data:
                session.execute(
                    text("""UPDATE parsing_data
                            SET avg_price = :avg_price
                            WHERE id = :id_"""),
                    {'id_': row[0], 'avg_price': row[1]}
                )


def get_all_title_avg_price() -> Tuple[Tuple[str, str], ...]:
    with Session() as session:
        with session.begin():
            data = session.execute(
                text("""SELECT title, avg_price
                        FROM parsing_data""")
            )
    return tuple(data.tuples())
