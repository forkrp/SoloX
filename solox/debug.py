from __future__ import absolute_import
import multiprocessing
import subprocess
import time
import os
import platform
import re
import webbrowser
import requests
import socket
import sys
from view.apis import api
from view.pages import page
from public.adb import adb
from logzero import logger
from threading import Lock
from flask_socketio import SocketIO, disconnect
from flask import Flask
import fire as fire
import signal


app = Flask(__name__, template_folder='templates', static_folder='static')
app.register_blueprint(api)
app.register_blueprint(page)

socketio = SocketIO(app, cors_allowed_origins="*")
thread = True
thread_lock = Lock()


@socketio.on('connect', namespace='/logcat')
def connect():
    socketio.emit('start connect', {'data': 'Connected'}, namespace='/logcat')
    logDir = os.path.join(os.getcwd(),'adblog')
    if not os.path.exists(logDir):
        os.mkdir(logDir)
    global thread
    thread = True
    with thread_lock:
        if thread:
            thread = socketio.start_background_task(target=backgroundThread)


def backgroundThread():
    global thread
    try:
        logger.info('Initializing adb environment ...')
        os.system('adb kill-server')
        os.system('adb start-server')
        current_time = time.strftime("%Y%m%d%H", time.localtime())
        logPath = os.path.join(os.getcwd(),'adblog',f'{current_time}.log')
        logcat = subprocess.Popen(f'adb logcat *:E > {logPath}', stdout=subprocess.PIPE,
                                  shell=True)
        
        with open(logPath, "r") as f:
            while thread:
                socketio.sleep(1)
                for line in f.readlines():
                    socketio.emit('message', {'data': line}, namespace='/logcat')
        if logcat.poll() == 0:
            thread = False
    except Exception:
        pass


@socketio.on('disconnect_request', namespace='/logcat')
def disconnect():
    global thread
    logger.warning('Logcat client disconnected')
    thread = False
    disconnect()


def checkPyVer():
    """
    :func: check python version
    """
    if int(platform.python_version().split('.')[0]) < 3:
        logger.error('python version must be >2,your python version is {}'.format(platform.python_version()))
        logger.error('please install python::3 and pip3 install -U solox')
        sys.exit()


def _hostIP():
    """
    :func: get local ip
    :return: ip
    """
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(('8.8.8.8', 80))
        ip = s.getsockname()[0]
    except Exception as e:
        raise e
    finally:
        s.close()
    return ip


def listeningPort(port):
    """
    Detect whether the port is occupied and clean up
    :param port: System port
    :return: None
    """
    if platform.system() != 'Windows':
        os.system("lsof -i:%s| grep LISTEN| awk '{print $2}'|xargs kill -9" % port)
    else:
        port_cmd = 'netstat -ano | findstr {}'.format(port)
        r = os.popen(port_cmd)
        r_data_list = r.readlines()
        if len(r_data_list) == 0:
            return
        else:
            pid_list = []
            for line in r_data_list:
                line = line.strip()
                pid = re.findall(r'[1-9]\d*', line)
                pid_list.append(pid[-1])
            pid_set = list(set(pid_list))[0]
            pid_cmd = 'taskkill -PID {} -F'.format(pid_set)
            os.system(pid_cmd)


def getServerStatus(host: str, port: int):
    """
    get solox server status
    :param host:
    :param port:
    :return:
    """
    try:
        r = requests.get(f'http://{host}:{port}', timeout=2.0)
        flag = (True, False)[r.status_code == 200]
        return flag
    except requests.exceptions.ConnectionError:
        pass
    except Exception:
        pass


def openUrl(host: str, port: int):
    """
    Listen and open the url after solox is started
    :param host:
    :param port:
    :return:
    """
    flag = True
    while flag:
        logger.info('start solox server')
        flag = getServerStatus(host, port)
    webbrowser.open(f'http://{host}:{port}/?platform=Android&lan=en', new=2)
    logger.info(f'Running on http://{host}:{port}/?platform=Android&lan=en (Press CTRL+C to quit)')


def startServer(host: str, port: int):
    """
    startup the solox service
    :param host:
    :param port:
    :return:
    """
    try:
        logger.info(f'Running on http://{host}:{port}/?platform=Android&lan=en (Press CTRL+C to quit)')
        socketio.run(app, host=host, debug=False, port=port)
    except Exception:
        sys.exit(0)

def main(host=_hostIP(), port=50003):
    """
    startup solox
    :param host: 0.0.0.0
    :param port: 默认5000端口
    :return:
    """
    try:
        checkPyVer()
        listeningPort(port=port)
        startServer(host, port)
        # pool = multiprocessing.Pool(processes=2)
        # pool.apply_async(startServer, (host, port))
        # pool.apply_async(openUrl, (host, port))
        # pool.close()
        # pool.join()
    except Exception:
        sys.exit(0)
    except KeyboardInterrupt:
        logger.info('stop solox success')                   

if __name__ == '__main__':
    fire.Fire(main)