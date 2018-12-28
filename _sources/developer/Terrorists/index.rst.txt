.. ITUCSDB1840 documentation master file, created as a template.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Terrorist Groups Table
======================

Create
-------

**Tgroups table is created in dbinit.py by adding the following statement to the init_statements list**



      "CREATE TABLE IF NOT EXISTS TGROUPS (NAME VARCHAR(100) PRIMARY KEY,TOTALA INTEGER DEFAULT 0,TOTALI INTEGER DEFAULT 0,TOTALF INTEGER DEFAULT 0,CATARGET VARCHAR(100),CATYPE VARCHAR(100))",


Add
----

**Adding a tgroup is handled in the add_tgroup() function of the Moderation Class**


   .. code-block:: python

      def add_tgroup(self):

        self.connection.run_statements("INSERT INTO TGROUPS(NAME) VALUES('{name}') ON CONFLICT DO NOTHING ".format(name=request.form['tgroup_name']))
        self.connection.commit()

ON CONFLICT DO NOTHING allows us to avoid errors when trying to add an existing tgroup.

Read
----

**Reading a city happens in /tgroups page**

   .. code-block:: python

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

A connection to the database is established and the tgroups are queried and passed to the template as parameters.

Update
------

**Updating a tgroup is handled in the update_tgroup() function of the Moderation Class**


   .. code-block:: python

      def update_tgroup(self):

        self.connection.run_statements("UPDATE TGROUPS SET name='{new_name}' WHERE name='{name}'".format(new_name=request.form["tgroup_new_name"],name=request.form["tgroup_name"]))
        self.connection.commit()


Notice that we only update the name of the tgroup. As the rest of it's attributes are always automatically calculated elsewhere.

Delete
------

**Deleting a tgroup is handled in the delete_tgroup() function of the Moderation Class**


   .. code-block:: python

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

When deleting a tgroup we have to first query the attacks that have been made by that tgroup.Then for each attack we need to update the data of the cities that the attacks were made in as if we just deleted the attack.
This is necessary in order to keep the data correct.The reason is that we have ON DELETE CASCADE for tgroup foreign keys which means we will automatically delete every attack that was made by that tgroup when we delete a tgroup.