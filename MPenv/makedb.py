import os
import random
import string
from pymongo import MongoClient
import yaml

__author__ = 'Anubhav Jain'
__copyright__ = 'Copyright 2013, The Materials Project'
__version__ = '0.1'
__maintainer__ = 'Anubhav Jain'
__email__ = 'ajain@lbl.gov'
__date__ = 'Aug 21, 2013'


def create_db():
    module_dir = os.path.dirname(os.path.abspath(__file__))
    static_dir = os.path.join(module_dir, 'makedb_static')

    ENV_NAME = "aj"
    curr_dir = os.getcwd()
    env_dir = os.path.join(curr_dir, ENV_NAME)
    os.makedirs(env_dir)

    with open(os.path.join(module_dir, "private", "admin_creds.yaml")) as f:
        creds = yaml.load(f.read())

        creds['USER'] = "admin_{}".format(ENV_NAME)
        creds['PW'] = make_password()

        # get connection
        connection = MongoClient(creds['HOST'], creds['PORT'], j=True)
        db = connection[creds['admin_name']]
        db.authenticate(creds['admin_username'], creds['admin_password'])

        creds['NAME'] = "fw_{}".format(ENV_NAME)
        connection.drop_database(creds['NAME'])
        db_fw = connection[creds['NAME']]
        db_fw.add_user(creds['USER'], creds['PW'], read_only=False)

        with open(os.path.join(static_dir, 'my_launchpad.yaml')) as f2:
            t = string.Template(f2.read())
            contents = t.substitute(creds)
            with open(os.path.join(env_dir, 'my_launchpad.yaml'), 'w+') as f3:
                f3.write(contents)


def make_password():
    length = 8
    chars = string.ascii_letters + string.digits + '!@#$%^&*()'
    random.seed = (os.urandom(1024))

    return ''.join(random.choice(chars) for i in range(length))

if __name__ == '__main__':
    create_db()