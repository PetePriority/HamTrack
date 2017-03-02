import os
import time
from datetime import datetime
import logging
from logging.config import fileConfig

import RPi.GPIO as GPIO

from peewee import *
from playhouse.shortcuts import RetryOperationalError

from pyfcm import FCMNotification

# wheel circumference in cm
# e.g., for 2*r = 28cm, d = 2*pi*r
HAMSTER_WHEEL_CIRCUMFERENCE = 88
# min time between revolutions in ms
HAMSTER_DEBOUNCE = 250
# session timeout in s
HAMSTER_SESSION_TIMEOUT = 60

# GPIO init
GPIO_CHANNEL = 10
GPIO.setmode(GPIO.BCM)
GPIO.setup(GPIO_CHANNEL, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

# FCM stuff
push_service = FCMNotification(api_key="<FCM API KEY>")

# setup logging
logging.config.fileConfig(os.path.join(os.path.dirname(os.path.realpath(__file__)), 'logging_config.ini'))
logger = logging.getLogger(__name__)

# SQL stuff
SQL_HOST = '<SQL_HOST>'
SQL_DB = '<SQL_DB>'
SQL_USER = '<SQL_USER>'
SQL_PASSWORD = '<SQL_PASSWORD>'
mysql_db = MySQLDatabase(SQL_DB, host=SQL_HOST, user=SQL_USER, passwd=SQL_PASSWORD)

# Fallback file - written when sql fails
FALLBACK_FILE = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'fallback.log')

# SQL table structure
class BaseModel(Model):
    """A base model that will use our MySQL database"""
    class Meta:
        database = mysql_db

class Hamstersession(BaseModel):
    start = DateTimeField(unique=True, index=True)
    circumference = FloatField()
    duration = FloatField()
    distance = FloatField()

# Create table if it doesn't exist
if not Hamstersession.table_exists():
    Hamstersession.create_table()
    print('Table Hamstersession created')


# no. of revolutions
revolutions = 0
# timestamp
last_revo = 0
session_start = 0

def post_notification(data_message):
    result = push_service.notify_topic_subscribers(
        topic_name = "news",
        data_message = data_message
    )


def finish_session(session_end):
    wstart = datetime.fromtimestamp(session_start)
    wcircumference = HAMSTER_WHEEL_CIRCUMFERENCE
    wduration = session_end - session_start
    wdistance = revolutions * HAMSTER_WHEEL_CIRCUMFERENCE

    logger.info('Session finished')
    logger.info('Start: {0}'.format(wstart))
    logger.info('Duration: {0}s'.format(wduration))
    logger.info('Distance: {0}m'.format(wdistance/100.0))
    logger.info('Revolutions: {0}'.format(revolutions))

    data_message = {
        "event": "session_finished",
        "start": int(session_start*1000),
        "duration": "{0:.1f}".format(wduration/60.0),
        "distance": "{0:.1f}".format(wdistance/100.0),
        "revolutions": revolutions
    }
    post_notification(data_message=data_message)

    try:
        #mysql_db.connect()
        mysql_db.get_conn().ping(True)
        hamstersession = Hamstersession.create(
            start = wstart,
            circumference = wcircumference,
            duration = wduration,
            distance = wdistance)
        hamstersession.save()
        mysql_db.close()
    except Exception as e:
        logger.error('MySQL error: {0}'.format(e))
        with open(FALLBACK_FILE, 'a') as fd:
            fd.write('start: {0}\n'.format(wstart))
            fd.write('circumference: {0}\n'.format(wcircumference))
            fd.write('duration: {0}\n'.format(wduration))
            fd.write('distance: {0}\n'.format(wdistance))



def start_session(session_start):
    data_message = {
        "event": "session_started",
        "start": int(session_start*1000)
    }
    post_notification(data_message=data_message)


logger.info('HamTrack initialized')
# main loop
try:
    while 1:
        channel = GPIO.wait_for_edge(GPIO_CHANNEL,
                                     GPIO.RISING,
                                     timeout=HAMSTER_SESSION_TIMEOUT*1000)
        now = time.time()
        if channel is None:
            # Timeout: End session
            if revolutions >= 5:
                finish_session(now - HAMSTER_SESSION_TIMEOUT)
            if revolutions < 5 and session_start != 0:
                logger.info('Session aborted - no activity')
            revolutions = 0
            session_start = 0
        else:
            # Debounce
            if now - last_revo > HAMSTER_DEBOUNCE/1000.0:
                # Revolution detected
                logger.debug('Revolution detected. dt={0}'.format(now-last_revo))
                # Start new session if none is running
                last_revo = now
                if session_start == 0:
                    session_start = now
                    logger.info('Session started')
                else:
                    revolutions += 1
                if revolutions == 5:
                    start_session(session_start)

# except RuntimeError as e:
#    syslog.syslog(e)
except KeyboardInterrupt:
    pass

GPIO.cleanup()
