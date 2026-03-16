#!/bin/sh
export PYTHONPATH=/Users/peteromalley/Documents/desloppify${PYTHONPATH:+:$PYTHONPATH}
exec /Users/peteromalley/.pyenv/versions/3.11.11/bin/python -m desloppify.cli "$@"
