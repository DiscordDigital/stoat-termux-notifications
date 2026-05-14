token="<insert token here>"

from stoat import Client, DMChannel
from time import time
import termux

lastDm = {}

class MyClient(Client):
    async def on_ready(self, _, /):
        print('Logged on as', self.me)

    async def on_message(self, message, /):
        global lastDm

        if isinstance(message.channel, DMChannel):
            target = message.channel.recipient or await client.fetch_user(message.channel.recipient_id)
            timeNow = time()
            if message.author_id != self.me.id:
                if target.name not in lastDm:
                    termux.Notification.notify(title=target.name + " — Stoat",content=message.content)
                    lastDm[target.name] = time()
                timeDiff = timeNow - lastDm[target.name]

                if timeDiff > 60:
                    termux.Notification.notify(title=target.name + " — Stoat",content=message.content)
                lastDm[target.name] = timeNow
            else:
                lastDm[target.name] = timeNow

client = MyClient(token=token,bot=False)
client.run()
