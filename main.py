import server
import threading
import yaml
import requests
from serverInfo import serverInfo


def run_server():
    server.run()


def check_for_request():
    while True:
        text = input()
        if len(text) > 8:
            if text[:7] == 'request':
                find_port(text[8:])


def find_port(filename):
    filenode = find_filenode(filename)
    for i in serverInfo.config['friend_nodes']:
        if i['node_name'] == filenode:
            query = {'filename': filename, 'port': serverInfo.port}
            requests.get('http://127.0.0.1:' + str(i['node_port']) + '/getfile/', params=query)
            return
    query = {'filenode': filenode}
    result = requests.get('http://127.0.0.1:' + str(serverInfo.config['friend_nodes'][0]['node_port']) + '/getport/',
                          params=query)
    query = {'filename': filename, 'port': serverInfo.port}
    requests.get('http://127.0.0.1:' + result.text + '/getfile/', params=query)


def find_filenode(filename):
    for i in node['node_files']:
        for j in i['node_files']:
            if j == filename:
                return i['node_name']


if __name__ == '__main__':
    with open("Config.yml", "r") as stream:
        try:
            config = yaml.safe_load(stream)
        except yaml.YAMLError as exc:
            print(exc)

    with open("NodeFiles.yml", "r") as stream:
        try:
            node = yaml.safe_load(stream)
        except yaml.YAMLError as exc:
            print(exc)

    config['friend_nodes'].sort(key=lambda n: abs(n['node_name'] - config['node_number']))

    serverInfo.port = config["node_port"]
    serverInfo.config = config
    serverInfo.node = node

    t1 = threading.Thread(target=run_server, name='t1')
    t2 = threading.Thread(target=check_for_request, name='t2')

    t1.start()
    t2.start()
