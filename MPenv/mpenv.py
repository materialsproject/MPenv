from argparse import ArgumentParser
import os
import subprocess
import traceback

__author__ = 'Anubhav Jain'
__copyright__ = 'Copyright 2013, The Materials Project'
__version__ = '0.1'
__maintainer__ = 'Anubhav Jain'
__email__ = 'ajain@lbl.gov'
__date__ = 'Aug 20, 2013'

def create_env():

    m_description = 'This program creates a self-contained environment for running ' \
                    'and testing FireWorks workflows at NERSC'
    parser = ArgumentParser(description=m_description)

    parser.add_argument('name', help='name of the new environment', default=None)

    args = parser.parse_args()

    c = []
    c.append(('print', 'SETTING UP VIRTUALENV'))
    c.append(("mkdir", args.name))
    c.append(("cd", args.name))
    c.append(("mkdir", "virtenv"))
    c.append("virtualenv --no-site-packages virtenv")
    c.append(("activate", os.path.join(os.getcwd(), args.name, 'virtenv/bin/activate_this.py')))

    c.append(('print', 'INSTALLING FIREWORKS (developer mode)'))
    c.append(("pip install django"))
    c.append(("mkdir", "codes"))
    c.append(("cd", 'codes'))
    c.append("git clone git@github.com:materialsproject/fireworks.git")
    c.append(("cd", 'fireworks'))
    c.append("python setup.py develop")


    try:
        for command in c:
            if isinstance(command, str):
                p = subprocess.check_call(command, shell=True, executable="/bin/bash")
            elif command[0] == 'mkdir':
                os.mkdir(command[1])
            elif command[0] == 'cd':
                os.chdir(command[1])
            elif command[0] == 'activate':
                execfile(command[1], dict(__file__=command[1]))
            elif command[0] == 'print':
                print '---'+command[1]
            else:
                raise ValueError("Invalid command! {}".format(command))
    except:
        traceback.print_exc()


if __name__ == '__main__':
    create_env()