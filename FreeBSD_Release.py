import os
import sys
import shutil
import subprocess

class Release:
    def __init__(self):
        self.jobs = 7
        self.kernel = "SEC"
        self.local_destdir = "/src/release/pub/FreeBSD/snapshots/amd64/amd64/11.0-CURRENT"

    def Describe(self):
        return "ISO/memstick"

    def get_src_job(self, job):
        for dep in job.dependencies:
            if dep.name == "FreeBSD Source":
                return dep

        return None

    def Run(self, job, config):
        curdir = os.getcwd()
        newdir = "/usr/src"
        srcjob = self.get_src_job(job)
        if srcjob == None:
            return False
        if "srcdir" in srcjob.options:
            newdir = srcjob.options["srcdir"]

        if not "branches" in srcjob.options:
            return True

        os.chdir(newdir)
        
        succeeded = True
        with job.GetLogfile(config) as logfile:
            for branch in srcjob.options["branches"]:
                if not branch["succeeded"]:
                    continue

                if not srcjob.instance.checkout_branch(branch["local-branch"], logfile):
                    succeeded = False
                    continue

                status = subprocess.call(["make", "-sj" + str(self.jobs), "KERNCONF=" + self.kernel, "buildworld", "buildkernel"], stdout=logfile, stderr=subprocess.STDOUT)
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

                if "destdir" in branch:
                    for filename in os.listdir("/usr/obj/usr/src/release"):
                        if len(filename) > 3 and filename[-3:] in ["txz", "iso"]:
                            shutil.copy("/usr/obj/usr/src/release/" + filename, branch["destdir"])

        os.chdir(curdir)
        return True
