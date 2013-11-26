import subprocess

class Poudriere:
    def __init__(self):
        self.jails = list()

    def Describe(self):
        return "Poudriere"

    def Run(self, job, config):
        if len(job.options) == 0:
            return False

        if "jails" not in job.options:
            return False

        with job.GetLogfile(config) as logfile:
            for jail in job.options["jails"]:
                if "version" in jail:
                    # Recreate the jail to pick up latest userland
                    status = subprocess.call([
                        "sudo",
                        "poudriere",
                        "jail",
                        "-j", jail["name"],
                        "-d"
                    ], stdout=logfile, stderr=subprocess.STDOUT)
                    if status != 0:
                        return False

                    args = [
                        "sudo",
                        "poudriere",
                        "jail",
                        "-c",
                        "-j", jail["name"],
                        "-p", jail["ports"],
                        "-v", jail["version"]
                    ]
                    if config.debug:
                        print "[*] Creating jail. Args: " + ", ".join(args)
                    status = subprocess.call(args, stdout=logfile, stderr=subprocess.STDOUT)
                    if status != 0:
                        return False

                status = subprocess.call([
                    "sudo",
                    "poudriere",
                    "bulk",
                    "-f", jail["configfile"],
                    "-j", jail["name"],
                    "-p", jail["ports"]
                ], stdout=logfile, stderr=subprocess.STDOUT)
                if status != 0:
                    return False

                if "syncdir" in jail:
                    status = subprocess.call([
                        "sudo",
                        "rsync"
                        "-a",
                        job.options["jaildir"] + "/data/packages/" + jail["name"] + "-" + jail["ports"] + "/",
                        jail["syncdir"]
                    ], stdout=logfile, stderr=subprocess.STDOUT)
                    if status != 0:
                        return False

            return True
