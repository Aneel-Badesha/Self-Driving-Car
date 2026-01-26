
import cv2
import socket
import struct
import numpy as np
import torch
from torchvision import transforms
from torchvision.models.detection import fasterrcnn_resnet50_fpn

COCO_INSTANCE_CATEGORY_NAMES = [
	'__background__', 'person', 'bicycle', 'car', 'motorcycle', 'airplane', 'bus',
	'train', 'truck', 'boat', 'traffic light', 'fire hydrant', 'stop sign', 'parking meter',
	'bench', 'bird', 'cat', 'dog', 'horse', 'sheep', 'cow', 'elephant', 'bear', 'zebra',
	'giraffe', 'backpack', 'umbrella', 'handbag', 'tie', 'suitcase', 'frisbee', 'skis',
	'snowboard', 'sports ball', 'kite', 'baseball bat', 'baseball glove', 'skateboard',
	'surfboard', 'tennis racket', 'bottle', 'wine glass', 'cup', 'fork', 'knife', 'spoon',
	'bowl', 'banana', 'apple', 'sandwich', 'orange', 'broccoli', 'carrot', 'hot dog',
	'pizza', 'donut', 'cake', 'chair', 'couch', 'potted plant', 'bed', 'dining table',
	'toilet', 'tv', 'laptop', 'mouse', 'remote', 'keyboard', 'cell phone', 'microwave',
	'oven', 'toaster', 'sink', 'refrigerator', 'book', 'clock', 'vase', 'scissors',
	'teddy bear', 'hair drier', 'toothbrush'
]

	pi_ip = '192.168.1.90'
	pi_port = 9999
	s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	s.connect((pi_ip, pi_port))
	print(f"Connected to {pi_ip}:{pi_port}")

	# Load model
	device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
	model = fasterrcnn_resnet50_fpn(pretrained=True).to(device)
	model.eval()

	preprocess = transforms.Compose([
		transforms.ToTensor()
	])

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
				# PyTorch inference
				input_tensor = preprocess(frame).to(device)
				with torch.no_grad():
					outputs = model([input_tensor])[0]
				# Draw boxes for detected objects with score > 0.5
				for box, label, score in zip(outputs['boxes'], outputs['labels'], outputs['scores']):
					if score > 0.5:
						x1, y1, x2, y2 = box.int().tolist()
						class_name = COCO_INSTANCE_CATEGORY_NAMES[label]
						cv2.rectangle(frame, (x1, y1), (x2, y2), (0,255,0), 2)
						cv2.putText(frame, f"{class_name}: {score:.2f}", (x1, y1-10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0,255,0), 2)
				cv2.imshow('Pi Stream + Detection', frame)
				if cv2.waitKey(1) == 27:
					break
	except Exception as e:
		print(f"Error: {e}")
	finally:
		s.close()
		cv2.destroyAllWindows()

if __name__ == "__main__":
	main()
