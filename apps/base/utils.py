from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer


def send_progress_websocket(group_name, message):
    """
    Send a message to the websocket
    """
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        group_name,
        message,
    )
