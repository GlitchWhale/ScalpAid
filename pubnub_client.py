# Based on class IoT_23_sd3b code, adapted for ScalpAid

from pubnub.pnconfiguration import PNConfiguration
from pubnub.pubnub import PubNub
import os

PUBNUB_PUBLISH_KEY = os.getenv("PUBNUB_PUBLISH_KEY", "demo")
PUBNUB_SUBSCRIBE_KEY = os.getenv("PUBNUB_SUBSCRIBE_KEY", "demo")
PUBNUB_CHANNEL = os.getenv("PUBNUB_CHANNEL", "scalpaid_sensor_stream")

pnconfig = PNConfiguration()
pnconfig.publish_key = PUBNUB_PUBLISH_KEY
pnconfig.subscribe_key = PUBNUB_SUBSCRIBE_KEY
pnconfig.ssl = True
pnconfig.uuid = "flask-server"


pubnub = PubNub(pnconfig)


def publish_sensor_data(message):
    """Publish a message to the ScalpAid PubNub channel."""
    try:
        envelope = pubnub.publish().channel(PUBNUB_CHANNEL).message(message).sync()
        if envelope.status.is_error():
            print("[PubNub ERROR]", envelope.status.error_data)
        else:
            print(f"[PubNub] Published to {PUBNUB_CHANNEL}: {message}")
    except Exception as e:
        print("[PubNub Exception]", e)
