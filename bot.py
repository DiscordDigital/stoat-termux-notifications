from dotenv import load_dotenv
from os import getenv
from stoat import Client, DMChannel, GroupChannel, TextChannel
from time import time
import termux
import re

load_dotenv()

token = getenv('token')
mentionNotifications = bool(getenv('mentionNotifications'))
dmNotifications = bool(getenv('dmNotifications'))
groupChannelNotifications = bool(getenv('groupChannelNotifications'))
notificationBuffer = int(getenv('notificationBuffer'))

channelTracker = {}

async def send_notification(**kwargs):
    attachments = kwargs['attachments']
    client = kwargs['client']
    content = kwargs['content']
    name = kwargs['name']
    nonce = kwargs['nonce']
    notificationType = kwargs['notificationType']

    pattern = re.compile(r'\:(.*?[^ ])\:', flags=re.DOTALL)
    matches = pattern.findall(content)

    if len(matches) > 0:
        for id in matches:
            try:
                emoji = await client.fetch_emoji(id)
                content = content.replace(":"+id+":", ":"+emoji.name+":")
            except Exception:
                pass

    if len(attachments) > 0:
        attachmentFilenames = [attachment.filename for attachment in attachments]
        content = "<" + ", ".join(attachmentFilenames) + "> " + content

    if notificationType == "dm":
        termux.Notification.notify(title=name + \
        " — Stoat",content=content,kwargs={"id":nonce})
    if notificationType == "groupChannel":
        termux.Notification.notify(title=kwargs['groupChannelName'] + \
        " — Stoat",content=name + ": " + content,kwargs={"id":nonce})
    if notificationType == "textChannel":
        termux.Notification.notify(title=name + " in " + \
        kwargs['serverName'] + " — Stoat",content=content,kwargs={"id":nonce})

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
                    await send_notification(name=target.name,
                                            content=message.content,
                                            notificationType="dm",
                                            nonce=message.author.id,
                                            attachments=message.attachments,
                                            client=client)
                elif groupChannel:
                    await send_notification(name=target.name,
                                            content=message.content,
                                            notificationType="groupChannel",
                                            groupChannelName=message.channel.name,
                                            nonce=message.channel.id,
                                            attachments=message.attachments,
                                            client=client)
                elif textChannel:
                    await send_notification(name=target.name,
                                            content=message.content,
                                            notificationType="textChannel",
                                            serverName=message.server.name,
                                            nonce=message.id,
                                            attachments=message.attachments,
                                            client=client)
                return

        if sendNotification == True:
            target = message.author or await message.get_author()
            timeNow = int(time())
            if message.author_id != self.me.id:
                if message.channel.id not in channelTracker:
                    newConversation = True
                    channelTracker[message.channel.id] = timeNow

                timeDiff = timeNow - channelTracker[message.channel.id]

                if timeDiff >= notificationBuffer or newConversation:
                    if dmChannel:
                        await send_notification(name=target.name,
                                                content=message.content,
                                                notificationType="dm",
                                                nonce=message.author.id,
                                                attachments=message.attachments,
                                                client=client)
                    elif groupChannel:
                        await send_notification(name=target.name,
                                                content=message.content,
                                                notificationType="groupChannel",
                                                groupChannelName=message.channel.name,
                                                nonce=message.channel.id,
                                                attachments=message.attachments,
                                                client=client)
                channelTracker[message.channel.id] = timeNow
            else:
                channelTracker[message.channel.id] = timeNow

if token == "<insert token>":
    print("Please edit .env and insert your token.")
    exit(1)

client = MyClient(token=token,bot=False)
client.run()
