from flask import Flask,render_template
import os

import psycopg2 as dbapi2
app = Flask(__name__)


class DatabaseConnection:
    def __init__(self):
        self.cursor=None

    def run_statements(self,statements):
        if self.cursor is not None:
            self.cursor.execute(statements)
        else:
            print("Connection is None!\n")

    def run_queries(self,queries):
        if self.cursor is not None:
            self.cursor.execute(queries)
            return self.cursor.fetchall()
        else:
            print("Connection is None!\n")

    def connect(self,url):
        self.cursor = dbapi2.connect(url).cursor()

    def close(self):
        self.cursor.close()


@app.route("/")
def home_page():
    return render_template('index.html')


@app.route("/attacks")
def attacks_page():
    connection = DatabaseConnection()
    url = os.getenv("DATABASE_URL")
    connection.connect(url)
    attacks = connection.run_queries("SELECT * FROM ATTACKS;")
    connection.close()
    return render_template('attacks.html',tuples=attacks)


@app.route("/cities")
def cities_page():
    connection = DatabaseConnection()
    url = os.getenv("DATABASE_URL")
    connection.connect(url)
    cities = connection.run_queries("SELECT * FROM CITIES;")
    connection.close()
    return  render_template('cities.html',tuples=cities)


@app.route("/tgroups")
def tgroups_page():
    connection = DatabaseConnection()
    url = os.getenv("DATABASE_URL")
    connection.connect(url)
    tgroups = connection.run_queries("SELECT * FROM TGROUPS;")
    connection.close()
    return render_template('tgroups.html',tuples=tgroups)


if __name__ == "__main__":
    app.run()


