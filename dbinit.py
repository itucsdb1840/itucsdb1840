import os
import sys

import psycopg2 as dbapi2


INIT_STATEMENTS = [
    "CREATE DOMAIN FATALITIES INTEGER CHECK (VALUE >=0)",
    "CREATE DOMAIN INJURIES  INTEGER CHECK (VALUE >=0)",
    "CREATE TABLE IF NOT EXISTS TGROUPS (ID SERIAL PRIMARY KEY,NAME VARCHAR(30),caTarget VARCHAR(15),catype VARCHAR(15),totala INTEGER,totali INTEGER,totalf INTEGER)",
    "CREATE TABLE IF NOT EXISTS CITIES(NAME VARCHAR(15) PRIMARY KEY,TOTALA INTEGER,TOTALF FATALITIES,TOTALI INJURIES,caTarget varchar(15))",
    "CREATE TABLE IF NOT EXISTS ATTACKS (ID SERIAL PRIMARY KEY,DATE DATE,CITY VARCHAR(15) REFERENCES CITIES(name),TGROUP INTEGER REFERENCES TGROUPS(id),atype VARCHAR(15),atarget VARCHAR(15),FATALITIES FATALITIES,INJURIES INJURIES)"]


def initialize(url):
    with dbapi2.connect(url) as connection:
        cursor = connection.cursor()
        for statement in INIT_STATEMENTS:
            cursor.execute(statement)
        cursor.close()


if __name__ == "__main__":
    url = os.getenv("DATABASE_URL")
    if url is None:
        print("Usage: DATABASE_URL=url python dbinit.py")
        sys.exit(1)
    initialize(url)
