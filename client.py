import cv2
import av
import socket
import struct
from datetime import datetime

# CHANGE THESE SETTINGS AS NEEDED
# VIDEO_SRC = 0 for webcam. Can also be a video path like "/Users/bencivjan/Desktop/360-video-streaming/videos/climbing.mp4"
# SERVER_IP is the IP address of the server. Use '127.0.0.1' for local testing.
VIDEO_SRC = 0
SERVER_IP = '10.193.220.145'
PORT = 9999

# Socket setup
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.connect((SERVER_IP, PORT))

# OpenCV camera or video
cap = cv2.VideoCapture(VIDEO_SRC)
width  = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
fps    = int(cap.get(cv2.CAP_PROP_FPS) or 30)

stream_options = {
    'b': '10000k',  # Bitrate
    'preset': 'ultrafast',  # Encoding speed
}

# PyAV encoder
output = av.open(sock.makefile('wb'), format='h264')
stream = output.add_stream('h264', rate=fps, options=stream_options)
stream.width = width
stream.height = height
stream.pix_fmt = 'yuv420p'

try:
    while True:
        ret, frame = cap.read()

        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')

        position = (10, 50)
        font = cv2.FONT_HERSHEY_PLAIN
        font_scale = 5
        color = (0, 0, 255)
        thickness = 4

        # Put the timestamp on the frame
        cv2.putText(frame, timestamp, position, font, font_scale, color, thickness, cv2.LINE_AA)

        if not ret:
            cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
            continue

        # Convert frame and encode
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        av_frame = av.VideoFrame.from_ndarray(frame_rgb, format='rgb24')

        for packet in stream.encode(av_frame):
            packet_bytes = bytes(packet)
            print(f'Packet size: {len(packet_bytes)} bytes')
            # Send length prefix then data
            sock.sendall(struct.pack('>I', len(packet_bytes)))
            sock.sendall(packet_bytes)
except KeyboardInterrupt:
    # Flush encoder
    for packet in stream.encode():
        packet_bytes = packet.to_bytes()
        sock.sendall(struct.pack('>I', len(packet_bytes)))
        sock.sendall(packet_bytes)

    cap.release()
    sock.close()
