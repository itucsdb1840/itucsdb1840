.. ITUCSDB1840 documentation master file, created as a template.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Extra Tables
===============

Users
-----
Adding and reading of users happen in the homepage.

   .. code-block:: python

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
                  username = request.form.get("username")
                  password = request.form.get("password")
                  unwanted = ["(", ")", ";"]
                  for element in unwanted:
                      if element in username or element in password or username == "":
                          session["logged"] = False
                      else:
                          UserInfo = connection.run_queries(
                              "SELECT * FROM USERS WHERE username='{username}' AND password='{password}'".format(
                                  username=username, password=password))
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

**Add**

A user is added in this part:

   .. code-block:: python

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

 Which first checks the users table to see if the username is unique. Then it also checks whether the characters used in the username are valid or not.
 It changes the session data to the current users data which means it automatically logs in after signing up. Then it inserts the new users data into the database.

**Read**

A user data is read in this part:

   .. code-block:: python

      if request.form.get("action")=="Login":
                        username = request.form.get("username")
                        password = request.form.get("password")
                        unwanted = ["(", ")", ";"]
                        for element in unwanted:
                            if element in username or element in password or username == "":
                                session["logged"] = False
                            else:
                                UserInfo = connection.run_queries(
                                    "SELECT * FROM USERS WHERE username='{username}' AND password='{password}'".format(
                                        username=username, password=password))
                                if UserInfo != []:
                                    userTuple = UserInfo[0]
                                    session["username"] = userTuple[0]
                                    session["password"] = userTuple[1]
                                    session["logged"] = True
                                    session["pp"] = None
                                else:
                                    session["logged"] = False

Where it first validates the username and password to avoid injections. Then it queries the database to see if the user exists.Then adds the user to the current session which is equal to logging in.

Suggestions
-----------

Adding of a suggestion is also made in the homepage, in this part:

   .. code-block:: python

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

Which validates the user input before inserting it to the database.