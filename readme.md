# 360 Video Streaming System

This project enables real-time streaming of 360° video from a client (video source) to a server, which can display the video and output it to a VR device. It does so with relatively low latency, ranging from *122 - 174 ms* for camera to VR device transmission.

### Requirements
To install dependencies:
> `pip install -r requirements.txt`

## Running the Server
The server receives the video stream, decodes it, and sends it to a virtual camera device (for use in Unity).

1. **Install the appropriate virtual camera software for your OS**
    - [More information here under "Supported virtal cameras](https://github.com/letmaik/pyvirtualcam)

2. **Start the server:**
`python server.py`

This will start a server on port `9999`. Make sure that this port is not blocked with a firewall, or change the port!

## Running the Client

The client captures video from a webcam or video file, encodes it, and streams it to the server.

1. **Set the video source**
    
By default, the client uses your webcam (VIDEO_SRC = 0). To use a video file, change the VIDEO_SRC variable in client.py to the file path.

2. **Start the client:**
`python client.py -s <SERVER_IP>`

Replace <SERVER_IP> with the IP address of the server machine.
If running both client and server on the same machine, you can omit -s (defaults to 127.0.0.1).

## Running in Unity
- TODO