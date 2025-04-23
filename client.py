import cv2
import socket
import numpy as np
import struct
import time
from datetime import datetime
import sys
import os
import av
import h264

# mod_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), 'streamers', 'ffenc_uiuc'))
# if mod_dir not in sys.path:
#     sys.path.append(mod_dir)
# from streamers.ffenc_uiuc import h264

def stream_video():
    if len(sys.argv) < 2:
        print('Input server IP address as first argument')
        return
    else:
        TCP_IP = sys.argv[1]
    TCP_PORT = 8010

    cap = cv2.VideoCapture('videos/climbing.mp4')
    client_socket = socket.socket()
    client_socket.settimeout(5)  # 5 seconds timeout
    while True:
        try:
            client_socket.connect((TCP_IP, TCP_PORT))
            break
        except OSError:
            print("Unable to connect to server socket, retrying...")
            datetime_obj = datetime.fromtimestamp(time.time())
            readable_time = datetime_obj.strftime("%Y-%m-%d %H:%M:%S")
            with open("errors.out", "a") as err_file:
                err_file.write(f'{readable_time}: Unable to connect to server at {TCP_IP}\n')
            time.sleep(5)

    try:
        frames_read = 0
        test_start_time = time.time()

        client_socket.sendall(struct.pack('B', 0x8))
        fps = cap.get(cv2.CAP_PROP_FPS)
        width = cap.get(cv2.CAP_PROP_FRAME_WIDTH)
        height = cap.get(cv2.CAP_PROP_FRAME_HEIGHT)
        streamer = h264.H264(client_socket, width, height, fps)

        while True:
            ret, frame = cap.read()
            frames_read += 1
            if not ret:
                print("Failed to capture frame")
                print(f'Actual frame rate: {frames_read / (time.time() - test_start_time)}')
                break

            streamer.send_frame(frame)
            print(frame.nbytes)
    finally:
        cap.release()
        client_socket.close()

if __name__ == '__main__':
    stream_video()