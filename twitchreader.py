import twitch
import time

data = {}
settings = {}
window = ''

def init(data_dict, config, win):
    global data, settings, window
    data = data_dict
    settings = config
    window = win

    try:
        chat = twitch.Chat(channel='#' + settings['twitch']['channel'],
                            nickname='bot',
                            oauth=settings['twitch']['oauth'],
                            helix= twitch.Helix(settings['twitch']['client-id'], settings['twitch']['client-secret']))
        
        chat.subscribe(onMessage)
    except KeyError:
        print("Twitch Credentials need to be setup")

def onMessage(message: twitch.chat.Message) -> None:
    updateChatbox(message.sender, message.text)

def updateChatbox(sender, msg):
    window.write_event_value('-CHAT-', {'sender': sender, 'msg':msg})