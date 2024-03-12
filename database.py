from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from config import DB_URL


engine = create_engine(DB_URL)


# def adapt_my_http_url(url: HttpUrl):
#     return AsIs(str(url))


# register_adapter(HttpUrl, adapt_my_http_url)

# adapter = adapt(HttpUrl('http://example.com'))

# # Check if the adapter is your custom adapter
# print(adapter.getquoted() == b"'http://example.com'")

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()
