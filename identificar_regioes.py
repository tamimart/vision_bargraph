
#!pip install ultralytics

import os
from ultralytics import YOLO
model = YOLO("yolov8n.pt")  # load pre trained model

# Use the model
results = model.train(data=os.path.join(ROOT_DIR, "google_colab_config.yaml"), epochs=20)  # train the model


