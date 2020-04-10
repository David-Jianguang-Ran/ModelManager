import django
import sys
import os

from django.conf import settings
from django.core.management import execute_from_command_line


# set some global vars of my own (non-django for now)
KMODEL_DIR = "records/kmodel"
ARTIFACT_DIR = "records/artifact"

# make data storage dir if one is not found
os.makedirs("records",exist_ok=True)
os.makedirs(KMODEL_DIR,exist_ok=True)
os.makedirs(ARTIFACT_DIR,exist_ok=True)

# configuring django
BASE_DIR = os.getcwd()

settings.configure(
    DATABASES={
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': os.path.join(BASE_DIR,"records/devdb.sqlite"),
        }
    },
    INSTALLED_APPS=[
        'mod_man',
    ],
    BASE_DIR=BASE_DIR
)
django.setup()
execute_from_command_line(["","makemigrations"])
execute_from_command_line(["","migrate"])



from mod_man.interface import *

if __name__ == "__main__" :
    execute_from_command_line(["","test"])



# import interface functions into current scope