# receiver.py
import av
import socket
import struct
import cv2
import pyvirtualcam
import threading


# retrieved frame
global display_frame

def send_virtualcam():
    with pyvirtualcam.Camera(width=3840, height=1920, fps=30) as cam:
        print(f'Using virtual camera: {cam.device}')  # RGB
        while True:
            if display_frame is not None:
                cam.send(display_frame[:, :, ::-1])
                cam.sleep_until_next_frame()

def handle_client(conn, addr):
    print(f"Accepted connection from {addr}")

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
                cv2.imshow("Received", img)
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    raise KeyboardInterrupt
    except KeyboardInterrupt:
        pass

    conn.close()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    threading.Thread(target=send_virtualcam).start()

    # Server socket
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(('0.0.0.0', 9999))
    server.listen(1)
    print("Waiting for connection...")
    conn, addr = server.accept()
    print(f"Connected to {addr}")

    # Decoder
    decoder = av.codec.CodecContext.create('h264', 'r')
    
    while True:
        client_socket, addr = server.accept()
        threading.Thread(target=handle_client, kwargs={'client_socket':conn, 'addr': addr}).start()