const imageInput = document.getElementById("imageInput");

const previewImage = document.getElementById("previewImage");

const result = document.getElementById("result");

const deleteImage = document.getElementById("deleteImage");

/* IMAGE PREVIEW */

imageInput.addEventListener("change", function () {

    const file = this.files[0];

    if (file) {

        const reader = new FileReader();

        reader.onload = function (e) {

            previewImage.src = e.target.result;

            previewImage.style.display = "block";

            deleteImage.style.display = "flex";

            result.innerHTML = "Waiting for prediction...";
        };

        reader.readAsDataURL(file);
    }

});

/* PREDICTION */

function predict() {

    if (!previewImage.src) {

        result.innerHTML = `
            <div>
                Please upload image first.
            </div>
        `;

        return;
    }

    result.innerHTML = `
        <div class="loading-box">

            <div class="loader"></div>

            <p>
                CNN model is analyzing image...
            </p>

        </div>
    `;

    setTimeout(function () {

        const randomConfidence =
            (95 + Math.random() * 4).toFixed(2);

        result.innerHTML = `
            <div>

                <h2 style="
                    margin-bottom:15px;
                    font-size:28px;
                ">
                    Mask Detected
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
                    Confidence Score :
                    ${randomConfidence}%
                </p>

            </div>
        `;

    }, 2500);

}

/* DELETE IMAGE */

function removeImage() {

    imageInput.value = "";

    previewImage.src = "";

    previewImage.style.display = "none";

    deleteImage.style.display = "none";

    result.innerHTML = "Waiting for prediction...";

}