#!/usr/bin/python2.7
# -*- coding: utf-8 -*-

# SMS gateway
# send messages from the database (outbox)
# receive messages and save them in the database (inbox)
# x-f, 2016

import time
from pygsm import GsmModem
import pymysql.cursors
from time import gmtime, strftime
import os
import config


logfile = config.logfile
logfile_ping = config.logfile_ping

def logmsg(msg, file=logfile):
  
  logmsg = strftime("%Y-%m-%d %H:%M:%S", gmtime())
  logmsg = "[" + logmsg + "] " + str(msg)
  cmd = "echo \"" + logmsg + "\" >> " + file
  # print cmd
  os.system(cmd)
  

def connectDB():
  return pymysql.connect(
    host=config.db_host,
    user=config.db_user,
    password=config.db_password,
    db=config.db_db,
    charset=config.db_charset,
    cursorclass=pymysql.cursors.DictCursor
  )
  

class SmsGw(object):
    def __init__(self, modem):
        self.modem = modem

    def incoming(self, msg):

        logmsg("got incoming msg: ")
        logmsg("  sender: " + msg.sender.encode('utf-8'))
        logmsg("  text: " + msg.text.encode('utf-8'))
        logmsg("  sent: " + str(msg.sent))
        logmsg("  received: " + str(msg.received))
        #print "index:", msg.index

        # msg.respond("Received %d characters" % len(msg.text))
        

        # Connect to the database
        connection = connectDB()

        try:
            with connection.cursor() as cursor:
                # Create a new record
                sqlstr = """INSERT INTO 
                    `sms_inbox`
                  SET
                    `message` = %s,
                    `sender` = %s,
                    `received` = %s,
                    `sent` = %s
                  """
                cursor.execute(sqlstr, (msg.text.encode('utf-8'), msg.sender, msg.received, msg.sent))

            # connection is not autocommit by default. So you must commit to save
            # your changes.
            connection.commit()

        finally:
            connection.close()
            
            # delete this message, don't fill up the storage
            if msg.index is not None:
              print self.modem.command("AT+CMGD=" + msg.index + ",0")
              logmsg("AT+CMGD=" + msg.index + ",0")
              # pass


    def outgoing(self):
        # Connect to the database
        connection = connectDB()

        try:
            with connection.cursor() as cursor:
                # Read a single record
                sqlstr = """SELECT 
                    * 
                  FROM 
                    `sms_outbox` 
                  WHERE 
                    ts <= NOW()
                  ORDER BY 
                    ts ASC
                  """
                cursor.execute(sqlstr)
                result = cursor.fetchone()
                # print(result)
                
                if result is not None:
                  
                  sqlstr = """UPDATE
                      sms_outbox
                    SET
                      retries = retries + 1
                    WHERE
                      id = %s
                    LIMIT
                      1
                    """
                  cursor.execute(sqlstr, (result['id']))
                  connection.commit()

                  if result['retries'] < 4:
                    
                    # replace "00xxx" with "+xxx"
                    if result['recipient'][0:2] == "00":
                      result['recipient'] = "+" + result['recipient'][2:]
                    
                    logmsg("got outgoing msg (" + str(result['id']) + "): ")
                    logmsg("  rcpn: " + result['recipient'].encode('utf-8'))
                    logmsg("  text: " + result['message'].encode('utf-8'))
                    logmsg("  retr: " + str(result['retries']).encode('utf-8'))
                  
                    if gsm.send_sms(result['recipient'].encode(), result['message'].encode("utf-8")):
                      logmsg("msg sent")
                      
                      sqlstr = """INSERT INTO
                          sms_sent
                        SET
                          ts = %s,
                          recipient = %s,
                          message = %s,
                          ts_processed = NOW(),
                          status = 0,
                          error = ''
                        """
                      cursor.execute(sqlstr, (result['ts'], result['recipient'], result['message'].encode('utf-8')))
                      connection.commit()

                      sqlstr = """DELETE FROM
                          sms_outbox
                        WHERE
                          id = %s
                        LIMIT
                          1
                        """
                      cursor.execute(sqlstr, (result['id']))
                      connection.commit()
                
                    else:
                      logmsg("sending failed")
                  
                  else:
                    logmsg("retries exceeded")
                  
                    sqlstr = """INSERT INTO
                        sms_sent
                      SET
                        ts = %s,
                        recipient = %s,
                        message = %s,
                        ts_processed = NOW(),
                        status = 2,
                        error = 'retries exceeded'
                      """
                    cursor.execute(sqlstr, (result['ts'], result['recipient'], result['message'].encode('utf-8')))
                    connection.commit()

                    sqlstr = """DELETE FROM
                        sms_outbox
                      WHERE
                        id = %s
                      LIMIT
                        1
                      """
                    cursor.execute(sqlstr, (result['id']))
                    connection.commit()
                
        finally:
            connection.close()


              
    def serve_forever(self):
        while True:
            
            # ping = gsm.command("\x1B", write_term="")
            # # ping = gsm.command("\x1A", write_term="")
            # # print ping
            # self.modem._write("\x1B", raise_errors=False)
            # print("esc")
            # self.modem.command("\x1B", write_term="", raise_errors=False)
            # print("escaped")
            # cmd = "echo \"" + logmsg(ping) + "\" >> /dev/shm/sms-gw.log"
            # print cmd
            # os.system(cmd)

            ping = self.modem.command("AT")
            if ping and len(ping) > 0 and ping[0] == "OK":
              # print "responded"
              cmd = "touch \"" + logfile_ping + "\""
              os.system(cmd)
              pass
            else:
              print ping
              logmsg(ping)
            # logmsg(ping, file=logfile_ping)
            # cmd = "echo \"" + logmsg(ping) + "\" >> /dev/shm/sms-gw.log"
            # print cmd
            # os.system(cmd)
              
            # print "Checking for message..."
            msg = self.modem.next_message(ping=False)
            
            if msg is not None:
                print "Got Message: %r" % (msg)
                logmsg("Got Message: %r" % (msg))
                self.incoming(msg)


            # check for outgoing message
            self.outgoing()

            time.sleep(10)


logmsg("-----------------")
print("SMS-GW started")
logmsg("SMS-GW started")


print("connecting..")
logmsg("connecting..")

# all arguments to GsmModem.__init__ are optional, and passed straight
# along to pySerial. for many devices, this will be enough:
gsm = GsmModem(
    port=config.modem_port,
    baudrate=config.modem_baudrate
    # ,logger=GsmModem.logger
  )#.boot()

# Esc
gsm._write("\x1B")
time.sleep(2)
#ping = gsm.command("\x1B", write_term="", raise_errors=False)
#print "Esc=" + str(ping)
#logmsg("Esc=" + str(ping))

ping = gsm.command("ATZ")
print "ATZ=" + str(ping)
logmsg("ATZ=" + str(ping))

  
gsm.boot()

print("port opened")
logmsg("port opened")

# fix notifications on SIM900
# gsm.command("AT+CNMI=2,1,0,1,0", raise_errors=False)


print "Waiting for network..."
logmsg("Waiting for network...")
s = gsm.wait_for_network()
print "signal:", s
logmsg("signal: " + str(s))
# print gsm.hardware()
# print gsm.signal_strength()
# print gsm.network()


# start the GW app
app = SmsGw(gsm)
try:
  # gsm.ussd("+CUSD=1,\"*120#\"")
  app.serve_forever()
except KeyboardInterrupt:
  pass
gsm.disconnect()

print("\nSMS-GW stopped")
logmsg("SMS-GW stopped")
