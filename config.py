import os

# modem params
modem_port="/dev/ttyUSB0"
modem_baudrate = 19200

# MySQL params
db_host = 'localhost'
db_user = 'user'
db_password = 'password'
db_db = 'db'
db_charset = 'utf8mb4'

logfile = os.path.dirname(os.path.abspath(__file__)) + '/sms-gw.log'
logfile_ping = '/dev/shm/sms-gw-ping.log'
