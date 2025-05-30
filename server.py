import av
import socket
import struct
import pyvirtualcam
import threading
import time


# Retrieved frame to display in Unity
global display_frame
display_frame = None

# Loop function to read display_frame and send to the virtual camera read by Unity
def send_virtualcam():
    with pyvirtualcam.Camera(width=3840, height=1920, fps=30) as cam:
        print(f'Using virtual camera: {cam.device}')  # RGB
        while True:
            if display_frame is not None:
                cam.send(display_frame[:, :, ::-1])
                cam.sleep_until_next_frame()

# Thread spawned for each client connection
def handle_client(conn, addr):
    print(f"Accepted connection from {addr}")

    frame_count = 0
    start_time = time.time()
    
    def calculate_fps():
        elapsed_time = time.time() - start_time
        if elapsed_time > 0:
            return frame_count / elapsed_time
        return 0

    try:
        while True:
            # Read 4-byte length
            header = conn.recv(4)
            if not header:
                break
            packet_len = struct.unpack('>I', header)[0]

            # Read full packet
            data = b''
            while len(data) < packet_len:
                chunk = conn.recv(packet_len - len(data))
                if not chunk:
                    break
                data += chunk

            # Decode
            packet = av.Packet(data)
            frames = decoder.decode(packet)
            for frame in frames:
                img = frame.to_ndarray(format='bgr24')
                display_frame = img
                frame_count += 1
                print(calculate_fps())
    except (socket.error, ConnectionResetError) as e:
        print(f"Socket error: {e}")
    finally:
        conn.close()
        avg_fps = calculate_fps()
        print(f"Average FPS: {avg_fps:.2f}")

if __name__ == "__main__":
    threading.Thread(target=send_virtualcam).start()

    # Server socket
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(('0.0.0.0', 9999))
    server.listen(1)
    print("Waiting for connection...")

    # Decoder
    decoder = av.codec.CodecContext.create('h264', 'r')
    
    while True:
        conn, addr = server.accept()
        threading.Thread(target=handle_client, kwargs={'conn':conn, 'addr': addr}).start()