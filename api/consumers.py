import uuid
from channels import Group

from .models import Trial

def ws_connect(message):
    accept = False
    try:
        trialId = uuid.UUID(message.content['path'].replace('/', ''))
        if (Trial.objects.filter(pk=trialId).exists()):
            Group(str(trialId)).add(message.reply_channel)
            accept = True
    except ValueError as e:
        pass
    finally:
        message.reply_channel.send({"accept": accept})

def ws_disconnect(message):
    pass
    # Group("simulation").discard(message.reply_channel)
    # Group(str(trialId)).add(message.reply_channel)
