from flask import Flask,render_template,request,redirect
import os

import psycopg2 as dbapi2
app = Flask(__name__)


class DatabaseConnection:
    def __init__(self):
        self.cursor=None
        self.connection =None

    def run_statements(self,statements):
        if self.cursor is not None:
            self.cursor.execute(statements)
        else:
            print("Connection failed!\n")

    def run_queries(self,queries):
        if self.cursor is not None:
            self.cursor.execute(queries)
            return self.cursor.fetchall()
        else:
            print("Connection failed!\n")

    def connect(self,url):
        self.connection = dbapi2.connect(url)
        self.cursor = self.connection.cursor()

    def close(self):
        self.cursor.close()

    def commit(self):
        self.connection.commit()

@app.route("/")
def home_page():
    return render_template('index.html')


@app.route("/attacks")
def attacks_page():
    connection = DatabaseConnection()
    url = os.getenv("DATABASE_URL")
    if url is None:
        url = 'postgres://itucs:itucspw@localhost:32768/itucsdb'
    connection.connect(url)
    attacks = connection.run_queries("SELECT * FROM ATTACKS;")
    connection.close()
    return render_template('attacks.html',tuples=attacks)


@app.route("/cities")
def cities_page():
    connection = DatabaseConnection()
    url = os.getenv("DATABASE_URL")
    if url is None:
        url = 'postgres://itucs:itucspw@localhost:32768/itucsdb'
    connection.connect(url)
    cities = connection.run_queries("SELECT * FROM CITIES;")
    connection.close()
    return  render_template('cities.html',tuples=cities)


@app.route("/tgroups")
def tgroups_page():
    connection = DatabaseConnection()
    url = os.getenv("DATABASE_URL")
    if url is None:
        url = 'postgres://itucs:itucspw@localhost:32768/itucsdb'
    connection.connect(url)
    tgroups = connection.run_queries("SELECT * FROM TGROUPS;")
    connection.close()
    return render_template('tgroups.html',tuples=tgroups)


@app.route("/admin", methods=['GET', 'POST'])
def admin_page():
    if request.method== 'GET':
        return render_template('adminGet.html')
    if request.method == 'POST' and request.form['password']=="muazzam":
        return render_template('adminPost.html')


@app.route("/moderation",methods=['POST'])
def moderation_page():
    connection = DatabaseConnection()
    url = os.getenv("DATABASE_URL")
    if url is None:
        url = 'postgres://itucs:itucspw@localhost:32768/itucsdb'
    connection.connect(url)
    if request.form["action"] == "attack_add":
        connection.run_statements("INSERT INTO ATTACKS(DATE,CITY,TGROUP,ATYPE,ATARGET,FATALITIES,INJURIES) VALUES('{date}','{city}','{gname}','{attacktype}','{target}','{fatalities}','{injuries}') ON CONFLICT DO NOTHING"\
            .format(date=request.form["attack_date"],city=request.form["attack_city"],gname=request.form["attack_tgroup"],
                    attacktype=request.form["attack_type"],target=request.form["attack_target"],fatalities =request.form["attack_fatalities"],injuries=request.form["attack_injuries"]))
    if request.form["action"] == "attack_update":
        connection.run_statements(
            "UPDATE ATTACKS SET date={date} city={city} tgroup={gname} atype={attacktype} atarget={target} fatalities={fatalities} injuries={injuries} WHERE id='{id}'" \
            .format(id=request.form["attack_id"],date=request.form["attack_date"], city=request.form["attack_city"],
                    gname=request.form["attack_tgroup"],
                    attacktype=request.form["attack_type"], target=request.form["attack_target"],
                    fatalities=request.form["attack_fatalities"], injuries=request.form["attack_injuries"]))
    if request.form["action"] == "attack_delete":
        print ("FOUND THE ATTACK WITH THE ID: {a}".format(a=connection.run_queries("SELECT * FROM ATTACKS WHERE id='{id}'".format(id=request.form["attack_id"]))))
        connection.run_statements(
            "DELETE FROM ATTACKS WHERE id='{id}'" \
            .format(id=request.form["attack_id"]))
        print("l/ATTACK DELETE OPERATION\n")
    if request.form["action"] == "cities_add":
        print('NOT IMPLEMENTED')
    if request.form["action"] == "cities_update":
        print('NOT IMPLEMENTED')
    if request.form["action"] == "cities_delete":
        print('NOT IMPLEMENTED')
    if request.form["action"] == "tgroup_add":
        print('NOT IMPLEMENTED')
    if request.form["action"] == "tgroup_update":
        print('NOT IMPLEMENTED')
    if request.form["action"] == "tgroup_delete":
        print('NOT IMPLEMENTED')
    connection.commit()
    connection.close()
    return render_template('adminPost.html')


if __name__ == "__main__":
    app.run()


