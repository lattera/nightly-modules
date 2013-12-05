import os
import sys
import subprocess

class Source:
    def __init__(self):
        pass

    def Describe(self):
        return "Source"

    def fetch_upstream(self, upstream, logfile):
        status = subprocess.call(["git", "fetch", upstream], stdout=logfile, stderr=subprocess.STDOUT)
        return status == 0

    def checkout_branch(self, branch, logfile):
        status = subprocess.call(["git", "checkout", branch], stdout=logfile, stderr=subprocess.STDOUT)
        return status == 0

    def merge_upstream(self, upstream, upstream_branch, logfile):
        status = subprocess.call(["git", "merge", "-m", "[automated] Merge in " + upstream + "/" + upstream_branch, upstream + "/" + upstream_branch], stdout=logfile, stderr=subprocess.STDOUT)
        return status == 0

    def push_remote(self, local_branch, remote, remote_branch, logfile):
        status = subprocess.call(["git", "push", remote, local_branch + ":" + remote_branch], stdout=logfile, stderr=subprocess.STDOUT)
        return status == 0

    def Run(self, job, config):
        curdir = os.getcwd()
        newdir = "/usr/src"
        if "srcdir" in job.options:
            newdir = job.options["srcdir"]

        os.chdir(newdir)

        with job.GetLogfile(config) as logfile:
            for branch in job.options["branches"]:
                branch["succeeded"] = False
                if not self.fetch_upstream(branch["upstream"], logfile):
                    continue

                if not self.checkout_branch(branch["local-branch"], logfile):
                    continue

                if not self.merge_upstream(branch["upstream"], branch["upstream-branch"], logfile):
                    continue

                if "push-remote" in branch:
                    if not self.push_remote(branch["local-branch"], branch["push-remote"], branch["push-remote-branch"], logfile):
                        continue

                branch["succeeded"] = True

            os.chdir(curdir)
            succeeded = True
            for branch in job.options["branches"]:
                if branch["succeeded"] == False:
                    succeeded = False
                    break

            return succeeded
