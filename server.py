from flask import Flask, Response, url_for
import cv2
import numpy as np
import socket
import struct
import threading
import time  # Import time for recording frame times
import os
import sys

mod_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), 'streamers', 'ffenc_uiuc'))
if mod_dir not in sys.path:
    sys.path.append(mod_dir)
from streamers.ffenc_uiuc import h264

app = Flask(__name__)

# Global variable to hold the latest image and frame times
video_captures = {}

def handle_client(client_socket, addr):
    global video_captures
    client_ip = addr[0]

    compression_alg = struct.unpack('B', client_socket.recv(1))[0]
    print(f'compression_alg: {compression_alg}')

    IMGS_PATH = f'./received_imgs_{compression_alg}_{client_ip}/'
    streamer = h264.H264(client_socket)
    
    os.makedirs(IMGS_PATH, exist_ok=True)

    frame_idx = 0
    while True:
        try:
            frame = streamer.get_frame()
            if frame is None:
                raise ConnectionResetError
            video_captures[client_ip] = frame
            img_name = IMGS_PATH + str(frame_idx) + '.jpg'
            ret = cv2.imwrite(img_name, frame)
            frame_idx += 1
            if ret == False:
                print(f'Failed to write image to {img_name}')
                if client_ip in video_captures:
                    del video_captures[client_ip]
                break
        except (ConnectionResetError, BrokenPipeError, struct.error):
            print("Client disconnected or error occurred")
            if client_ip in video_captures:
                del video_captures[client_ip]
            break

def video_feed(camera_id):
    global video_captures
    while True:
        if camera_id in video_captures:
            img = video_captures[camera_id]
            start = time.time()
            print(f"Pred time: {time.time() - start}")
            ret, jpeg = cv2.imencode('.jpg', img)
            if ret:
                yield (b'--frame\r\n'
                       b'Content-Type: image/jpeg\r\n\r\n' + jpeg.tobytes() + b'\r\n\r\n')

@app.route(f'/video_feed/<string:camera_id>')
def video_feed_route(camera_id):
    return Response(video_feed(camera_id),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/')
def index():
    global video_captures
    links = ''
    for camera_id in video_captures.keys():
        links += f'<p><a href="{url_for("video_feed_route", camera_id=camera_id)}">{camera_id}</a></p>'
    return links

def main():
    HOST_PUBLIC = '0.0.0.0'
    HOST_LOCAL = 'localhost'
    SOCKET_PORT = 8010
    WEB_PORT = 8080
    server_socket = socket.socket()
    server_socket.bind((HOST_PUBLIC, SOCKET_PORT))
    server_socket.listen(1)
    # So we don't have to wait when restarting the server
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    threading.Thread(target=app.run, kwargs={'host':HOST_PUBLIC, 'port':WEB_PORT}).start()

    while True:
        client_socket, addr = server_socket.accept()
        threading.Thread(target=handle_client, kwargs={'client_socket':client_socket, 'addr': addr}).start()

if __name__ == '__main__':
    main()