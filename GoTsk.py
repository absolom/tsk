from FrontEnd import TskFrontEnd
from Pomo import Pomo
from TaskFileParser import TaskFileParser
from Render import TskTextRender
from Render import PomoRender
from TskLogic import TskLogic
from Storage import Storage
from LockFile import LockFile
from TskGit import TskGit
import shutil
import argparse
import subprocess
import time
import os.path
import sys
import atexit

class TskLogicFactory:
    @staticmethod
    def get(*args, **kwargs):
        return TskLogic(*args, **kwargs)

def goTsk(git=TskGit(".tsk"), LockFileCls=LockFile, TskLogicFactory=TskLogicFactory,
    pomo=Pomo(), atexit=atexit, os=os, shutil=shutil, time=time, StorageCls=Storage,
    subprocess=subprocess, arguments=sys.argv[1:], TaskFileParserCls=TaskFileParser,
    TskFrontEndCls=TskFrontEnd, TskTextRenderCls=TskTextRender, PomoRenderCls=PomoRender,
    open=open):

    tsk = TskLogicFactory.get(t=time)

    atexit.register(LockFileCls.remove)

    if LockFileCls.exists():
        print 'Lock file detected. Another instance of tsk may be open. Remove the lock file'
        print 'in .tsk/ to override.'
        sys.exit(1)
    else:
        LockFileCls.create()

    if os.path.exists('.tsk'):
        try:
            shutil.copyfile('.tsk/tskfile_backup', '/tmp/tskfile_backup')
        except:
            None
        shutil.copyfile('.tsk/tskfile', '.tsk/tskfile_backup')
        storage = StorageCls(time)
        if storage.load('.tsk/tskfile'):
            tsk.tasks = storage.tasks
            if storage.pomo:
                pomo = storage.pomo
        else:
            print 'Failed to load Tsk database file.'

    fe = TskFrontEndCls(tsk, pomo, TskTextRenderCls(tsk), PomoRenderCls(pomo), time, subprocess,
        TaskFileParserCls())

    valid_commands = [ "edit",
                       "add",
                       "status",
                       "show_backlog",
                       "sort_backlog",
                       "activate",
                       "block",
                       "open",
                       "close",
                       "start",
                       "pause",
                       "cancel",
                       "monitor",
                       "move",
                       "closed",
                       "show",
                       "init",
                       "set_due_date",
                       "remove_due_date",
                       "time_estimate",
                       "time_log",
                       "push",
                       "pull" ]

    parser = argparse.ArgumentParser(description='Self task management program.')
    parser.add_argument('command',  choices=valid_commands)
    parser.add_argument('args', nargs=argparse.REMAINDER)

    skip_git = False
    ret = True

    # TODO: Refactor to use subparsers

    args = parser.parse_args(args=arguments)

    if args.command == "init":
        if os.path.exists('.tsk'):
            print "Tsk already initialized"
            return False

        os.makedirs('.tsk')
        f = open('.tsk/tskfile', 'w+')
        f.close()

        if not git.init():
            print "Failed to create git repo."
            return False

        print 'Tsk initialized.'
        return True

    if not os.path.exists('.tsk'):
        print "Tsk directory not found.  Use init command to initialize task in this directory."
        return False

    if not os.path.isfile('.tsk/tskfile'):
        print "No tskfile database found."
        return False

    if args.command == "edit":
        parser = argparse.ArgumentParser(description='Opens text editor to edit task contents.')
        parser.add_argument('task_id', nargs='?', type=int, default=None)
        args = parser.parse_args(args.args)
        print fe.edit_task(args.task_id)
    elif args.command == "show":
        parser = argparse.ArgumentParser(description='Shows details of task.')
        parser.add_argument('task_id', type=int)
        args = parser.parse_args(args.args)
        print fe.show_task(args.task_id)
        skip_git = True
    elif args.command == "add":
        parser = argparse.ArgumentParser(description='Adds a new task.')
        parser.add_argument('summary')
        parser.add_argument('--description', default="")
        args = parser.parse_args(args.args)
        print fe.add_task(args.summary, args.description)
    elif args.command == "status":
        print fe.status()
        skip_git = True
    elif args.command == "closed":
        print fe.closed()
        skip_git = True
    elif args.command == "show_backlog":
        print fe.backlog()
        skip_git = True
    elif args.command == "block":
        parser = argparse.ArgumentParser(description='Changes state of task to blocked state.')
        parser.add_argument('task_id', type=int)
        parser.add_argument('reason')
        args = parser.parse_args(args.args)
        if tsk.set_blocked(args.task_id, args.reason):
            print "Task {:d} marked blocked.".format(args.task_id)
        else:
            print "Failed to mark task {:d} blocked.".format(args.task_id)
            ret = False
    elif args.command == "open":
        parser = argparse.ArgumentParser(description='Changes state of task to open state.')
        parser.add_argument('task_id', type=int)
        args = parser.parse_args(args.args)
        if tsk.set_open(args.task_id):
            print "Task {:d} opened.".format(args.task_id)
        else:
            print "Failed to open task {:d}.".format(args.task_id)
            ret = False
    elif args.command == "move":
        parser = argparse.ArgumentParser(description='Moves a task in the backlog to a new position (use +/- for relative).')
        parser.add_argument('task_id', type=int)
        parser.add_argument('new_pos')
        args = parser.parse_args(args.args)
        if args.new_pos[0] == '+' or args.new_pos[0] == '-':
            new_pos = int(args.new_pos[1:])
            new_pos = new_pos if args.new_pos[0] == '+' else new_pos*-1
            if tsk.set_backlog_position_relative(args.task_id, new_pos):
                if new_pos >= 0:
                    print "Task {:d} moved {:d} down.".format(args.task_id, new_pos)
                else:
                    print "Task {:d} moved {:d} up.".format(args.task_id, -1*new_pos)
            else:
                print "Failed to move task {:d}.".format(args.task_id)
                ret = False
        else:
            if tsk.set_backlog_position(args.task_id, int(args.new_pos)):
                print "Task {:d} moved to position {:d}.".format(args.task_id, int(args.new_pos))
            else:
                print "Failed to move task {:d}.".format(args.task_id)
                ret = False
    elif args.command == "activate":
        parser = argparse.ArgumentParser(description='Activates a task.')
        parser.add_argument('task_id', type=int)
        args = parser.parse_args(args.args)
        if tsk.set_active(args.task_id):
            print "Task {:d} activated.".format(args.task_id)
        else:
            print "Failed to activate task {:d}.".format(args.task_id)
            ret = False
    elif args.command == "close":
        parser = argparse.ArgumentParser(description='Changes state of task to closed state.')
        parser.add_argument('task_id', type=int)
        parser.add_argument('--r', default=None)
        args = parser.parse_args(args.args)
        if tsk.set_closed(args.task_id, args.r):
            print "Task {:d} closed.".format(args.task_id)
        else:
            print "Failed to close task {:d}.".format(args.task_id)
            ret = False
    elif args.command == "set_due_date":
        parser = argparse.ArgumentParser(description='Changes the due date of a task.')
        parser.add_argument('task_id', type=int)
        parser.add_argument('date')
        args = parser.parse_args(args.args)
        if args.date[0] == '+' or args.date[0] == '-':
            if tsk.set_due_date_relative(args.task_id, int(args.date)):
                print "Task {:d}'s due date has been set.".format(args.task_id)
            else:
                print "Task {:d} could not be found.".format(args.task_id)
                ret = False
        else:
            print fe.set_due_date(args.task_id, args.date)
            ret = False
    elif args.command == "remove_due_date":
        parser = argparse.ArgumentParser(description='Removes the due date of a task.')
        parser.add_argument('task_id', type=int)
        args = parser.parse_args(args.args)
        if tsk.remove_due_date(args.task_id):
            print "Task {:d}'s due date has been removed.".format(args.task_id)
        else:
            print "Task {:d} could not be found.".format(args.task_id)
            ret = False
    elif args.command == "time_estimate":
        parser = argparse.ArgumentParser(description='Sets the total estimate of work (in seconds) for this task.')
        parser.add_argument('task_id', type=int)
        parser.add_argument('estimate', type=int)
        args = parser.parse_args(args.args)
        if tsk.time_estimate(args.task_id, args.estimate):
            print "Estimate set for Task {:d}.".format(args.task_id)
        else:
            print "Task {:d} could not be found.".format(args.task_id)
            ret = False
    elif args.command == "time_log":
        parser = argparse.ArgumentParser(description="Record specified number of seconds towards a task's completion.")
        parser.add_argument('task_id', type=int)
        parser.add_argument('seconds', type=int)
        args = parser.parse_args(args.args)
        if tsk.time_log(args.task_id, args.seconds):
            print "Time recorded for Task {:d}.".format(args.task_id)
        else:
            print "Task {:d} could not be found.".format(args.task_id)
            ret = False
    elif args.command == "sort_backlog":
        parser = argparse.ArgumentParser(description="Sort backlog by due date.")
        parser.add_argument('-a', '--alphasort', action="store_true")
        args = parser.parse_args(args.args)
        tsk.sort_backlog(args.alphasort)
        print "Backlog sorted by due date."
    elif args.command == "start":
        print fe.start()
        skip_git = True
    elif args.command == "pause":
        print fe.pause()
        skip_git = True
    elif args.command == "cancel":
        print fe.cancel()
        skip_git = True
    elif args.command == "monitor":
        fe.monitor()
        skip_git = True
    elif args.command == "push":
        skip_git = True
        if git.push():
            print "Successfully pushed latest to remote."
        else:
            print "Failed to push latest to remote."
    elif args.command == "pull":
        skip_git = True
        if git.pull():
            print "Successfully pulled latest from remote."
        else:
            print "Failed to pull from remote."

    storage = StorageCls(time)
    storage.tasks = tsk.tasks
    storage.pomo = pomo
    storage.save('.tsk/tskfile')

    if not skip_git:
        git.commit()

    return ret
