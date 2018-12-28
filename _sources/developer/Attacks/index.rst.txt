.. ITUCSDB1840 documentation master file, created as a template.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Attacks Table
===============

Create
-------

**Attacks table is created in dbinit.py by adding the following statement to the init_statements list**



      "CREATE TABLE IF NOT EXISTS ATTACKS (ID SERIAL PRIMARY KEY,DATE DATE,CITY VARCHAR(30) REFERENCES CITIES(name) ON UPDATE CASCADE ON DELETE CASCADE,TGROUP VARCHAR(100) REFERENCES TGROUPS(name) ON UPDATE CASCADE ON DELETE CASCADE,atype VARCHAR(100),atarget VARCHAR(100),FATALITIES INTEGER,INJURIES INTEGER)"

Notice that we have ON DELETE CASCADE and ON UPDATE CASCADE for our foreign keys.

Add
----

**Adding an attack is handled in the add_attack() function of the Moderation Class**


   .. code-block:: python

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

When adding an attack, first the attack is inserted into the attacks table. Then the city the attack was made in and the tgroup that made the attack gets updated.

Read
----

**Reading an attack happens in /attacks page**

   .. code-block:: python
      @app.route("/attacks")
      def attacks_page():
          connection = DatabaseConnection()
          url = os.getenv("DATABASE_URL")
          if url is None:
              url = 'postgres://itucs:itucspw@localhost:32768/itucsdb'
          connection.connect(url)
          attacks = connection.run_queries("SELECT * FROM ATTACKS;")
          years = [""]
          for x in range(1970,2018):
              years.append(x)
          connection.close()
          return render_template('attacks.html',tuples=attacks,years=years)

A connection to the database is established and the attacks are queried.Then a year range to display in the timespan filtering is passed to the template as parameters.
Update
------

**Updating an attack is handled in the update_attack() function of the Moderation Class**


   .. code-block:: python

       def update_attack(self):

           city, fatalities, injuries, tgroup = self.connection.run_queries(
               "SELECT city,fatalities,injuries,tgroup FROM ATTACKS where id={id};".format(id=request.form["attack_id"]))[
               0]
           difference_fatalities = fatalities - int(request.form["attack_fatalities"])
           difference_injuries = injuries - int(request.form["attack_injuries"])
           if city == request.form["attack_city"] and tgroup == request.form["attack_tgroup"]:
               self.connection.run_statements(
                   "UPDATE CITIES SET TOTALF = TOTALF - {fatalities},TOTALI =  TOTALI - {injuries}  WHERE NAME = '{city}'" \
                       .format(fatalities=difference_fatalities, injuries = difference_injuries,city = city))
               self.connection.run_statements(
                   "UPDATE TGROUPS SET TOTALF = TOTALF - {fatalities},TOTALI =  TOTALI - {injuries}  WHERE NAME = '{tgroup}'" \
                       .format(fatalities=difference_fatalities, injuries=difference_injuries, tgroup=tgroup))
           if city != request.form["attack_city"] and tgroup == request.form["attack_tgroup"]:
               self.connection.run_statements(
                   "UPDATE CITIES SET TOTALA = TOTALA-1,TOTALF = TOTALF - {fatalities},TOTALI =  TOTALI - {injuries}  WHERE NAME = '{city}'" \
                       .format(fatalities=fatalities, injuries=injuries, city=city))
               self.connection.run_statements(
                   "UPDATE CITIES SET TOTALA = TOTALA+1,TOTALF = TOTALF + {fatalities},TOTALI =  TOTALI + {injuries}  WHERE NAME = '{city}'" \
                       .format(fatalities=request.form["attack_fatalities"], injuries=request.form["attack_injuries"], city=request.form["attack_city"]))
               self.connection.run_statements(
                   "UPDATE TGROUPS SET TOTALF = TOTALF - {fatalities},TOTALI =  TOTALI - {injuries}  WHERE NAME = '{tgroup}'" \
                       .format(fatalities=difference_fatalities, injuries=difference_injuries, tgroup=tgroup))
           if city == request.form["attack_city"] and tgroup != request.form["attack_tgroup"]:
               self.connection.run_statements(
                   "UPDATE TGROUPS SET TOTALA = TOTALA-1,TOTALF = TOTALF - {fatalities},TOTALI =  TOTALI - {injuries}  WHERE NAME = '{tgroup}'" \
                       .format(fatalities=fatalities, injuries=injuries, tgroup=tgroup))
               self.connection.run_statements(
                   "UPDATE TGROUPS SET TOTALA = TOTALA+1,TOTALF = TOTALF + {fatalities},TOTALI =  TOTALI + {injuries}  WHERE NAME = '{tgroup}'" \
                       .format(fatalities=request.form["attack_fatalities"], injuries=request.form["attack_injuries"], tgroup=request.form["attack_tgroup"]))
               self.connection.run_statements(
                   "UPDATE CITIES SET TOTALF = TOTALF - {fatalities},TOTALI =  TOTALI - {injuries}  WHERE NAME = '{city}'" \
                       .format(fatalities=difference_fatalities, injuries=difference_injuries, city=city))
           if city != request.form["attack_city"] and tgroup != request.form["attack_tgroup"]:
               self.connection.run_statements(
                   "UPDATE CITIES SET TOTALA = TOTALA-1,TOTALF = TOTALF - {fatalities},TOTALI =  TOTALI - {injuries}  WHERE NAME = '{city}'" \
                       .format(fatalities=fatalities, injuries=injuries, city=city))
               self.connection.run_statements(
                   "UPDATE CITIES SET TOTALA = TOTALA+1,TOTALF = TOTALF + {fatalities},TOTALI =  TOTALI + {injuries}  WHERE NAME = '{city}'" \
                       .format(fatalities=request.form["attack_fatalities"], injuries=request.form["attack_injuries"],
                               city=request.form["attack_city"]))
               self.connection.run_statements(
                   "UPDATE TGROUPS SET TOTALA = TOTALA-1,TOTALF = TOTALF - {fatalities},TOTALI =  TOTALI - {injuries}  WHERE NAME = '{tgroup}'" \
                       .format(fatalities=fatalities, injuries=injuries, tgroup=tgroup))
               self.connection.run_statements(
                   "UPDATE TGROUPS SET TOTALA = TOTALA+1,TOTALF = TOTALF + {fatalities},TOTALI =  TOTALI + {injuries}  WHERE NAME = '{tgroup}'" \
                       .format(fatalities=request.form["attack_fatalities"], injuries=request.form["attack_injuries"],
                               tgroup=request.form["attack_tgroup"]))
           self.connection.run_statements("UPDATE ATTACKS SET date='{date}',city='{city}',tgroup='{tgroup}',atype='{atype}',atarget='{atarget}',fatalities='{fatalities}',injuries='{injuries}' WHERE id={id}"
                                          .format(date=request.form["attack_date"],city=request.form["attack_city"],tgroup=request.form["attack_tgroup"],atype=request.form["attack_type"]
                                                  ,atarget=request.form["attack_target"],fatalities=request.form["attack_fatalities"],injuries=request.form["attack_injuries"],id=request.form["attack_id"]))
           self.connection.commit()


What we do in update_attack() is, we first query for the attack being updated. Then we compare the updated attack data to the existing one.
We then update the tables according to the differences between these 2 attacks.

Delete
------

**Deleting an attack is handled in the delete_attack() function of the Moderation Class**


   .. code-block:: python

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

When deleting an attack, first the existing attack is queried. Then the city the attack was made in and the tgroup that made the attack gets updated.