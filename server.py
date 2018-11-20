from flask import Flask,render_template
import os
import sys

import psycopg2 as dbapi2

app = Flask(__name__)


class DatabaseConnection:
    def __init__(self,url):
        self.cursor = dbapi2.connect(url).cursor()

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

    def close(self):
        self.cursor.close()


@app.route("/")
def home_page():
    return "Hello, world!"


@app.route("/attacks")
def attacks_page():
    url = os.getenv("DATABASE_URL")
    connection = DatabaseConnection(url)
    attacks = connection.run_queries("SELECT * FROM ATTACKS;")
    connection.close()
    return render_template('attacks.html',attacks=attacks)


if __name__ == "__main__":
    app.run()

    if url is None:
        print("Failed connection to database\n")
        sys.exit(1)
    attacks_page(dbc)


