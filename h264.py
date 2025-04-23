import time
import av
import numpy as np
import cv2
import struct
import datetime

class H264:
    def __init__(self, sock, w=0, h=0, fps=0, stream_options={}, logger=None):
        self.sock = sock
        self.logger = logger
        self.encoder = ffenc.ffenc(int(w), int(h), int(fps))
        self.decoder = ffdec.ffdec()
        self.buffer = b''
        self.send_frame_idx = 0
        self.recv_frame_idx = 0
        self.nbytes_received = 0

        # PyAV encoder
        output = av.open(sock.makefile('wb'), format='h264')
        self.stream = output.add_stream('h264', rate=fps, options=stream_options)
        stream.width = w
        stream.height = h
        stream.pix_fmt = 'yuv420p'


    def send_frame(self, frame):
        # self.encoder.change_settings(5000, 31)
        try:
            # Convert frame and encode
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            av_frame = av.VideoFrame.from_ndarray(frame_rgb, format='rgb24')

            for packet in stream.encode(av_frame):
                packet_bytes = bytes(packet)
                print(f'Packet size: {len(packet_bytes)} bytes')
                # Send length prefix then data
                self.sock.sendall(struct.pack('>I', len(packet_bytes)))
                self.sock.sendall(packet_bytes)

            # print(f'Frame size: {out.shape[0]} bytes')
            # start_time = time.time()

            # self.sock.sendall(struct.pack('!d', start_time))
            # self.sock.sendall(struct.pack('!I', out.shape[0]))
            # self.sock.sendall(out.tobytes())
            # end_time = time.time()

            self.send_frame_idx += 1
        except TimeoutError:
            print("Unable to send frame, connection timed out...")
        
    def get_frame(self):
        client_send_start_time = struct.unpack('!d', self.sock.recv(8))[0]
        data_length = struct.unpack('!I', self.sock.recv(4))[0]
        
        while len(self.buffer) < data_length:
            data = self.sock.recv(min(data_length - len(self.buffer), 40960))
            if not data: # socket closed
                return None
            self.buffer += data

        self.nbytes_received += len(self.buffer)

        data = np.frombuffer(self.buffer, dtype=np.uint8)
        print(data.nbytes)
        frame = self.decoder.process_frame(data)
        frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
        self.buffer = b''

        self.recv_frame_idx += 1

        return frame