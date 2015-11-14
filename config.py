import os
basedir = os.path.abspath(os.path.dirname(__file__))
db_path = os.path.join(basedir,"db","user.db")

DATABASE= db_path
SECRET_KEY='development key'
USERNAME='admin'
PASSWORD='default'