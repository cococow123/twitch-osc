####################-   IMPORTS   -#######################

import PySimpleGUI as sg
import json
import csv
import os.path
import threading
from collections import defaultdict

import twitchreader
import oscclient

###################-   SETTINGS   -#######################
config = {'twitch': 
            {'channel': '', 
            'oauth': '', 
            'client-id': '',
            'client-secret': ''}, 
        'osc': {
            'ip': '0.0.0.0', 
            'port': '25575'}, 
        'gui': {'theme': 'Reds'}}

# -   LOAD SETTINGS


def load_settings():
    global config
    if(os.path.exists('config.json')):
        with open('config.json', "r") as infile:
            config = json.load(infile)
            infile.close()

# -   SAVE SETTINGS


def save_settings():
    with open('config.json', 'w') as outfile:
        json.dump(config, outfile, indent=2)
        outfile.close()


###################-   COMMANDS   -#######################
data_dict = {}
data = []
headings = ['Twitch Chat', 'OSC Command                         ']

# -   LOAD COMMANDS


def load_commands():
    global data
    if(os.path.exists('commands.csv')):
        with open('commands.csv', "r") as infile:
            reader = csv.reader(infile)
            try:
                data = list(reader)  # read everything else into a list of rows
                if len(data) == 0:
                    data = [['', 'ADD COMMANDS ABOVE!'], ]
            except:
                sg.popup_error('Error reading file')
            infile.close()
    else:
        data = [
            ['hello', ''],
        ]

# -   UPDATE DICT OF COMMANDS


def update_data_dict():
    global data_dict
    data_dict = defaultdict(list)
    for k, v in data:
        data_dict[k] = v

# -   SAVE COMMANDS


def save_commands():
    with open('commands.csv', 'w', encoding='UTF-8', newline='') as outfile:
        writer = csv.writer(outfile)

        writer.writerows(data)
        outfile.close()


####################-   LAYOUT   -#######################
load_commands()

cmd_layout = [
    [sg.Text("Add command for twitch message:")],
    [sg.Input(size=(14, 1), key='-MSG-'),
     sg.Input(size=(43, 1), key='-CMD-'), sg.Button('Add')],
    [sg.pin(sg.Column([[sg.Table(data, headings=headings, size=(40, 10),
            justification='left', key='-TABLE-')]], key='-Column-'))],
    [sg.Button('Delete', button_color=('white', 'firebrick3')), sg.Button('Modify'), sg.Checkbox('Enabled?', key='-ENABLED-'), ]]

chat_layout = [sg.Text('...', key="-CHANNEL-")],  [sg.ML(size=(110, 20),
                                                         disabled=True, autoscroll=True, font='Helvetica 10', key='-CHATBOX-'), ]

tab_group_layout = [[
                    sg.Tab('Commands', cmd_layout, key='-TAB2-'),
                    sg.Tab('Chat', chat_layout, key='-TAB3-'),
                    ]]

layout = [
    [sg.TabGroup(tab_group_layout,
                 enable_events=True,
                 key='-TABGROUP-')],
]

#################-   TWITCH READER   -###################
chat_history = ''


def init_twitch(window):
    twitchreader.init(data_dict, config, window)

###################-   OSC CLIENT   -####################


def init_OSC():
    global config
    oscclient.init(config['osc']['ip'], config['osc']['port'])


def send_OSC(cmd):
    oscclient.send_OSC(cmd)

#########################################################
#####################-   MAIN   -########################
#########################################################


def main():
    global chat_history, data_dict, config

    update_data_dict()
    load_settings()
    init_OSC()

    sg.theme(config['gui']['theme'])
    window = sg.Window("twitch-osc", layout, size=(500, 330), finalize=True)

    column = window['-Column-']
    table = window['-TABLE-']
    entry = window['-CMD-']
    entry.bind('<Return>', 'RETURN-')

    window['-CHANNEL-'].update('Twitch: ' + config['twitch']['channel'])

    threading.Thread(target=init_twitch, args=(window,), daemon=True).start()
    while True:
        event, values = window.read()
        if event == sg.WINDOW_CLOSED:
            break
        # print(event, values)
        if event in ('Add', '-CMD-RETURN-'):
            msg = values['-MSG-'].rstrip()
            cmd = values['-CMD-'].rstrip()

            if msg != '' and cmd != '':
                if msg in data_dict:
                    sg.popup_error('Message already exists!')
                else:
                    data.append([msg, cmd])
                    window['-TABLE-'].update(values=data)

                    window['-MSG-'].update('')
                    window['-CMD-'].update('')
                    update_data_dict()

        elif event == 'Delete':
            try:
                data.pop(values['-TABLE-'][0])
                window['-TABLE-'].update(values=data)
                update_data_dict()
            except IndexError:
                pass

        elif event == 'Modify':
            try:
                msg = data[values['-TABLE-'][0]][0]
                text = sg.popup_get_text(
                    'Modify command for \'' + msg + '\'', 'Modify command', data[values['-TABLE-'][0]][1])
                if(text != None and text.rstrip() != ''):
                    data.pop(values['-TABLE-'][0])
                    data.insert(values['-TABLE-'][0], [msg, text.rstrip()])
                    window['-TABLE-'].update(values=data)
                    update_data_dict()
            except IndexError:
                pass

        elif event == '-CHAT-':
            chat = values[event]
            chatbox = f'     {chat.get("sender")}: {chat.get("msg")}'

            if(values['-ENABLED-']):
                if chat['msg'] in data_dict:
                    chatbox = f'***  {chat.get("sender")}: {chat.get("msg")}'

                    command = data_dict.get(chat['msg'])
                    send_OSC(command)

            chat_history += chatbox + '\n'
            window['-CHATBOX-'].update(chat_history)

    window.close()
    save_commands()
    save_settings()


if __name__ == '__main__':
    main()
