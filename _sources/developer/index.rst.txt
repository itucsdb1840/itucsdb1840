.. ITUCSDB1840 documentation master file, created as a template.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Developer Guide
===============

Database Design
---------------

**For this project I implemented 5 tables which were:**

**Attacks**

Non-Key Columns:

* DATE(Date) ; Date of the attack
* ATYPE(Varchar(100)) ; Type of the attack
* ATARGET(Varchar(100)) ; Target of the attack
* FATALITIES(Integer) ; Number of casualties
* INJURIES(Integer) ; Number of injuries

Key Columns:

* ID (Primary Key, Serial)
* CITY (Foreign Key which references table CITIES(Name))
* TGROUP (Foreign Key which references table TGROUP(Name))

**Cities**

Non-Key Columns:

* TOTALA(Integer) ; Total attack made in this city
* TOTALF(Integer) ; Total casualties sustained in this city
* TOTALI(Integer) ; Total injuries sustained in this city
* CATARGET(Varchar(100)) ; Most common attack target in this city
* CATYPE(Varchar(100)) ; Most common attack type in this city

Key Columns:

* Name(Primary Key,Varchar(30))

**Tgroups**

Non-Key Columns:

* TOTALA(Integer) ; Total attack made by this terrorist group
* TOTALF(Integer) ; Total casualties inflicted by this terrorist group
* TOTALI(Integer) ; Total injuries caused by this terrorist group
* CATARGET(Varchar(100)) ; Most common attack target for this terrorist group
* CATYPE(Varchar(100)) ; Most common attack type for this terrorist group

Key Columns:

* Name(Primary Key,Varchar(100))

**Users**

Non-Key Columns:

* Username(Varchar(20)) ; User name of the user
* Password(Varchar(10)) ; Password of the user
* Profilepic(bytea) ; Profile picture of the user

**Suggestion**

* Content(Varchar(250)) ; Suggestions taken from visitors

**E/R Diagram:**

   .. figure:: ../figures/E_R_diagram.png

Code
----

.. note:: After every call to a moderation function the following codeblock, which calculates the common attack target and types for the tgroups and cities, is executed to keep the data correct.

   .. code-block:: python

      connection = moderation.connection
       cities = connection.run_queries("SELECT name FROM CITIES")
       # Since there are changes the tables need to be updated after each moderation
       for c, in cities:
           # CATARGET
           try:
               atarget, count = connection.run_queries(
               "SELECT atarget, count(atarget) FROM attacks WHERE city = '{city}' GROUP BY atarget ORDER BY count DESC LIMIT 1".format(
                   city=c))[0]
               connection.run_statements(
                   "UPDATE CITIES SET catarget = '{atarget}' WHERE name='{city}'".format(atarget=atarget, city=c))
           except IndexError:
               print("NOT A VALID QUERY WITH THE CITY:")
               print(c)

           # CATYPE
           try:
               atype, count =connection.run_queries(
                   "SELECT atype, count(atype) FROM attacks WHERE city = '{city}' GROUP BY atype ORDER BY count DESC LIMIT 1".format(
                       city=c))[0]
               connection.run_statements("UPDATE CITIES SET catype = '{atype}' WHERE name='{city}'".format(atype=atype, city=c))
           except IndexError:
               print("NOT A VALID QUERY WITH THE CITY:")
               print(c)

       # CATARGET and CATYPE calculations for tgroups
       tgroups = connection.run_queries("SELECT name FROM TGROUPS")
       for t, in tgroups:
           # CATARGET
           try:
               atarget, count = connection.run_queries(
                   "SELECT atarget, count(atarget) FROM attacks WHERE tgroup = '{gname}' GROUP BY atarget ORDER BY count DESC LIMIT 1".format(
                       gname=t))[0]
               connection.run_statements(
                   "UPDATE TGROUPS SET catarget = '{atarget}' WHERE name='{gname}'".format(atarget=atarget, gname=t))
           except IndexError:
               print("NOT A VALID QUERY")

           # CATYPE
           try:
               atype, count = connection.run_queries(
                   "SELECT atype, count(atype) FROM attacks WHERE tgroup = '{gname}' GROUP BY atype ORDER BY count DESC LIMIT 1".format(
                       gname=t))[0]
               connection.run_statements("UPDATE TGROUPS SET catype = '{atype}' WHERE name='{gname}'".format(atype=atype, gname=t))
           except IndexError:
               print("NOT A VALID QUERY")

       connection.commit()
       connection.close()


.. toctree::
   Attacks/index
   Cities/index
   Terrorists/index
   extras/index

