import shutil
import uvicorn
from fastapi import FastAPI, File, UploadFile
from serverInfo import serverInfo
import requests

app = FastAPI()


@app.get("/getport/")
def get_port_node(filenode: int, source_port: int = None):
    print('get port called')
    serverInfo.config['friend_nodes'].sort(key=lambda n: abs(n['node_name'] - serverInfo.port))
    for i in serverInfo.config['friend_nodes']:
        if i['node_name'] == filenode:
            return i['node_port']
    query = {'filenode': filenode, 'source_port': serverInfo.port}
    if serverInfo.config['friend_nodes'][0]['node_port'] != source_port:
        result = requests.get(
            'http://127.0.0.1:' + str(serverInfo.config['friend_nodes'][0]['node_port']) + '/getport/',
            params=query)
    else:
        result = requests.get(
            'http://127.0.0.1:' + str(serverInfo.config['friend_nodes'][1]['node_port']) + '/getport/',
            params=query)
    return result.text


@app.get("/getfile/")
def send_file(filename: str, port: int):
    print('get file called')
    files = {'file': (filename, open(serverInfo.config['owned_files_dir'] + filename, 'rb'), 'multipart/form-data')}
    requests.post('http://127.0.0.1:' + str(port) + '/uploadfile/', files=files)
    return {"filename": filename}


@app.post("/uploadfile/")
async def create_upload_file(file: UploadFile = File(...)):
    print('upload file called')
    with open(serverInfo.config['new_files_dir'] + file.filename, 'wb') as buffer:
        shutil.copyfileobj(file.file, buffer)
    return {"filename": file.filename}


def run():
    print('run server in port: ' + str(serverInfo.port))
    uvicorn.run(app, host="127.0.0.1", port=serverInfo.port, log_level="critical")
