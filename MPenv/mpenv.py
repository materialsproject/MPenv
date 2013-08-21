from argparse import ArgumentParser
import os
from string import Template
import string
import subprocess
import traceback

__author__ = 'Anubhav Jain'
__copyright__ = 'Copyright 2013, The Materials Project'
__version__ = '0.1'
__maintainer__ = 'Anubhav Jain'
__email__ = 'ajain@lbl.gov'
__date__ = 'Aug 20, 2013'

def create_env():

    root_dir = os.getcwd()
    module_dir = os.path.dirname(os.path.abspath(__file__))

    DEV_MODE = True
    BASHRC_FILE = os.path.join(root_dir, "bashrc.temp")

    m_description = 'This program creates a self-contained environment for running ' \
                    'and testing FireWorks workflows at NERSC'
    parser = ArgumentParser(description=m_description)

    parser.add_argument('name', help='name of the new environment', default=None)

    args = parser.parse_args()



    print module_dir
    c = []
    c.append(('print', 'SETTING UP VIRTUALENV'))
    c.append(("mkdir", args.name))
    c.append(("cd", args.name))
    c.append(("mkdir", "virtenv"))
    c.append("virtualenv --no-site-packages virtenv")
    c.append(("activate", os.path.join(root_dir, args.name, 'virtenv/bin/activate_this.py')))

    c.append(('print', 'INSTALLING FIREWORKS (developer mode)'))
    if not DEV_MODE:
        c.append(("pip install django"))
        c.append(("mkdir", "codes"))
        c.append(("cd", 'codes'))
        c.append("git clone git@github.com:materialsproject/fireworks.git")
        c.append(("cd", 'fireworks'))
        c.append("python setup.py develop")

    c.append(('print', 'ADDING SETTINGS'))
    c.append(("cd", os.path.join(root_dir, args.name)))
    c.append(("mkdir", "config"))
    c.append(("cd", "config"))
    c.append(("mkdir", "config_mendel"))
    c.append(("mkdir", "config_hopper"))
    c.append(("mkdir", "dbs"))
    c.append(("mkdir", "logs"))

    c.append(('print', 'UPDATING ENVIRONMENT'))
    c.append(("append", ))


    try:
        for command in c:
            if isinstance(command, str):
                subprocess.check_call(command, shell=True, executable="/bin/bash")
            elif command[0] == 'mkdir':
                os.mkdir(command[1])
            elif command[0] == 'cd':
                os.chdir(command[1])
            elif command[0] == 'activate':
                execfile(command[1], dict(__file__=command[1]))
            elif command[0] == 'print':
                print '---'+command[1]
            elif command[0] == 'append':
                appendtext = ''
                with open(os.path.join(module_dir, 'BASH_template.txt')) as f:
                    t = CustomTemplate(f.read())
                    replacements = {}
                    replacements["ACTIVATE"] = os.path.join(root_dir, args.name, 'virtenv/bin/activate')
                    replacements["CONFIG_LOC"] = os.path.join(root_dir, args.name, 'config')
                    replacements["NAME"] = args.name
                    appendtext = t.substitute(replacements)
                with open(BASHRC_FILE, 'a') as f:
                    f.write(appendtext)

            else:
                raise ValueError("Invalid command! {}".format(command))
    except:
        traceback.print_exc()


class CustomTemplate(string.Template):
    delimiter = '$$'

if __name__ == '__main__':
    create_env()