#! /bin/bash
set -e

python FrontEnd.py
python Pomo.py
python Render.py
python Storage.py
python Task.py
python TaskFileParser.py
python TskLogic.py
python TskTest.py