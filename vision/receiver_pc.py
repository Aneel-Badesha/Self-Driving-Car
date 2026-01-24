import cv2
import socket
import struct
import numpy as np

def main():
	pi_ip = '192.168.1.90'
	pi_port = 9999
	s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	s.connect((pi_ip, pi_port))
	print(f"Connected to {pi_ip}:{pi_port}")

	data = b''
	payload_size = struct.calcsize('>L')
	try:
		while True:
			# Receive message length
			while len(data) < payload_size:
				packet = s.recv(4096)
				if not packet:
					break
				data += packet
			if len(data) < payload_size:
				break
			packed_msg_size = data[:payload_size]
			data = data[payload_size:]
			msg_size = struct.unpack('>L', packed_msg_size)[0]

			# Receive frame data
			while len(data) < msg_size:
				data += s.recv(4096)
			frame_data = data[:msg_size]
			data = data[msg_size:]

			# Decode JPEG
			frame = cv2.imdecode(np.frombuffer(frame_data, np.uint8), cv2.IMREAD_COLOR)
			if frame is not None:
				cv2.imshow('Pi Stream', frame)
				if cv2.waitKey(1) == 27:
					break
	except Exception as e:
		print(f"Error: {e}")
	finally:
		s.close()
		cv2.destroyAllWindows()

if __name__ == "__main__":
	main()
