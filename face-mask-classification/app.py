from flask import Flask, render_template, request, jsonify
from tensorflow.keras.models import load_model
import numpy as np
import joblib
import os
import cv2
from werkzeug.utils import secure_filename

app = Flask(__name__)

# ==========================
# LOAD MODEL CNN
# ==========================

model = load_model(
    "model/mask_detector_final.h5"
)

idx_to_label = joblib.load(
    "model/idx_to_label.pkl"
)

# ==========================
# LOAD DNN FACE DETECTOR
# ==========================

face_net = cv2.dnn.readNetFromCaffe(
    "face_detector/deploy.prototxt",
    "face_detector/res10_300x300_ssd_iter_140000.caffemodel"
)

IMG_SIZE = (224, 224)

# ==========================
# HOME
# ==========================

@app.route("/")
def home():
    return render_template("index.html")

# ==========================
# PREDICT IMAGE
# ==========================

def predict_image(image_path):

    image = cv2.imread(image_path)

    if image is None:
        raise Exception(
            f"Gagal membaca gambar: {image_path}"
        )

    (h, w) = image.shape[:2]

    blob = cv2.dnn.blobFromImage(
        cv2.resize(image, (300, 300)),
        1.0,
        (300, 300),
        (104.0, 177.0, 123.0)
    )

    face_net.setInput(blob)

    detections = face_net.forward()

    faces = []

    for i in range(detections.shape[2]):

        confidence = detections[0, 0, i, 2]

        if confidence > 0.5:

            box = detections[0, 0, i, 3:7] * np.array(
                [w, h, w, h]
            )

            (x1, y1, x2, y2) = box.astype("int")

            faces.append(
                (
                    x1,
                    y1,
                    x2 - x1,
                    y2 - y1
                )
            )

    print("Jumlah wajah terdeteksi:", len(faces))

    # ==========================
    # TIDAK ADA WAJAH
    # ==========================

    if len(faces) == 0:

        return (
            "Face Not Detected",
            0,
            0
        )

    # ==========================
    # WAJAH TERBESAR
    # ==========================

    largest_face = max(
        faces,
        key=lambda f: f[2] * f[3]
    )

    x, y, w, h = largest_face

    x = max(0, x)
    y = max(0, y)

    w = min(
        w,
        image.shape[1] - x
    )

    h = min(
        h,
        image.shape[0] - y
    )

    face = image[
        y:y+h,
        x:x+w
    ]

    face = cv2.resize(
        face,
        IMG_SIZE
    )

    face = cv2.cvtColor(
        face,
        cv2.COLOR_BGR2RGB
    )

    img_array = (
        face.astype("float32") / 255.0
    )

    img_array = np.expand_dims(
        img_array,
        axis=0
    )

    # ==========================
    # PREDIKSI CNN
    # ==========================

    prob = float(
        model.predict(
            img_array,
            verbose=0
        )[0][0]
    )

    pred_idx = int(
        prob > 0.5
    )

    label = idx_to_label[
        pred_idx
    ]

    if pred_idx == 1:

        confidence = prob * 100

    else:

        confidence = (
            1 - prob
        ) * 100

    if label == "with_mask":

        result = "Mask Detected"

    else:

        result = "No Mask Detected"

    return (
        result,
        confidence,
        len(faces)
    )

# ==========================
# API PREDICT
# ==========================

@app.route(
    "/predict",
    methods=["POST"]
)
def predict():

    if "image" not in request.files:

        return jsonify({
            "error":
            "No image uploaded"
        })

    file = request.files["image"]

    if file.filename == "":

        return jsonify({
            "error":
            "No image selected"
        })

    os.makedirs(
        "uploads",
        exist_ok=True
    )

    filename = secure_filename(
        file.filename
    )

    filepath = os.path.join(
        "uploads",
        filename
    )

    file.save(filepath)

    try:

        label, confidence, face_count = (
            predict_image(filepath)
        )

        os.remove(filepath)

        return jsonify({

            "label": label,

            "confidence": round(
                confidence,
                2
            ),

            "faces": face_count

        })

    except Exception as e:

        if os.path.exists(filepath):
            os.remove(filepath)

        return jsonify({
            "error": str(e)
        }), 500

# ==========================
# RUN
# ==========================

if __name__ == "__main__":
    app.run(
        debug=True,
        use_reloader=False,
        port=5001
    )