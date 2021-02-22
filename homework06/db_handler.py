from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, String, Integer
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from news_parser import get_news
Base = declarative_base()
engine = create_engine("sqlite:///news.db")
session = sessionmaker(bind=engine)

class News(Base):
    __tablename__ = "news"
    id = Column(Integer, primary_key=True)
    title = Column(String)
    author = Column(String)
    url = Column(String)
    comments = Column(Integer)
    points = Column(Integer)
    label = Column(String)

Base.metadata.create_all(bind=engine)

s = session()
def upload_to_db(news_list:list):
    for post in news_list:
        if s.query.filter_by(title=post.get('title')) is None:
            news = News(title=post.get('title'),
                        author=post.get('author'),
                        url=post.get('url'),
                        comments=post.get('comments'),
                        points=post.get('points'))
            s.add(news)
    s.commit()

if __name__ == '__main__':
    news_list = get_news(1)
    upload_to_db(news_list)