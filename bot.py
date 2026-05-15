from dotenv import load_dotenv
from os import getenv
from stoat import Client, DMChannel, GroupChannel, TextChannel
from time import time
import termux

load_dotenv()

token = getenv('token')
mentionNotifications = bool(getenv('mentionNotifications'))
dmNotifications = bool(getenv('dmNotifications'))
groupChannelNotifications = bool(getenv('groupChannelNotifications'))
notificationBuffer = int(getenv('notificationBuffer'))

channelTracker = {}

def send_notification(**kwargs):    
    if kwargs['notificationType'] == "dm":
        termux.Notification.notify(title=kwargs['name'] + \
        " — Stoat",content=kwargs['content'],kwargs={"id":kwargs['nonce']})
    if kwargs['notificationType'] == "groupChannel":
        termux.Notification.notify(title=kwargs['groupChannelName'] + \
        " — Stoat",content=kwargs['name'] + ": " + kwargs['content'],kwargs={"id":kwargs['nonce']})
    if kwargs['notificationType'] == "textChannel":
        termux.Notification.notify(title=kwargs['name'] + " in " + \
        kwargs['serverName'] + " — Stoat",content=kwargs['content'],kwargs={"id":kwargs['nonce']})

class MyClient(Client):
    async def on_ready(self, _, /):
        print('Logged on as', self.me)

    async def on_message(self, message, /):
        global channelTracker
        global mentionNotifications
        global dmNotifications
        global groupChannelNotifications
        sendNotification = False
        newConversation = False
        dmChannel = False
        groupChannel = False
        textChannel = False

        # channel ping
        if isinstance(message.channel, DMChannel) and dmNotifications:
            dmChannel = True
            sendNotification = True

        if isinstance(message.channel, GroupChannel) and groupChannelNotifications:
            groupChannel = True
            sendNotification = True
        
        if isinstance(message.channel, TextChannel):
            textChannel = True

        if mentionNotifications:
            if client.user.id in message.mention_ids:
                target = message.author or await message.get_author()
                if dmChannel:
                    send_notification(name=target.name,
                                      content=message.content,
                                      notificationType="dm",
                                      nonce=message.author.id)
                elif groupChannel:
                    send_notification(name=target.name,
                                      content=message.content,
                                      notificationType="groupChannel",
                                      groupChannelName=message.channel.name,
                                      nonce=message.channel.id)
                elif textChannel:
                    send_notification(name=target.name,
                                      content=message.content,
                                      notificationType="textChannel",
                                      serverName=message.server.name,
                                      nonce=message.id)
                return
        
        if sendNotification == True:
            target = message.author or await message.get_author()
            timeNow = int(time())
            if message.author_id != self.me.id:
                if message.channel.id not in channelTracker:
                    newConversation = True
                    channelTracker[message.channel.id] = timeNow
                
                timeDiff = timeNow - channelTracker[message.channel.id]
                print(str(timeDiff))

                if timeDiff > notificationBuffer or newConversation:
                    if dmChannel:
                        send_notification(name=target.name,
                                          content=message.content,
                                          notificationType="dm",
                                          nonce=message.author.id)
                    elif groupChannel:
                        send_notification(name=target.name,
                                          content=message.content,
                                          notificationType="groupChannel",
                                          groupChannelName=message.channel.name,
                                          nonce=message.channel.id)
                channelTracker[message.channel.id] = timeNow
            else:
                channelTracker[message.channel.id] = timeNow

if token == "<insert token>":
    print("Please edit .env and insert your token.")
    exit(1)

client = MyClient(token=token,bot=False)
client.run()
