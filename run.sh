#!/usr/bin/env bash

set -e
pwd
# 日志文件
touch /var/hua_home/workspace/log/access_print.log
touch /var/hua_home/workspace/log/error_print.log
touch /var/hua_home/workspace/log/output_print.log
touch /var/hua_home/workspace/log/eval_print.log
pwd
ls -l

# exec flask init-db

cd /var/hua_home/workspace/evaluate/

exec python eval.py > /var/hua_home/workspace/log/eval_print.log &

cd /var/hua_home/workspace/

exec gunicorn app:app \
        -c /var/hua_home/workspace/gunicorn.conf.py \
        --bind 0.0.0.0:8000 \
        --workers 4 \
        --log-level debug \
        --access-logfile=/var/hua_home/workspace/log/access_print.log \
        --error-logfile=/var/hua_home/workspace/log/error_print.log
exec "$@"
