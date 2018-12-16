from flask import Flask,render_template,request,redirect,session
import os
import base64

import psycopg2 as dbapi2
UPLOAD_FOLDER = '/static/'
app = Flask(__name__)
app.secret_key = "2C70E12B7A0646F92279F427C7B38E7334D8E5389CFF167A1DC30E73F826B683"
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


def imageToByte(image):
    return bytearray(base64.b64encode(image.read()))


def byteToImage(bytea):
    f = open("static/user_pp.png",'wb')
    f.write(base64.b64decode(bytea))
    f.close()



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


class Moderation:
    def __init__(self):
        connection = DatabaseConnection()
        url = os.getenv("DATABASE_URL")
        if url is None:
            url = 'postgres://itucs:itucspw@localhost:32768/itucsdb'
        connection.connect(url)
        self.connection = connection

    def add_attack(self):

        self.connection.run_statements(
            "INSERT INTO ATTACKS(DATE,CITY,TGROUP,ATYPE,ATARGET,FATALITIES,INJURIES) VALUES('{date}','{city}','{gname}','{attacktype}','{target}','{fatalities}','{injuries}') ON CONFLICT DO NOTHING" \
            .format(date=request.form["attack_date"], city=request.form["attack_city"],
                    gname=request.form["attack_tgroup"],
                    attacktype=request.form["attack_type"], target=request.form["attack_target"],
                    fatalities=request.form["attack_fatalities"], injuries=request.form["attack_injuries"]))
        self.connection.run_statements(
            "UPDATE CITIES SET TOTALA = TOTALA+1,TOTALF = TOTALF + {fatalities},TOTALI = TOTALI + {injuries} WHERE NAME = '{city}'" \
            .format(city=request.form["attack_city"], fatalities=request.form["attack_fatalities"],
                    injuries=request.form["attack_injuries"]))
        self.connection.run_statements(
            "UPDATE TGROUPS SET TOTALA = TOTALA+1,TOTALF = TOTALF + {fatalities},TOTALI = TOTALI + {injuries} WHERE NAME = '{gname}'" \
            .format(gname=request.form["attack_tgroup"], fatalities=request.form["attack_fatalities"],
                    injuries=request.form["attack_injuries"]))
        self.connection.commit()

    def delete_attack(self):

        city,fatalities,injuries,tgroup = self.connection.run_queries("SELECT city,fatalities,injuries,tgroup FROM ATTACKS where id={id};".format(id=request.form["attack_id"]))[0]
        self.connection.run_statements(
            "UPDATE CITIES SET TOTALA = TOTALA-1,TOTALF = TOTALF - {fatalities},TOTALI = TOTALI - {injuries} WHERE NAME = '{city}'" \
                .format(city=city, fatalities=fatalities,
                        injuries=injuries))
        self.connection.run_statements(
            "UPDATE TGROUPS SET TOTALA = TOTALA-1,TOTALF = TOTALF - {fatalities},TOTALI = TOTALI - {injuries} WHERE NAME = '{gname}'" \
                .format(gname=tgroup, fatalities=fatalities,
                        injuries=injuries))
        self.connection.run_statements(
            "DELETE FROM ATTACKS WHERE id='{id}'" \
                .format(id=request.form["attack_id"]))
        self.connection.commit()

    def update_attack(self):

        self.delete_attack()
        self.add_attack()

    def add_city(self):

        self.connection.run_statements("INSERT INTO CITIES(NAME) VALUES('{name}') ON CONFLICT DO NOTHING ".format(name=request.form['city_name']))
        self.connection.commit()

    def update_city(self):

        self.connection.run_statements("UPDATE CITIES SET name='{new_name}' WHERE name='{name}'".format(new_name=request.form["city_new_name"],name=request.form["city_name"]))
        self.connection.commit()

    def delete_city(self):
        attacks = self.connection.run_queries("SELECT tgroup,fatalities,injuries FROM ATTACKS WHERE city='{city}'".format(city=request.form['city_name']))
        for attack in attacks:
            tgroup,fatalities,injuries = attack
            self.connection.run_statements("UPDATE TGROUPS SET totala = totala-1, totalf = totalf - {fatalities}, totali = totali - {injuries} WHERE name = '{tgroup}'"
                                        .format(tgroup=tgroup,fatalities=fatalities,injuries=injuries))
            self.connection.run_statements("DELETE FROM CITIES WHERE name='{city}'".format(city=request.form["city_name"]))
        self.connection.commit()

    def add_tgroup(self):

        self.connection.run_statements("INSERT INTO TGROUPS(NAME) VALUES('{name}') ON CONFLICT DO NOTHING ".format(name=request.form['tgroup_name']))
        self.connection.commit()

    def update_tgroup(self):

        self.connection.run_statements("UPDATE TGROUPS SET name='{new_name}' WHERE name='{name}'".format(new_name=request.form["tgroup_new_name"],name=request.form["tgroup_name"]))
        self.connection.commit()

    def delete_tgroup(self):

        attacks = self.connection.run_queries(
            "SELECT city,fatalities,injuries FROM ATTACKS WHERE tgroup='{tgroup}'".format(tgroup=request.form['tgroup_name']))
        for attack in attacks:
            city, fatalities, injuries = attack
            self.connection.run_statements(
                "UPDATE CITIES SET totala = totala-1, totalf = totalf - {fatalities}, totali = totali - {injuries} WHERE name = '{city}'"
                .format(city=city, fatalities=fatalities, injuries=injuries))
            self.connection.run_statements(
                "DELETE FROM tgroups WHERE name='{tgroup}'".format(tgroup=request.form["tgroup_name"]))
        self.connection.commit()


