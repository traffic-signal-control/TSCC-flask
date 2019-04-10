From gpu-conda-vnc-sim

ADD flaskr /var/hua_home/workspace/flaskr
ADD evaluate /var/hua_home/workspace/evaluate
ADD run.sh /var/hua_home/workspace/ 
ADD app.py /var/hua_home/workspace/
ADD Dockerfile /var/hua_home/workspace/
ADD gunicorn.conf.py /var/hua_home/workspace/
ADD requirements.txt /var/hua_home/workspace/


RUN pip install flask gunicorn gevent Flask-Mail Flask-WTF flask_talisman



RUN mkdir -p /var/hua_home/workspace/log/
RUN chmod +x /var/hua_home/workspace/run.sh


VOLUME /var/hua_home/workspace


ENTRYPOINT ["./run.sh"]

EXPOSE 8000
