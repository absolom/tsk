#! /bin/bash

python FrontEnd.py || exit 1
python Pomo.py || exit 1
python Render.py || exit 1
python Storage.py || exit 1
python Task.py || exit 1
python TaskFileParser.py || exit 1
python TskLogic.py || exit 1
