from flask import Flask,render_template
import os
import sys

import psycopg2 as dbapi2

app = Flask(__name__)

class DatabaseConnection:
    def __init__(self,url):
        self.cursor = dbapi2.connect(url).cursor()
    def runStatements(self,statements):
        self.cursor.execute(statements)

@app.route("/")
def home_page():
    return "Hello, world!"
@app.route("/attacks")
def attacks_page(connection=None):
    attacks = connection.runStatements("SELECT * FROM ATTACKS")
    return render_template('attacks.html',attacks=attacks)


if __name__ == "__main__":

    url = os.getenv("DATABASE_URL")
    DBC = DatabaseConnection()
    if url is None:
        print("Failed connection to database")
        sys.exit(1)
    attacks_page(DBC)
    app.run()


