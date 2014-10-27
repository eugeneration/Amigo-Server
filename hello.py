from flask import Flask
app = Flask(__name__)

####################################################
###### FROM SCRIPT.PY
####################################################
#!/usr/bin/python
import sys, json, time, random, string, xmpp

SERVER = 'gcm.googleapis.com'
PORT = 5235
USERNAME = "596039776570"
PASSWORD = "AIzaSyCGZhlSrNd6gz1JVU1errLhBTSbsYYohdU"

#Eugene
# ANDROID = "APA91bH2pbQD5TPGP75v31ADfU5Vb2jcel3Dy2BMWE9Vv1gZg2Oboxsd_h0fz3raBBEcVrpDxLoGhiLHDsSPPF7yGj7pEmN4RdwdIyK_TUgyVsnV5UH_qiLaFZq4VpE5Zc9mx3HgGYlLKsY_vhuvIxs8fxT2pzCGIQ"
# CHROME = "APA91bHnYuSEo98qTqTE86ALKj1KY77bZjkDFKvFVeMx0nqsDh4_8lj9sZi1bx6ViGIhCQEongxFZNc0n7-X0noh1lw1hZCG3rQVcdD1sQ6SEEVX4gqCuUpAsB_KBOQCjTFQMKKG5-TXqWUYprlvG4aHGf5A54pLJw"

#STEPHENY
ANDROID = "APA91bGzZ2HrvaZujm9LPDdidVheisf16B7MKqBpnfqOk2BVyz3tW6qZ8PAWEo1Li_eAvFYToIAiTnEBbFr6-DYVuHDYXbqy3Gem8sJ6ey81GUufWXepaHYBsavhcmflR6-J-604DIo0gXC9l80rZJSZlcCPBAQlqw"
CHROME = "APA91bGgGseq3R0ffg3uZApRv4R3j0cXjuytqSgmB3H4tUIbCgZwmbbhcj13GwDC7S9RCjhkbkR2FvdhRkPpXdfd7QUMqH9MC4VQlhMJfKiSDBM0_jRaCUHTR3-hBPSPQwnAdGBQmaJHpnPgE8JygFFSS4SZdibYeQ"

TARGET = "target";
TYPE = "type";
ACTION = "action";
MESSAGETYPE = "messagetype";
STATUS = "updatestatus";
TITLE = "title";

MESSAGETYPE_ACTION = "action";
MESSAGETYPE_UPDATE = "update";

unacked_messages_quota = 100
send_queue = []
print 'before'
client = xmpp.Client('gcm.googleapis.com', debug=['socket'])
client.connect(server=(SERVER,PORT), secure=1, use_srv=False)
print 'i iz here'
# Return a random alphanumerical id
def random_id():
  rid = ''
  for x in range(8): rid += random.choice(string.ascii_letters + string.digits)
  return rid

def message_callback(session, message):
  global unacked_messages_quota
  gcm = message.getTags('gcm')
  if gcm:
    gcm_json = gcm[0].getData()
    msg = json.loads(gcm_json)
    
    #=====================================================================
    # ACTUAL MESSAGES
    if not msg.has_key('message_type'):
        
      # Acknowledge the incoming message immediately.
      send({'to': msg['from'],
            'message_type': 'ack',
            'message_id': msg['message_id'],
            })
                
      # Queue a response
      if msg.has_key('from'):
        # ensure the message is correctly formatted
        if msg.has_key('data') and msg['data'].has_key(MESSAGETYPE):
          data = msg['data']
          #--------------------------------------------------------------
          # for action messages (android to chrome):
          if data[MESSAGETYPE] == MESSAGETYPE_ACTION:
            if not (data.has_key(TYPE) and data.has_key(TARGET) and data.has_key(ACTION)):
              print "Poorly formatted ACTION message."
              return
            
            # send to the other device - if unknown device, echo back.
            # if msg['from'] == ANDROID:
            #   sendTo = CHROME
            # elif msg['from'] == CHROME:
            #   sendTo = ANDROID
            # else:
            #   sendTo = msg['from']

            data['message_destination'] = 'RegId'
            # Route the message to the other app.
            send_queue.append({'to': CHROME,#'to': sendTo,
                               'message_id': random_id(),
                               'data': data})
          #--------------------------------------------------------------
          # for update messages (chrome to android)
          elif data[MESSAGETYPE] == MESSAGETYPE_UPDATE:
            if not (data.has_key(TARGET) and data.has_key(STATUS) and data.has_key(TITLE)):
              print "Poorly formatted UPDATE message."
              return

            # Route the message to the other app.
            send_queue.append({'to': ANDROID,#'to': sendTo,
                               'message_id': random_id(),
                               'data': data})
            
          #--------------------------------------------------------------
          # other types of messages
          else:
            print "non ACTION message"
          
    #=====================================================================
    # NACK type responses
    elif msg['message_type'] == 'ack' or msg['message_type'] == 'nack':
      unacked_messages_quota += 1

def send(json_dict):
  template = ("<message><gcm xmlns='google:mobile:data'>{1}</gcm></message>")
  client.send(xmpp.protocol.Message(
      node=template.format(client.Bind.bound[0], json.dumps(json_dict))))

def flush_queued_messages():
  global unacked_messages_quota
  while len(send_queue) and unacked_messages_quota > 0:
    send(send_queue.pop(0))
    unacked_messages_quota -= 1

####################################################


@app.route('/')
def hello_world():
  print 'in hello world method'
  # client = xmpp.Client('gcm.googleapis.com', debug=['socket'])

  client.RegisterHandler('message', message_callback)
  send_queue.append({'to': ANDROID,
                     'message_id': 'reg_id',
                     'data': {'title': 'Poop', 'message_destination': 'RegId',
                              'message_id': random_id()}})

  #while True:
  client.Process(1)
  flush_queued_messages()

  send_queue.append({'to': ANDROID,
                   'message_id': 'reg_id',
                   'data': {'title': 'Poop', 'message_destination': 'RegId',
                            'message_id': random_id()}})
  return 'Sent a message to Android!'

if __name__ == '__main__':
    print 'in main'
    auth = client.auth(USERNAME, PASSWORD)
    if not auth:
      print 'Authentication failed!'
      sys.exit(1)
    app.run()