import subprocess

class Poudriere:
    def __init__(self):
        self.jails = list()
        self.poudriere_dir = "/tank/poudriere/jails"
        self.config_dir = "/tank/poudriere/configs"

        jail = dict()
        jail["name"] = "11-current_amd64"
        jail["ports"] = "local"
        jail["configfile"] = "11-current_amd64.ports.txt"
        jail["syncdir"] = "/tank/poudriere/packages/11-current_amd64"
        jail["version"] = "11.0-CURRENT"
        self.jails.append(jail)

    def Describe(self):
        return "Poudriere"

    def Run(self, job, config):
        with job.GetLogfile(config) as logfile:
            for jail in self.jails:
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
                    "-f", self.config_dir + "/" + jail["configfile"],
                    "-j", jail["name"],
                    "-p", jail["ports"]
                ], stdout=logfile, stderr=subprocess.STDOUT)
                if status != 0:
                    return False

                status = subprocess.call([
                    "sudo",
                    "rsync"
                    "-a",
                    self.poudriere_dir + "/data/packages/" + jail["name"] + "-" + jail["ports"] + "/",
                    jail["syncdir"]
                ], stdout=logfile, stderr=subprocess.STDOUT)
                if status != 0:
                    return False

            return True
