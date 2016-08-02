import subprocess

class TskGit:
    def __init__(self, tskDir, subp=subprocess):
        self.tskDir = tskDir
        self.subprocess = subp

    def commit(self):
        proc = self.subprocess.Popen("cd {:s} && git add tskfile && git commit -m 'Updates tskfile.'".format(self.tskDir),
            shell=True, stdout=self.subprocess.PIPE)
        proc.wait()


    def init(self):
        proc = subprocess.Popen("git init {:s}".format(self.tskDir), shell=True, stdout=subprocess.PIPE)
        proc.wait()
        if proc.returncode != 0:
            return False
        return True
