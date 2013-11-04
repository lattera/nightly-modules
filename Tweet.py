import os
import subprocess

class Tweet:
    def __init__(self):
        self.completed = list()
        pass

    def _tweet_status(self, message):
        subprocess.call(["ttytter", "-status=" + message, "-hold", "-silent"])

    def _recurse_job(self, job):
        for dep in job.dependencies:
            self._recurse_job(dep)

        if job.name in self.completed:
            return

        self.completed.append(job.name)

        description = job.name
        if "Describe" in dir(job.instance) and callable(getattr(job.instance, "Describe")):
            description = job.instance.Describe()

        status = "Unknown"
        if job.status == "skipped":
            status = "Skipped"
        elif job.status == "true":
            status = "Success"
        elif job.status == "false":
            status = "Failed"

        self._tweet_status("#FreeBSD #ASLR automated nightly build: Step[" + description + "]: " + status)

    def Run(self, job, config):
        for dep in job.dependencies:
            self._recurse_job(dep)

        return True
