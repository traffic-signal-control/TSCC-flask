#!/usr/bin/env bash

set -e
pwd
# 日志文件
touch ./log/access_print.log
touch ./log/error_print.log
touch ./log/output_print.log
touch ./log/eval_print.log
pwd
ls -l

# exec flask init-db

cd ./evaluate/

exec python eval.py > ../log/eval_print.log &

cd ..

exec gunicorn app:app \
        -c ./gunicorn.conf.py \
        --bind 0.0.0.0:8000 \
        --workers 4 \
        --log-level debug \
        --access-logfile=log/access_print.log \
        --error-logfile=log/error_print.log  \
        > log/output_print.log

exec "$@"
