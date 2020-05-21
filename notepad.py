from src.SData import SDataConnection as SDataConnection
from src.SQlite import DbConnection as Db
from datetime import date

# were i test out ideas and concepts

# modules used:
SDataCon = SDataConnection.SdataConnection('bot01','Bot01','http://192.168.1.200:5495/sdata/accounts50/gcrm/-/')
db = Db.DbConnection('192.168.1.94','root','TheOfficePeople',3306,'autoStock')


