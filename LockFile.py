import os
import subprocess

class LockFile:
    @staticmethod
    def exists():
        return os.path.isfile('.tsk/lock_file')

    @staticmethod
    def create():
        devnull = open(os.devnull, 'w')
        subprocess.call(['touch .tsk/lock_file'], shell=True, stdout=devnull, stderr=devnull)

    @staticmethod
    def remove():
        devnull = open(os.devnull, 'w')
        subprocess.call(['rm .tsk/lock_file'], shell=True, stdout=devnull, stderr=devnull)
