# export GOOGLE_APPLICATION_CREDENTIALS=/Users/marcel/tmp/google-cloud-porteiro.json

import time
import os
import json
from google.cloud import pubsub_v1

# Operator id 0 is System Engineer
OPERATOR_ID = 0 
# Default Net2 password
OPERATOR_PWD = os.environ['OPERATOR_PWD'] 
# When running on the machine where Net2 is installed
NET2_SERVER = os.environ['NET2_SERVER']

GOOGLE_CLOUD_PROJECT = "hk2019-project-3"
PUBSUB_TOPIC="porteiro"
PUBSUB_SUBSCRIPTION="porteiro_subscription"


def handle(message):
    print("payload %s" % message.data)

    # parse json
    msg = json.loads(message.data)

    if "first_name" not in msg:
        message.ack()
        return

    from Net2Scripting import init_logging
    from Net2Scripting.net2xs import Net2XS
    from Net2Scripting.pylog4net import Log4Net
    with Net2XS(NET2_SERVER) as net2:
        net2.authenticate(OPERATOR_ID, OPERATOR_PWD)
        # find user by name
        user_id = net2.get_user_id_by_name((msg["first_name"], msg["last_name"]))
        print("Found user id %d" % (user_id))

        # Found a valid user id
        if user_id >= 0:
            # TODO check if user can open door
            open_door(msg["door"])
        
    message.ack()

def open_door(door):
    from Net2Scripting import init_logging
    from Net2Scripting.net2xs import Net2XS
    from Net2Scripting.pylog4net import Log4Net
    with Net2XS(NET2_SERVER) as net2:
        # Authenticate
        net2.authenticate(OPERATOR_ID, OPERATOR_PWD)

        if not net2.hold_door_open(door):
            print(
                "Failed to hold door %s open: %s." %
                (door, net2.last_error_message))
        else:
            print("Set door %s open." % (door))

        time.sleep(3)

        if not net2.close_door(door):
            print(
                "Failed to close door %s: %s." %
                (door, net2.last_error_message))
        else:
            print("Set door %s closed." % (door))

if __name__ == "__main__":

    import os
    print(os.environ['GOOGLE_APPLICATION_CREDENTIALS'])


    subscriber = pubsub_v1.SubscriberClient()
    topic_name = 'projects/{project_id}/topics/{topic}'.format(
        project_id=GOOGLE_CLOUD_PROJECT,
        topic='porteiro',
    )
    subscription_name = 'projects/{project_id}/subscriptions/{sub}'.format(
        project_id=GOOGLE_CLOUD_PROJECT,
        sub='porteiro-subscription',
    )

    future = subscriber.subscribe(subscription_name, handle)


    import http.server
    import socketserver

    PORT = 8080
    Handler = http.server.SimpleHTTPRequestHandler

    with socketserver.TCPServer(("", PORT), Handler) as httpd:
        print("serving at port", PORT)
        httpd.serve_forever()
