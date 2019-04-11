import flaskr
import logging
import logging.handlers
import sys

app = flaskr.create_app()


app.debug = True
handler = logging.StreamHandler(sys.stdout)
logging_format = logging.Formatter('%(asctime)s - %(levelname)s - %(filename)s - %(lineno)s - %(message)s')
handler.setFormatter(logging_format)

file_handler = logging.handlers.RotatingFileHandler('./log/output_print.log', maxBytes=10*1024*1024, backupCount=9)
file_handler.setLevel(logging.DEBUG)
file_handler.setFormatter(logging_format)
app.logger.addHandler(file_handler)
app.logger.addHandler(handler)


if __name__ == '__main__':
    # from werkzeug.contrib.fixers import ProxyFix
    # app.wsgi_app = ProxyFix(app.wsgi_app)
    app.run(host='0.0.0.0', port=8000)
    # app.run(debug=True)
    # gunicorn app:app -c gunicorn.conf.py -w 4 -b 127.0.0.1:4000
