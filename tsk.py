#! /usr/bin/python
from FrontEnd import TskFrontEnd
from Pomo import Pomo
from TaskFileParser import TaskFileParser
from Render import TskTextRender
from Render import PomoRender
from TskLogic import TskLogic
from Storage import Storage
import argparse
import subprocess
import time
import os.path

tsk = TskLogic()
pomo = Pomo()

if os.path.isfile('.tskfile'):
    storage = Storage(time)
    if storage.load('.tskfile'):
        tsk.tasks = storage.tasks
        if storage.pomo:
            pomo = storage.pomo

fe = TskFrontEnd(tsk, pomo, TskTextRender(tsk), PomoRender(pomo), time, subprocess, TaskFileParser())

valid_commands = [ "edit_task",
                   "add_task",
                   "status",
                   "backlog",
                   "activate",
                   "block",
                   "open",
                   "close",
                   "start",
                   "pause",
                   "cancel" ]

parser = argparse.ArgumentParser(description='Self task management program.')
parser.add_argument('command',  choices=valid_commands)
parser.add_argument('args', nargs=argparse.REMAINDER)

# TODO: Refactor to use subparsers

args = parser.parse_args()

if args.command == "edit_task":
    parser = argparse.ArgumentParser(description='Opens text editor to edit task contents.')
    parser.add_argument('task_id', type=int)
    args = parser.parse_args(args.args)
    print args
    print fe.edit_task(args.task_id)
elif args.command == "add_task":
    parser = argparse.ArgumentParser(description='Adds a new task.')
    parser.add_argument('summary')
    parser.add_argument('--description', default="")
    args = parser.parse_args(args.args)
    print args
    print fe.add_task(args.summary, args.description)
elif args.command == "status":
    print fe.status()
elif args.command == "backlog":
    print fe.backlog()
elif args.command == "block":
    parser = argparse.ArgumentParser(description='Changes state of task to blocked state.')
    parser.add_argument('task_id', type=int)
    parser.add_argument('reason')
    args = parser.parse_args(args.args)
    print args
    print fe.block(args.task_id, args.reason)
elif args.command == "open":
    parser = argparse.ArgumentParser(description='Changes state of task to open state.')
    parser.add_argument('task_id', type=int)
    args = parser.parse_args(args.args)
    print args
    print fe.open(args.task_id)
elif args.command == "activate":
    parser = argparse.ArgumentParser(description='Activates a task.')
    parser.add_argument('task_id', type=int)
    args = parser.parse_args(args.args)
    print args
    print fe.activate(args.task_id)
elif args.command == "close":
    parser = argparse.ArgumentParser(description='Changes state of task to closed state.')
    parser.add_argument('task_id', type=int)
    args = parser.parse_args(args.args)
    print args
    print fe.close(args.task_id)
elif args.command == "start":
    print fe.start()
elif args.command == "pause":
    print fe.pause()
elif args.command == "cancel":
    print fe.cancel()

storage = Storage(time)
storage.tasks = tsk.tasks
storage.pomo = pomo
storage.save('.tskfile')
