# -*- coding: utf-8 -*-
# v1.3.0

import re
import json
import ast
import os
import hashlib

FILE_PATH = './plugins/MagicChat/'
detect = False
player = ""
message = ""
item_list = {}


def on_load(server, old):
    if not os.path.exists(FILE_PATH):
        os.makedirs(FILE_PATH)
    if not os.path.isfile(FILE_PATH + 'minecraft_item_list.json'):
        file = download_item_list()
        if file == 'error':
            server.logger.info('§c物品名称映射文件下载失败！')
            return
        else:
            with open(FILE_PATH + 'minecraft_item_list.json', 'wb') as download:
                download.write(file.content)
                download.flush()
                server.logger.info('已下载物品名称映射文件')
    if os.path.isfile(FILE_PATH + 'minecraft_item_list.json'):
        with open(FILE_PATH + 'minecraft_item_list.json') as init_item_list:
            global item_list
            item_list = json.load(init_item_list)


def on_info(server, info):
    global detect
    global player
    global message
    if info.is_player == 1 and '%i' in info.content:
        detect = True
        player = info.player
        message = info.content
        server.execute('data get entity {} SelectedItem'.format(info.player))
    elif info.is_player == 0 and re.fullmatch(r'.* has the following entity data: .*', info.content) and detect == True:
        detect = False
        item = data_convert(info.content)
        item_name = item_name_translate(item)
        if message.startswith('%i'):
            server.execute('/tellraw @a ["",{"text":"[","color":"gray"},{"text":"MagicChat","color":"green"},{"text":"] ","color":"gray"},{"text":"<' + player +
                           '> ","color":"white"},{"text":"[' + item_name + ']","color":"gold","hoverEvent":{"action":"show_item","value":' + item + '}},{"text":"' + message.replace('%i', '') + '"}]')
        elif message.endswith('%i'):
            server.execute('/tellraw @a ["",{"text":"[","color":"gray"},{"text":"MagicChat","color":"green"},{"text":"] ","color":"gray"},{"text":"<' + player +
                           '> ","color":"white"},{"text":"' + message.replace('%i', '') + '"},{"text":"[' + item_name + ']","color":"gold","hoverEvent":{"action":"show_item","value":' + item + '}}]')
        else:
            message = message.split('%i')
            server.execute('/tellraw @a ["",{"text":"[","color":"gray"},{"text":"MagicChat","color":"green"},{"text":"] ","color":"gray"},{"text":"<' + player + '> ","color":"white"},{"text":"' +
                           message[0] + '"},{"text":"[' + item_name + ']","color":"gold","hoverEvent":{"action":"show_item","value":' + item + '}},{"text":"' + message[1] + '"}]')


def item_name_translate(item_data):
    item_name = item_data.split(',')[0]
    item_name = re.findall(r"\\\"id\\\": \\\"(.+?)\\\"", item_name)[0]
    item_name = item_name_map(item_name)
    if item_name == None:
        return '展示物品'
    return item_name


def data_convert(item):
    item = re.sub(r'^.* has the following entity data: ', '', item)
    item = item.replace('minecraft:', '')
    item = re.sub(r'(?<=\d)[a-zA-Z](?=\D)', '', item)
    item = re.sub(r'([a-zA-Z.]+)(?=:)', '"\g<1>"', item)
    item = json.dumps(item)
    return item


def item_name_map(item_id):
    for id in item_list:
        if id == item_id:
            return item_list[id]


def download_item_list():
    try:
        import requests
        file = requests.get(
            'https://raw.githubusercontent.com/Da-Dog/MCDR-MagicChat/master/minecraft_item_list.json')
        return file
    except:
        return 'error'