@app.route("/",methods=['GET', 'POST'])
def home_page():
    connection = DatabaseConnection()
    url = os.getenv("DATABASE_URL")
    if url is None:
        url = 'postgres://itucs:itucspw@localhost:32768/itucsdb'
    connection.connect(url)
    if request.method == 'POST':
        content = request.form.get("contact")
        # Input validation to avoid injections
        if content is not None or "":
            content.replace("'", "")
            content.replace("(", "")
            content.replace(")", "")
            content.replace(";", "")
            connection.run_statements("INSERT INTO SUGGESTIONS(CONTENT) VALUES('{content}')".format(content=content))
            connection.commit()
        if request.form.get("action")=="Login":

            UserInfo = connection.run_queries(
                "SELECT * FROM USERS WHERE username='{username}' AND password='{password}'".format(
                    username=request.form.get("username"), password=request.form.get("password")))
            if UserInfo != []:
                userTuple = UserInfo[0]
                session["username"] = userTuple[0]
                session["password"] = userTuple[1]
                session["logged"] = True
                session["pp"] = None
            else:
                session["logged"] = False
        signFail = False
        if request.form.get("action")=="Sign up":

            UserInfo = connection.run_queries(
                "SELECT * FROM USERS WHERE username='{username}'".format(
                    username=request.form.get("username")))
            if UserInfo == []:
                username = request.form.get("username")
                password = request.form.get("password")
                unwanted = ["(", ")", ";"]
                for element in unwanted:
                    if element in username or element in password or username=="":
                        signFail = True
                if not signFail:
                    session["username"] = username
                    session["password"] = password
                    session["logged"] = True
                    session["pp"] = None
                    connection.run_statements("INSERT INTO USERS(username,password) VALUES('{username}','{password}')".format(username=username,password=password))
                    connection.commit()

        return render_template('index.html',logged=session["logged"],signFail = signFail)
    else:

        return render_template('index.html',signFail = False)


