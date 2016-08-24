import subprocess

class TskGit:
    def __init__(self, tskDir, subp=subprocess):
        self.tskDir = tskDir
        self.subprocess = subp

    def commit(self):
        proc = self.subprocess.Popen("cd {:s} && git add tskfile && git commit -m 'Updates tskfile.'".format(self.tskDir),
            shell=True, stdout=self.subprocess.PIPE)
        proc.wait()

    def push(self):
        proc = self.subprocess.Popen("cd {:s} && git push".format(self.tskDir), shell=True, stdout=self.subprocess.PIPE)
        proc.wait()
        if proc.returncode != 0:
            return False
        return True

    def pull(self):
        proc = self.subprocess.Popen("cd {:s} && git pull".format(self.tskDir), shell=True, stdout=self.subprocess.PIPE)
        proc.wait()
        if proc.returncode != 0:
            return False
        return True

    def init(self):
        proc = self.subprocess.Popen("git init {:s}".format(self.tskDir), shell=True, stdout=subprocess.PIPE)
        proc.wait()
        if proc.returncode != 0:
            return False
        return True
