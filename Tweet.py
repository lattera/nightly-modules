import os
import subprocess

class Tweet:
    def __init__(self):
        self.completed = list()
        self.options = dict()
        pass

    def _tweet_status(self, message):
        subprocess.call(["ttytter", "-status=" + message, "-hold", "-silent"])

    def _recurse_job(self, job):
        for dep in job.dependencies:
            self._recurse_job(dep)

        if job.name in self.completed:
            return

        self.completed.append(job.name)

        prefix = "#FreeBSD #ASLR automated nightly build: "
        if "prefix" in self.options:
            prefix = self.options["prefix"]

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

        self._tweet_status(prefix + " Step[" + description + "]: " + status)

    def Run(self, job, config):
        self.options = job.options
        for dep in job.dependencies:
            self._recurse_job(dep)

        return True
