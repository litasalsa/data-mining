const imageInput = document.getElementById("imageInput");

const previewImage = document.getElementById("previewImage");

const result = document.getElementById("result");


/* IMAGE PREVIEW */

imageInput.addEventListener("change", function () {

    const file = this.files[0];

    previewImage.src = "";
    previewImage.style.display = "none";

    result.innerHTML = "Waiting for prediction...";

    if (file) {
        const reader = new FileReader();

        reader.onload = function (e) {
            previewImage.src = e.target.result;
            previewImage.style.display = "block";
        };

        reader.readAsDataURL(file);
    }
});

/* PREDICTION */

async function predict() {

    const file = imageInput.files[0];

    if (!file) {

        result.innerHTML = `
            <div>Please upload image first.</div>
        `;
        return;
    }

    result.innerHTML = `
        <div class="loading-box">
            <div class="loader"></div>
            <p>CNN model is analyzing image...</p>
        </div>
    `;

    const formData = new FormData();

    formData.append(
        "image",
        file
    );

    try {

        const response =
            await fetch(
                "/predict",
                {
                    method: "POST",
                    body: formData
                }
            );

        const data =
            await response.json();

        if (data.label === "Face Not Detected") {

            result.innerHTML = `
                <div>

                    <h2 style="
                        color:#ef4444;
                        margin-bottom:15px;
                    ">
                        Face Not Detected
                    </h2>

                    <p>
                        Please upload a clearer face image.
                    </p>

                </div>
            `;

            return;
        }


        result.innerHTML = `
            <div>

                <h2 style="
                    margin-bottom:15px;
                    font-size:28px;
                ">
                    ${data.label}
                </h2>

                <p style="
                    color:#cbd5e1;
                    margin-bottom:10px;
                ">
                    CNN model successfully analyzed image.
                </p>

                <p style="
                    color:#60a5fa;
                    font-weight:600;
                    font-size:18px;
                ">
                    Confidence Score : ${data.confidence}%
                </p>

            </div>
        `;

    } catch (error) {

        result.innerHTML =
            "Prediction failed.";

        console.error(error);
    }
}

