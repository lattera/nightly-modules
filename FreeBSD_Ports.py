import os
import sys
import subprocess

class FreeBSD_Ports:
    def __init__(self):
        self.portsdir = "/usr/ports"
        self.jobs = 7

    def Describe(self):
        return "Ports Tree"

    def Run(self, job, config):
        curdir = os.getcwd()
        os.chdir(self.portsdir)

        with job.GetLogfile(config) as logfile:
            status = subprocess.call(["git", "fetch"], stdout=logfile, stderr=subprocess.STDOUT)
            if status != 0:
                os.chdir(curdir)
                return False

            status = subprocess.call(["git", "merge", "-m", "[automated] Merge origin/master", "origin/master"], stdout=logfile, stderr=subprocess.STDOUT)
            if status != 0:
                os.chdir(curdir)
                return False

            if self.portsdir == "/usr/ports":
                status = subprocess.call(["make", "-j" + str(self.jobs), "index"], stdout=logfile, stderr=subprocess.STDOUT)
                if status != 0:
                    os.chdir(curdir)
                    return False

            os.chdir(curdir)

            return True
