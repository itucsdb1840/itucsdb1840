import pandas as pd
data_cols = [1, 2, 3, 11,29, 35, 58, 98, 101]  # Necessary data columns
df = pd.read_csv('./data.csv', error_bad_lines=False, encoding='ISO-8859-1', usecols=data_cols,na_values="",
                     dtype=str)  # This will read the data columns specified in data_cols and fill null values with UNKOWN
data = df.rename(columns={'iyear': 'year', 'imonth': 'month', 'iday': 'day','provstate':'city', 'attacktype1_txt': "attacktype",
                              'targtype1_txt': 'target', 'nkill': 'fatalities', 'nwound': 'injuries'})

INIT_STATEMENTS=[
    ]
    # Filling the statements
for i,row in data.iterrows():
    date = "{year}-{month}-{day}".format(year=row['year'],month=row['month'],day=row['day'])
    # Had to check like this to avoid values getting converted to nan
    statement1 = "INSERT INTO CITIES(NAME) VALUES('{name}') ON CONFLICT DO NOTHING ".format(name=row['city'])  # Make sure the referenced city exists
    INIT_STATEMENTS.append(statement1)
    statement2 = "INSERT INTO TGROUPS(NAME) VALUES('{name}') ON CONFLICT DO NOTHING".format(name=row['gname'])  # Make sure the referenced group exists
    INIT_STATEMENTS.append(statement2)
    statement3 = "INSERT INTO ATTACKS(DATE,CITY,TGROUP,ATYPE,ATARGET,FATALITIES,INJURIES) VALUES('{date}','{city}','{gname}','{attacktype}','{target}','{fatalities}','{injuries}') ON CONFLICT DO NOTHING"\
            .format(date=date,city=row['city'],gname=row['gname'],attacktype=row['attacktype'],target=row['target'],fatalities =row['fatalities'],injuries=row['injuries'])
    INIT_STATEMENTS.append(statement3)
if __name__ == "__main__":
    #You need to delete statements.txt before running this script if it exists.
    output = open("statements.txt","a")
    for statement in INIT_STATEMENTS:
        line = "\"{s}\",".format(s=statement)
        output.write(line)