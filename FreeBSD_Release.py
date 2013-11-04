import os
import sys
import shutil
import subprocess

class FreeBSD_Release:
    def __init__(self):
        self.jobs = 7
        self.kernel = "SEC"
        self.local_destdir = "/src/release/pub/FreeBSD/snapshots/amd64/amd64/11.0-CURRENT"

    def Describe(self):
        return "ISO/memstick"

    def Run(self, job, config):
        curdir = os.getcwd()
        os.chdir("/usr/src")
        
        with job.GetLogfile(config) as logfile:
            status = subprocess.call(["make", "-DNO_CLEAN", "-sj" + str(self.jobs), "KERNCONF=" + self.kernel, "buildworld", "buildkernel"], stdout=logfile, stderr=subprocess.STDOUT)
            if status != 0:
                os.chdir(curdir)
                return False

            os.chdir("/usr/src/release")
            status = subprocess.call(["sudo", "make", "clean"], stdout=logfile, stderr=subprocess.STDOUT)
            if status != 0:
                os.chdir(curdir)
                return False

            status = subprocess.call(["sudo", "make", "-s", "KERNCONF=" + self.kernel, "release"], stdout=logfile, stderr=subprocess.STDOUT)
            if status != 0:
                os.chdir(curdir)
                return False

        for filename in os.listdir("/usr/obj/usr/src/release"):
            if len(filename) > 3 and filename[-3:] in ["txz", "iso"]:
                shutil.copy("/usr/obj/usr/src/release/" + filename, self.local_destdir)

        os.chdir(curdir)
        return True
