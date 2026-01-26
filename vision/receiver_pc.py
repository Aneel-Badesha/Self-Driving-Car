
import argparse
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

def main():
    parser = argparse.ArgumentParser(description='Pi stream receiver with optional detection')
    parser.add_argument('--no-detect', action='store_true', help='Skip model loading and inference (display only)')
    parser.add_argument('--scale', type=float, default=1.0, help='Downscale factor for frames before inference (0.0-1.0)')
    parser.add_argument('--skip-frames', type=int, default=0, help='Number of frames to skip between inferences (0 = every frame)')
    args = parser.parse_args()

    pi_ip = '192.168.1.90'
    pi_port = 9999
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((pi_ip, pi_port))
    print(f"Connected to {pi_ip}:{pi_port}")

    # Load model unless user disabled it
    if args.no_detect:
        device = None
        model = None
        preprocess = None
        print('Detection disabled (--no-detect)')
    else:
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
                # optionally downscale before inference to speed up processing
                original_h, original_w = frame.shape[:2]
                use_frame = frame
                scale = float(args.scale) if args.scale and args.scale > 0 and args.scale <= 1.0 else 1.0
                if scale != 1.0:
                    new_w = max(1, int(original_w * scale))
                    new_h = max(1, int(original_h * scale))
                    use_frame = cv2.resize(frame, (new_w, new_h), interpolation=cv2.INTER_LINEAR)

                do_infer = (not args.no_detect) and (model is not None)
                # manage frame skipping
                if args.skip_frames > 0:
                    # use a simple counter attached to the socket object
                    cnt = getattr(s, '_frame_count', 0) + 1
                    s._frame_count = cnt
                    if (cnt - 1) % (args.skip_frames + 1) != 0:
                        do_infer = False

                outputs = None
                if do_infer:
                    input_tensor = preprocess(use_frame).to(device)
                    with torch.no_grad():
                        outputs = model([input_tensor])[0]
                # Draw boxes for detected objects with score > 0.5
                if outputs is not None:
                    for box, label, score in zip(outputs['boxes'], outputs['labels'], outputs['scores']):
                        if score > 0.5:
                            x1, y1, x2, y2 = box.int().tolist()
                            # label may be a torch tensor scalar; convert to int safely
                            try:
                                label_idx = int(label)
                            except Exception:
                                try:
                                    label_idx = int(label.item())
                                except Exception:
                                    label_idx = None

                            if label_idx is None:
                                class_name = str(label)
                            elif 0 <= label_idx < len(COCO_INSTANCE_CATEGORY_NAMES):
                                class_name = COCO_INSTANCE_CATEGORY_NAMES[label_idx]
                            else:
                                class_name = f"cls_{label_idx}"

                            # if we ran inference on a downscaled frame, scale boxes back to original
                            if scale != 1.0:
                                x1 = int(x1 / scale)
                                y1 = int(y1 / scale)
                                x2 = int(x2 / scale)
                                y2 = int(y2 / scale)

                            cv2.rectangle(frame, (x1, y1), (x2, y2), (0,255,0), 2)
                            cv2.putText(frame, f"{class_name}: {score:.2f}", (x1, y1-10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0,255,0), 2)

                # choose window name based on whether detection ran
                if outputs is not None:
                    window_name = 'Pi Stream + Detection'
                else:
                    window_name = 'Pi Stream (no detection)'
                cv2.imshow(window_name, frame)
                if cv2.waitKey(1) == 27:
                    break
    except Exception as e:
        print(f"Error: {e}")
    finally:
        s.close()
        cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
