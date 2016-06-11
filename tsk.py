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

if os.path.isfile('.tskfile'):
    shutil.copyfile('.tskfile', '.tskfile_backup')
    storage = Storage(time)
    if storage.load('.tskfile'):
        tsk.tasks = storage.tasks
        if storage.pomo:
            pomo = storage.pomo

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
                   "init" ]

parser = argparse.ArgumentParser(description='Self task management program.')
parser.add_argument('command',  choices=valid_commands)
parser.add_argument('args', nargs=argparse.REMAINDER)

# TODO: Refactor to use subparsers

args = parser.parse_args()

if args.command == "init":
    f = open('.tskfile', 'w+')
    f.close()
    print 'Tsk initialized.'
    sys.exit(0)

if not os.path.isfile('.tskfile'):
    print "No .tskfile database found."
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
elif args.command == "add_task":
    parser = argparse.ArgumentParser(description='Adds a new task.')
    parser.add_argument('summary')
    parser.add_argument('--description', default="")
    args = parser.parse_args(args.args)
    print fe.add_task(args.summary, args.description)
elif args.command == "status":
    print fe.status()
elif args.command == "closed":
    print fe.closed()
elif args.command == "show_backlog":
    print fe.backlog()
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
elif args.command == "start":
    print fe.start()
elif args.command == "pause":
    print fe.pause()
elif args.command == "cancel":
    print fe.cancel()
elif args.command == "monitor":
    fe.monitor()

storage = Storage(time)
storage.tasks = tsk.tasks
storage.pomo = pomo
storage.save('.tskfile')
os.remove('.tskfile_backup')
