#! /usr/bin/python
from FrontEnd import TskFrontEnd
from Pomo import Pomo
from TaskFileParser import TaskFileParser
from Render import TskTextRender
from Render import PomoRender
from TskLogic import TskLogic
from Storage import Storage
import shutil
import argparse
import subprocess
import time
import os.path
import sys

tsk = TskLogic()
pomo = Pomo()

if os.path.exists('.tsk'):
    try:
        shutil.copyfile('.tsk/tskfile_backup', '/tmp/tskfile_backup')
    except:
        None
    shutil.copyfile('.tsk/tskfile', '.tsk/tskfile_backup')
    storage = Storage(time)
    if storage.load('.tsk/tskfile'):
        tsk.tasks = storage.tasks
        if storage.pomo:
            pomo = storage.pomo
    else:
        print 'Failed to load Tsk database file.'

fe = TskFrontEnd(tsk, pomo, TskTextRender(tsk), PomoRender(pomo), time, subprocess, TaskFileParser())

valid_commands = [ "edit_task",
                   "add_task",
                   "status",
                   "show_backlog",
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
                   "record_work",
                   "set_estimate" ]

parser = argparse.ArgumentParser(description='Self task management program.')
parser.add_argument('command',  choices=valid_commands)
parser.add_argument('args', nargs=argparse.REMAINDER)

skip_git = False

# TODO: Refactor to use subparsers

args = parser.parse_args()

if args.command == "init":
    if os.path.exists('.tsk'):
        print "Tsk already initialized"
        sys.exit(1)

    os.makedirs('.tsk')
    f = open('.tsk/tskfile', 'w+')
    f.close()

    proc = subprocess.Popen("git init .tsk/", shell=True, stdout=subprocess.PIPE)
    proc.wait()
    if proc.returncode != 0:
        print "Failed to create git repo."
        sys.exit(1)

    print 'Tsk initialized.'
    sys.exit(0)

if not os.path.exists('.tsk'):
    print "Tsk directory not found."
    sys.exit(1)

if not os.path.isfile('.tsk/tskfile'):
    print "No tskfile database found."
    sys.exit(1)

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
    args = parser.parse_args(args.args)
    print fe.close(args.task_id)
elif args.command == "set_due_date":
    parser = argparse.ArgumentParser(description='Changes the due date of a task.')
    parser.add_argument('task_id', type=int)
    parser.add_argument('date')
    args = parser.parse_args(args.args)
    if args.date[0] == '+' or args.date[0] == '-':
        print fe.set_due_date_relative(args.task_id, int(args.date))
    else:
        print fe.set_due_date(args.task_id, args.date)
elif args.command == "remove_due_date":
    parser = argparse.ArgumentParser(description='Removes the due date of a task.')
    parser.add_argument('task_id', type=int)
    args = parser.parse_args(args.args)
    print fe.remove_due_date(args.task_id)
elif args.command == "set_estimate":
    parser = argparse.ArgumentParser(description='Sets the total estimate of work (in pomos) for this task.')
    parser.add_argument('task_id', type=int)
    parser.add_argument('estimate', type=int)
    args = parser.parse_args(args.args)
    print fe.set_estimate(args.task_id, args.estimate)
elif args.command == "record_work":
    parser = argparse.ArgumentParser(description="Record a completed pomo towards a task's completion.")
    parser.add_argument('task_id', type=int)
    args = parser.parse_args(args.args)
    print fe.record_work(args.task_id)
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

storage = Storage(time)
storage.tasks = tsk.tasks
storage.pomo = pomo
storage.save('.tsk/tskfile')
if not skip_git:
    proc = subprocess.Popen("cd .tsk && git add tskfile && git commit -m 'Updates tskfile.'", shell=True, stdout=subprocess.PIPE)
    proc.wait()
# if proc.returncode != 0:
#     print "Failed to update Tsk's git repo."
