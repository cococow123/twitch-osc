import twitch

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
        
        chat.subscribe(on_message)
    except KeyError:
        print("Twitch Credentials need to be setup")

def on_message(message: twitch.chat.Message) -> None:
    update_chatbox(message.sender, message.text)

def update_chatbox(sender, msg):
    window.write_event_value('-CHAT-', {'sender': sender, 'msg':msg})