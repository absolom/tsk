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

    valid_commands = [ "edit_task",
                       "add_task",
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
                       "show_task",
                       "init",
                       "set_due_date",
                       "remove_due_date",
                       "time_estimate",
                       "time_log" ]

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

    if args.command == "edit_task":
        parser = argparse.ArgumentParser(description='Opens text editor to edit task contents.')
        parser.add_argument('task_id', type=int)
        args = parser.parse_args(args.args)
        print fe.edit_task(args.task_id)
    elif args.command == "show_task":
        parser = argparse.ArgumentParser(description='Shows details of task.')
        parser.add_argument('task_id', type=int)
        args = parser.parse_args(args.args)
        print fe.show_task(args.task_id)
        skip_git = True
    elif args.command == "add_task":
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
        print fe.block(args.task_id, args.reason)
    elif args.command == "open":
        parser = argparse.ArgumentParser(description='Changes state of task to open state.')
        parser.add_argument('task_id', type=int)
        args = parser.parse_args(args.args)
        print fe.open(args.task_id)
    elif args.command == "move":
        parser = argparse.ArgumentParser(description='Moves a task in the backlog to a new position (use +/- for relative).')
        parser.add_argument('task_id', type=int)
        parser.add_argument('new_pos')
        args = parser.parse_args(args.args)
        if args.new_pos[0] == '+' or args.new_pos[0] == '-':
            print fe.set_position_relative(args.task_id, int(args.new_pos))
        else:
            print fe.set_position(args.task_id, int(args.new_pos))
    elif args.command == "activate":
        parser = argparse.ArgumentParser(description='Activates a task.')
        parser.add_argument('task_id', type=int)
        args = parser.parse_args(args.args)
        print fe.activate(args.task_id)
    elif args.command == "close":
        parser = argparse.ArgumentParser(description='Changes state of task to closed state.')
        parser.add_argument('task_id', type=int)
        parser.add_argument('--r', default=None)
        args = parser.parse_args(args.args)
        print fe.close(args.task_id, args.r)
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
        print fe.remove_due_date(args.task_id)
    elif args.command == "time_estimate":
        parser = argparse.ArgumentParser(description='Sets the total estimate of work (in seconds) for this task.')
        parser.add_argument('task_id', type=int)
        parser.add_argument('estimate', type=int)
        args = parser.parse_args(args.args)
        print fe.time_estimate(args.task_id, args.estimate)
    elif args.command == "time_log":
        parser = argparse.ArgumentParser(description="Record specified number of seconds towards a task's completion.")
        parser.add_argument('task_id', type=int)
        parser.add_argument('seconds', type=int)
        args = parser.parse_args(args.args)
        print fe.time_log(args.task_id, args.seconds)
    elif args.command == "sort_backlog":
        parser = argparse.ArgumentParser(description="Sort backlog by due date.")
        parser.add_argument('-a', '--alphasort', action="store_true")
        args = parser.parse_args(args.args)
        print fe.sort_backlog(args.alphasort)
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

    storage = StorageCls(time)
    storage.tasks = tsk.tasks
    storage.pomo = pomo
    storage.save('.tsk/tskfile')

    if not skip_git:
        git.commit()

    return ret