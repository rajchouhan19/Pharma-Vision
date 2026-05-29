
from flask import (
    Flask,
    render_template,
    request,
    redirect
)

import os

from tablet.tablet_processor import (
    process_tablet
)

from capsule.capsule_processor import (
    process_capsule
)

app = Flask(__name__)

# ======================================
# FOLDERS
# ======================================
UPLOAD_FOLDER = (
    "static/uploads"
)

OUTPUT_FOLDER = (
    "static/outputs"
)

app.config[
    "UPLOAD_FOLDER"
] = UPLOAD_FOLDER

app.config[
    "OUTPUT_FOLDER"
] = OUTPUT_FOLDER

os.makedirs(
    UPLOAD_FOLDER,
    exist_ok=True
)

os.makedirs(
    OUTPUT_FOLDER,
    exist_ok=True
)

# ======================================
# HOME
# ======================================
@app.route("/")
def home():

    return render_template(
        "index.html"
    )


# ======================================
# PROCESS FILE
# ======================================
@app.route(
    "/process/<inspection_type>",
    methods=["POST"]
)
def process_file(
    inspection_type
):

    # ------------------------------
    # CHECK FILE
    # ------------------------------
    if (
        "file"
        not in request.files
    ):
        return redirect("/")

    file = request.files[
        "file"
    ]

    if (
        file.filename == ""
    ):
        return redirect("/")

    # ------------------------------
    # SAVE FILE
    # ------------------------------
    filename = (
        file.filename
    )

    input_path = os.path.join(
        app.config[
            "UPLOAD_FOLDER"
        ],
        filename
    )

    file.save(
        input_path
    )

    extension = (
        filename
        .split(".")[-1]
        .lower()
    )

    # ------------------------------
    # OUTPUT PATH
    # ------------------------------
    output_name = (
        "processed_"
        + filename
    )

    output_path = os.path.join(
        app.config[
            "OUTPUT_FOLDER"
        ],
        output_name
    )

    # ==================================
    # TABLET
    # ==================================
    if (
        inspection_type
        == "tablet"
    ):

        result = (
            process_tablet(
                input_path,
                output_path,
                extension
            )
        )
        print(result)

    # ==================================
    # CAPSULE
    # ==================================
    else:

        result = (
            process_capsule(
                input_path,
                output_path,
                extension
            )
        )

    # ------------------------------
    # IMAGE OR VIDEO
    # ------------------------------
    video_formats = [
        "mp4",
        "avi",
        "mov"
    ]

    media_type = (
        "video"
        if extension
        in video_formats
        else "image"
    )

    # ==================================
    # RESULT PAGE
    # ==================================
    return render_template(
        "result.html",

        output_file=
        output_name,

        media_type=
        media_type,

        good=
        result["good"],

        defective=
        result[
            "defective"
        ],

        status=
        result[
            "status"
        ],

        inspection=
        inspection_type
    )


# ======================================
# RUN
# ======================================
if __name__ == "__main__":

    app.run(
        debug=True
    )