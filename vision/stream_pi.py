import cv2
import socket
import struct

def main():
	# Camera setup
	cap = cv2.VideoCapture(0)
	if not cap.isOpened():
		print("Camera not detected")
		return

	# Socket setup
	server_ip = '0.0.0.0'  # Listen on all interfaces
	server_port = 9999
	s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
	s.bind((server_ip, server_port))
	s.listen(1)
	print(f"Waiting for connection on {server_ip}:{server_port}...")
	conn, addr = s.accept()
	print(f"Connected by {addr}")

	try:
		while True:
			ret, frame = cap.read()
			if not ret:
				break
			# Encode frame as JPEG
			_, buffer = cv2.imencode('.jpg', frame)
			data = buffer.tobytes()
			# Send length of data first, then data
			conn.sendall(struct.pack('>L', len(data)) + data)
	except Exception as e:
		print(f"Error: {e}")
	finally:
		cap.release()
		conn.close()
		s.close()

if __name__ == "__main__":
	main()
