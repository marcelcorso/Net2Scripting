import time
import os
import json
from google.cloud import pubsub_v1
from Net2Scripting import init_logging
from Net2Scripting.net2xs import Net2XS
from Net2Scripting.pylog4net import Log4Net

# Operator id 0 is System Engineer
OPERATOR_ID = 0
# Default Net2 password
OPERATOR_PWD = "net2"
# When running on the machine where Net2 is installed
NET2_SERVER = "localhost"

GOOGLE_CLOUD_PROJECT = "hk2019-project-3"

def handle(message):

    # parse json
    msg = json.loads(message.data)

    # find user by name
    user_id = net2.get_user_id_by_name((FIRST_NAME, SUR_NAME))
    print("Found user id %d" % (user_id))

    # Found a valid user id
    if user_id >= 0:
        # TODO check if user can open door

        with Net2XS(NET2_SERVER) as net2:
            # Authenticate
            net2.authenticate(OPERATOR_ID, OPERATOR_PWD)

            if not net2.hold_door_open(door):
                print(
                    "Failed to hold door %d open: %s." %
                    (door, net2.last_error_message))
            else:
                print("Set door %d open." % (door))

    message.ack()

if __name__ == "__main__":

    subscriber = pubsub_v1.SubscriberClient()
    topic_name = 'projects/{project_id}/topics/{topic}'.format(
        project_id=GOOGLE_CLOUD_PROJECT,
        topic='porteiro',
    )
    subscription_name = 'projects/{project_id}/subscriptions/{sub}'.format(
        project_id=GOOGLE_CLOUD_PROJECT,
        sub='porteiro-subscription',
    )
    subscriber.create_subscription(
        name=subscription_name, topic=topic_name)

    future = subscriber.subscribe(subscription_name, handle)

