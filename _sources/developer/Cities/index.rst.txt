.. ITUCSDB1840 documentation master file, created as a template.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Cities Table
===============

Create
-------

**Cities table is created in dbinit.py by adding the following statement to the init_statements list**



      "CREATE TABLE IF NOT EXISTS CITIES(NAME VARCHAR(30) PRIMARY KEY,TOTALA INTEGER DEFAULT 0,TOTALF INTEGER DEFAULT 0,TOTALI INTEGER DEFAULT 0,caTarget varchar(100),CATYPE varchar(100))",



Add
----

**Adding a city is handled in the add_city() function of the Moderation Class**


   .. code-block:: python

       def add_city(self):

           self.connection.run_statements("INSERT INTO CITIES(NAME) VALUES('{name}') ON CONFLICT DO NOTHING ".format(name=request.form['city_name']))
           self.connection.commit()

ON CONFLICT DO NOTHING allows us to avoid errors when trying to add an existing city

Read
----

**Reading a city happens in /cities page**

   .. code-block:: python

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

A connection to the database is established and the cities are queried and passed to the template as parameters.

Update
------

**Updating a city is handled in the update_city() function of the Moderation Class**


   .. code-block:: python

      def update_city(self):

        self.connection.run_statements("UPDATE CITIES SET name='{new_name}' WHERE name='{name}'".format(new_name=request.form["city_new_name"],name=request.form["city_name"]))
        self.connection.commit()


Notice that we only update the name of the city. As the rest of it's attributes are always automatically calculated elsewhere.

Delete
------

**Deleting a city is handled in the delete_city() function of the Moderation Class**


   .. code-block:: python

       def delete_city(self):
           attacks = self.connection.run_queries("SELECT tgroup,fatalities,injuries FROM ATTACKS WHERE city='{city}'".format(city=request.form['city_name']))
           for attack in attacks:
               tgroup,fatalities,injuries = attack
               self.connection.run_statements("UPDATE TGROUPS SET totala = totala-1, totalf = totalf - {fatalities}, totali = totali - {injuries} WHERE name = '{tgroup}'"
                                           .format(tgroup=tgroup,fatalities=fatalities,injuries=injuries))
           self.connection.run_statements("DELETE FROM CITIES WHERE name='{city}'".format(city=request.form["city_name"]))
           self.connection.commit()

When deleting a city we have to first query the attacks that have happened in that city.Then for each attack we need to update the data of the terrorist group that made the attack as if we just deleted the attack.
This is necessary in order to keep the data correct.The reason is that we have ON DELETE CASCADE for city foreign keys which means we will automatically delete every attack that has happened in that city when we delete a city.