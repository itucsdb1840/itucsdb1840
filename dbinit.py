import os
import sys

import psycopg2 as dbapi2
# noinspection PyPackageRequirements
import pandas as pd


INIT_STATEMENTS = [
    "CREATE TABLE IF NOT EXISTS TGROUPS (NAME VARCHAR(100) PRIMARY KEY,caTarget VARCHAR(100),catype VARCHAR(100),totala INTEGER,totali INTEGER,totalf INTEGER)",
    "CREATE TABLE IF NOT EXISTS CITIES(NAME VARCHAR(30) PRIMARY KEY,TOTALA INTEGER,TOTALF INTEGER,TOTALI INTEGER,caTarget varchar(100))",
    "CREATE TABLE IF NOT EXISTS ATTACKS (ID SERIAL PRIMARY KEY,DATE DATE,CITY VARCHAR(30) REFERENCES CITIES(name),TGROUP VARCHAR(100) REFERENCES TGROUPS(name),atype VARCHAR(100),atarget VARCHAR(100),FATALITIES INTEGER,INJURIES INTEGER)"
]


def initialize(url):
    with dbapi2.connect(url) as connection:
        cursor = connection.cursor()
        for statement in INIT_STATEMENTS:
            cursor.execute(statement)
        cursor.close()


if __name__ == "__main__":
    url = 'postgres://itucs:itucspw@localhost:32768/itucsdb' #Temporary static url for testing purposes
    if url is None:
        print("Usage: DATABASE_URL=url python dbinit.py")
        sys.exit(1)
    data_cols = [1, 2, 3, 11,29, 35, 58, 98, 101]  # Necessary data columns
    df = pd.read_csv('./data.csv', error_bad_lines=False, encoding='ISO-8859-1', usecols=data_cols,na_values="",
                     dtype=str)  # This will read the data columns specified in data_cols and fill null values with UNKOWN
    data = df.rename(columns={'iyear': 'year', 'imonth': 'month', 'iday': 'day','provstate':'city', 'attacktype1_txt': "attacktype",
                              'targtype1_txt': 'target', 'nkill': 'fatalities', 'nwound': 'injuries'})

    # Filling the attacks table
    for i,row in data.iterrows():
        date = "{year}-{month}-{day}".format(year=row['year'],month=row['month'],day=row['day'])
        # Had to check like this to avoid values getting converted to nan
        f = str(row['fatalities']).replace("nan","-1")  # 0 was error prone because of string formatting im going to change -1 to 0 when working with the value
        inj = str(row['injuries']).replace("nan","-1")  # 0 was error prone because of string formatting im going to change -1 to 0 when working with the value
        statement1 = "INSERT INTO CITIES(NAME) VALUES('{name}') ON CONFLICT DO NOTHING ".format(name=row['city'])  # Make sure the referenced city exists
        INIT_STATEMENTS.append(statement1)
        statement2 = "INSERT INTO TGROUPS(NAME) VALUES('{name}') ON CONFLICT DO NOTHING".format(name=row['gname'])  # Make sure the referenced group exists
        INIT_STATEMENTS.append(statement2)
        statement3 = "INSERT INTO ATTACKS(DATE,CITY,TGROUP,ATYPE,ATARGET,FATALITIES,INJURIES) VALUES('{date}','{city}','{gname}','{attacktype}','{target}','{fatalities}','{injuries}') ON CONFLICT DO NOTHING"\
            .format(date=date,city=row['city'],gname=row['gname'],attacktype=row['attacktype'],target=row['target'],fatalities =f,injuries=inj)
        INIT_STATEMENTS.append(statement3)
    initialize(url)
