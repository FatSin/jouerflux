""" Flask application initialization """


import connexion
from flask_sqlalchemy import SQLAlchemy

from exceptions import NotFoundInDB,\
                       IntegrityError,\
                       DatabaseError,\
                       GenericError,\
                       not_found_handler,\
                       integrity_error_handler,\
                       db_error_handler,\
                       generic_error_handler


conn_app = connexion.App(__name__, specification_dir="./")
conn_app.add_api("specifications.yaml")

conn_app.add_error_handler(NotFoundInDB, not_found_handler)
conn_app.add_error_handler(IntegrityError, integrity_error_handler)
conn_app.add_error_handler(DatabaseError, db_error_handler)
conn_app.add_error_handler(GenericError, generic_error_handler)

flask_app = conn_app.app

flask_app.config['SQLALCHEMY_DATABASE_URI'] = r'sqlite:///jouerflux.db'
flask_app.config['ENV'] = 'production'

db = SQLAlchemy(flask_app)


if __name__ == '__main__':
    conn_app.run()

