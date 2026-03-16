#!/bin/sh
export PYTHONPATH=/Users/peteromalley/Documents/desloppify${PYTHONPATH:+:$PYTHONPATH}
exec /Users/peteromalley/.pyenv/versions/3.11.11/bin/python3 -m desloppify.cli "$@"