@app.route("/attacks")
def attacks_page():
    connection = DatabaseConnection()
    url = os.getenv("DATABASE_URL")
    if url is None:
        url = 'postgres://itucs:itucspw@localhost:32768/itucsdb'
    connection.connect(url)
    attacks = connection.run_queries("SELECT * FROM ATTACKS;")
    years = [""]
    for x in xrange(1970,2018):
        years.append(x)
    connection.close()
    return render_template('attacks.html',tuples=attacks,years=years)


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

    moderation = Moderation()

    # Add a new attack
    if request.form["action"] == "attack_add":

        moderation.add_attack()

    # Update an existing attack
    if request.form["action"] == "attack_update":

        moderation.update_attack()

    # Delete an attack
    if request.form["action"] == "attack_delete":

        moderation.delete_attack()

    # Add a new City
    if request.form["action"] == "cities_add":

        moderation.add_city()

    # Update an existing city
    if request.form["action"] == "cities_update":

        moderation.update_city()

    # Delete a city
    if request.form["action"] == "cities_delete":

        moderation.delete_city()

    if request.form["action"] == "tgroup_add":

        moderation.add_tgroup()

    if request.form["action"] == "tgroup_update":

        moderation.update_tgroup()

    if request.form["action"] == "tgroup_delete":

        moderation.delete_tgroup()

    connection = moderation.connection
    cities = connection.run_queries("SELECT name FROM CITIES")
    # Since there are changes the tables need to be updated after each moderation
    for c, in cities:
        # CATARGET
        connection.run_statements(
            "SELECT atarget, count(atarget) FROM attacks WHERE city = '{city}' GROUP BY atarget ORDER BY count DESC LIMIT 1".format(
                city=c))
        try:
            atarget, count = connection.cursor.fetchone()
            connection.run_statements(
                "UPDATE CITIES SET catarget = '{atarget}' WHERE name='{city}'".format(atarget=atarget, city=c))
        except TypeError:
            print("NOT A VALID QUERY WITH THE CITY:")
            print(c)

        # CATYPE
        try:
            connection.run_statements(
                "SELECT atype, count(atype) FROM attacks WHERE city = '{city}' GROUP BY atype ORDER BY count DESC LIMIT 1".format(
                    city=c))
            atype, count = connection.cursor.fetchone()
            connection.cursor.execute(("UPDATE CITIES SET catype = '{atype}' WHERE name='{city}'").format(atype=atype, city=c))
        except TypeError:
            print("NOT A VALID QUERY WITH THE CITY:")
            print(c)

    # CATARGET and CATYPE calculations for tgroups
    tgroups = connection.run_queries("SELECT name FROM TGROUPS")
    for t, in tgroups:
        # CATARGET
        try:
            connection.run_statements(
                "SELECT atarget, count(atarget) FROM attacks WHERE tgroup = '{gname}' GROUP BY atarget ORDER BY count DESC LIMIT 1".format(
                    gname=t))
            atarget, count = connection.cursor.fetchone()
            connection.run_statements(
                ("UPDATE TGROUPS SET catarget = '{atarget}' WHERE name='{gname}'").format(atarget=atarget, gname=t))
        except TypeError:
            print("NOT A VALID QUERY")

        # CATYPE
        try:
            connection.run_statements(
                "SELECT atype, count(atype) FROM attacks WHERE tgroup = '{gname}' GROUP BY atype ORDER BY count DESC LIMIT 1".format(
                    gname=t))
            atype, count = connection.cursor.fetchone()
            connection.run_statements(("UPDATE TGROUPS SET catype = '{atype}' WHERE name='{gname}'").format(atype=atype, gname=t))
        except TypeError:
            print("NOT A VALID QUERY")

    connection.commit()
    connection.close()
    return render_template('adminPost.html')


@app.route("/filter",methods=['POST'])
def filter_page():

    #  If we close the connection without committing we can filter our tables anyway we want and it will return to it's original state
    connection = DatabaseConnection()
    url = os.getenv("DATABASE_URL")
    if url is None:
        url = 'postgres://itucs:itucspw@localhost:32768/itucsdb'
    connection.connect(url)

    # Timespan Filter
    if request.form["timespan_start"] != "":
        connection.run_statements("DELETE FROM ATTACKS WHERE date<'{year}-01-01'".format(year=request.form["timespan_start"]))
    if request.form["timespan_end"] != "":
        connection.run_statements(
            "DELETE FROM ATTACKS WHERE date>'{year}-12-31'".format(year=request.form["timespan_end"]))

    # Extra Filters (we use .get as these are optional)

    if request.form.get("hide_unknown") == "1":
        connection.run_statements("DELETE FROM ATTACKS WHERE tgroup='Unknown'")
    if request.form.get("hide_failed") == "1":
        connection.run_statements("DELETE FROM ATTACKS WHERE fatalities=0 and injuries=0")

    # Ordering Filter
    attacks = connection.run_queries("SELECT * FROM ATTACKS ORDER BY {value} DESC".format(value=request.form["ordering"]))
    years = ['']

    for x in xrange(1970, 2018):
        years.append(x)
    return render_template('attacks.html',tuples=attacks,years=years)


@app.route("/profile",methods=['POST','GET'])
def profile_page():
    connection = DatabaseConnection()
    url = os.getenv("DATABASE_URL")
    if url is None:
        url = 'postgres://itucs:itucspw@localhost:32768/itucsdb'
    connection.connect(url)
    if request.method == 'POST':
        pic =request.files["profilePic"]
        if pic is None or pic.filename == '':
            return render_template("profile.html")
        b = imageToByte(pic)
        connection.run_statements("UPDATE USERS SET profilePic = '{BLOB}' WHERE username='{username}'".format(BLOB=b,username=session["username"]))
        connection.commit()
        byteToImage(b)
        session['image']= session['image']+1
        return render_template("profile.html")
    if request.method == 'GET':
        pic, = connection.run_queries("SELECT profilePic FROM USERS WHERE username='{username}'".format(username=session["username"]))
        session["hasPic"] = True
        if pic[0] is not None:
            byteToImage(pic[0])
            session["hasPic"] = True
            try:
                if session['image'] == 0:
                    session['image'] = session['image'] + 1
            except KeyError:
                session['image'] = 0
        return render_template("profile.html")


@app.route("/logout")
def logout_page():
    session["logged"] = False
    session["username"] = None
    session["password"] = None
    return redirect("/")


if __name__ == "__main__":
    app.run()


