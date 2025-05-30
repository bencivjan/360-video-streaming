import cv2
import av
import socket
import struct
from datetime import datetime
import argparse


parser = argparse.ArgumentParser(description='Video streaming client')

# SERVER_IP is the IP address of the server. Use '127.0.0.1' for local testing.
parser.add_argument('-s', default='127.0.0.1', help='Server IP address (default: 127.0.0.1)')
args = parser.parse_args()

# CHANGE THESE SETTINGS AS NEEDED
# VIDEO_SRC = 0 for webcam. Can also be a video path like "/Users/bencivjan/Desktop/360-video-streaming/videos/climbing.mp4"
VIDEO_SRC = 0
SERVER_IP = args.s
PORT = 9999

# Socket setup
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.connect((SERVER_IP, PORT))

cap = cv2.VideoCapture(VIDEO_SRC)
width  = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
fps    = int(cap.get(cv2.CAP_PROP_FPS) or 30)

stream_options = {
    'b': '10000k',  # Bitrate, adjust as needed (e.g., '5000k' for 5 Mbps)
    'preset': 'ultrafast',  # Encoding speed, ultrafast is fastest but lower encoding efficiency. Best for low-latency streaming
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

        # Display the video stream in a window to verify it's working
        if ret:
            cv2.imshow('Video Stream', frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
        
        # Timestamp the frame for latency measurements
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')

        position = (10, 50)
        font = cv2.FONT_HERSHEY_PLAIN
        font_scale = 5
        color = (0, 0, 255)
        thickness = 4

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
