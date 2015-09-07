from urllib.request import urlopen
import json
from collections import Iterable
from configparser import ConfigParser
import os.path
import os
from SimpleConfig import SimpleConfig
from datetime import datetime
import time

class bcolors:
    """
    Constants for teminal coloring
    """
    
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

def get_posts(count=1, offset=0, domain='oldlentach'):
    """"
    Returns last posts from lentach vk page

    :param count: number of posts returned
    :return: returns nested dictionary containing last posts
    """

    url = 'https://api.vk.com/method/wall.get?domain={}&count={}&offset={}'.format(domain, count, offset)
    with urlopen(url, timeout=5) as data:
        pydata = json.loads(data.read().decode('utf-8'))
    return pydata

def find_val(dic, search_key='audio'):
    """
    Finds all entries in nested dictionary/list object whose key is search_key

    :param dic: dictionary object to search in
    :param search_key: key to search for in dictionary
    :return: returns generator which yields found values 
    """

    if dic is not None:
        if hasattr(dic, '__iter__') and not isinstance(dic, str):
            iterable = dic if isinstance(dic, dict) else range(len(dic))
            for key in iterable:
                item = dic[key]
                if key == search_key:
                    yield item
                if hasattr(item, '__iter__') and not isinstance(item, str):
                    indexes = item if isinstance(item, dict) else range(len(item))
                    for index in indexes:
                        if index == search_key:
                            yield item[index]
                        for val in find_val(item[index], search_key):
                            yield val

def save_audio(url, title, performer, music_dir=os.path.expanduser('~')+'/Music'):
    """
    Saves audio from url on the computer

    :param url: URL to download from
    :param title: name to be saved on disk with
    :return: returns nothing
    """

    with urlopen(url) as data:
        folder = music_dir + '/{}/'.format(performer)
        if not os.path.exists(folder):
            os.makedirs(folder)
        with open(folder + title + '.mp3', 'wb') as file:
            file.write(data.read())

def set_config(config):
    """
    Initializes config with data if needed

    :param config: SimpleConfig object
    :return: returns config object
    """

    for name in config:
        if name != 'DEFAULT' and name != 'PRIVATE':
            group = config[name]
            if 'last_post_id' not in group or group['last_post_id'] == '-1':
                domain = group['domain']
                posts_count = int(config['PRIVATE']['ppd'])
                posts = get_posts(count=posts_count, domain=domain)
                for index in range(1, posts_count+1):
                    id = posts['response'][index]['id']
                    if id > int(group['last_post_id']):
                        group['last_post_id'] = str(id)
                config.save()      
    return config  

def get_config():
    """
    Gets config if exists. If not creates new one.

    :return: returns config
    """

    config = SimpleConfig(content='[PRIVATE]\n'
                                  'ppd = 5')
    if not config.exists():
        config.create()
    config.load()
    return config

def set_up():
    """
    Gets config, sets it up, and returns it.

    :return: returns config object
    """

    return set_config(get_config())

def save_audios(audios):
    """
    Saves audios echoing if successful or not

    :param audios: iterable of dictionaries representing audio
    :return: return nothing
    """

    for audio in audios:
        try:
            print(bcolors.OKBLUE, 'downloading ', bcolors.ENDC, audio['title'], end=' ')
            save_audio(audio['url'], audio['title'], audio['performer'])
        except:
            print(bcolors.FAIL, 'failure', bcolors.ENDC)
        else:
            print(bcolors.OKGREEN, 'success', bcolors.ENDC)

def parse_group(group, config):
    """
    Saves audios from a given group saving state in config

    :param group: config section object
    :param config: SimpleConfig object
    :return: returns nothing
    """
    ALLOWED_PER_SECOND = 3
    allowed = ALLOWED_PER_SECOND
    last_time = time.time()
    more_posts_needed = True
    last_post_id = -1
    config_last_id = int(group['last_post_id'])
    posts_count = int(config['PRIVATE']['ppd'])
    domain = group['domain']
    offset = 0
    
    while more_posts_needed:
        if allowed > 0:
            allowed -= 1
            posts = get_posts(count=posts_count, offset=offset, domain=domain)
            offset += posts_count
            new_posts = [post for post in posts['response'][1:posts_count+1] \
                        if post['id'] > config_last_id and 'is_pinned' not in post]
            save_audios(find_val(new_posts)) 
            post_ids = [post['id'] for post in posts['response'][1:posts_count+1] if 'is_pinned' not in post]
            last_post_id = max(last_post_id, max(post_ids))
            last_loaded = min(post_ids)
            more_posts_needed = last_loaded > config_last_id
        else:
            cur_time = time.time()
            if (cur_time - last_time) < 1:
                time.sleep(1)
            else:
                allowed = ALLOWED_PER_SECOND
                last_time = time.time()
    if last_post_id != -1:
        group['last_post_id'] = str(last_post_id)
        config.save()

def load_new_posts(config):
    """
    Loads audios from new posts 

    :param config: config object
    :return: returns nothing
    """

    for name in config:
        group = config[name]
        if name != 'PRIVATE' and name != 'DEFAULT':
            parse_group(group, config)


def main():
    load_new_posts(set_up())

if __name__ == '__main__':
    main()