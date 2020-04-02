import django
import sys
import os
import sqlite3

from django.conf import settings
from django.core.management import execute_from_command_line


# configuring django
BASE_DIR = os.path.dirname(os.path.realpath(sys.argv[0]))
DB_PATH = os.path.join(BASE_DIR,"records/devdb.sqlite")

# # make sqlite3 file since django is unable to
# with sqlite3.connect(DB_PATH) as fake_conn:
#     pass

settings.configure(
    DATABASES={
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': DB_PATH,
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

# set some global vars of my own (non-django for now)
KMODEL_DIR = "records/kmodel"
ARTIFACT_DIR = "records/artifact"

from mod_man.interface import KModel

if __name__ == "__main__" :
    execute_from_command_line(["","test"])


    kmod = KModel()
    kmod.save()
    kmod.add_tags(["test_tag"])


# import interface functions into current scope