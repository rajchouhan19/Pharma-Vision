import cv2
import numpy as np


def process_capsule(
    input_path,
    output_path,
    extension
):

    image_formats = [
        "jpg",
        "jpeg",
        "png"
    ]

    video_formats = [
        "mp4",
        "avi",
        "mov"
    ]

    # =====================================
    # IMAGE PROCESSING
    # =====================================
    if extension in image_formats:

        image = cv2.imread(
            input_path
        )

        output = image.copy()

        gray = cv2.cvtColor(
            image,
            cv2.COLOR_BGR2GRAY
        )

        blur = cv2.GaussianBlur(
            gray,
            (7, 7),
            0
        )

        _, thresh = cv2.threshold(
            blur,
            135,
            255,
            cv2.THRESH_BINARY
        )

        h, w = thresh.shape

        mask = np.zeros_like(
            thresh
        )

        cv2.rectangle(
            mask,
            (int(w * 0.23), 0),
            (int(w * 0.82), h),
            255,
            -1
        )

        thresh = cv2.bitwise_and(
            thresh,
            mask
        )

        kernel = (
            cv2.getStructuringElement(
                cv2.MORPH_ELLIPSE,
                (5, 5)
            )
        )

        thresh = cv2.dilate(
            thresh,
            kernel,
            iterations=1
        )

        thresh = cv2.morphologyEx(
            thresh,
            cv2.MORPH_CLOSE,
            kernel,
            iterations=1
        )

        thresh = cv2.morphologyEx(
            thresh,
            cv2.MORPH_OPEN,
            kernel,
            iterations=1
        )

        contours, _ = (
            cv2.findContours(
                thresh,
                cv2.RETR_EXTERNAL,
                cv2.CHAIN_APPROX_SIMPLE
            )
        )

        detected_capsules = []

        for cnt in contours:

            area = (
                cv2.contourArea(
                    cnt
                )
            )

            if area < 250:
                continue

            x, y, w_box, h_box = (
                cv2.boundingRect(
                    cnt
                )
            )

            margin = 10

            if (
                x < margin
                or
                y < margin
                or
                x + w_box >
                image.shape[1]
                - margin
                or
                y + h_box >
                image.shape[0]
                - margin
            ):
                continue

            aspect_ratio = max(
                w_box,
                h_box
            ) / (
                min(
                    w_box,
                    h_box
                ) + 1e-6
            )

            if (
                aspect_ratio < 1.1
                or
                aspect_ratio > 6
            ):
                continue

            detected_capsules.append({
                "contour":
                    cnt,
                "x": x,
                "y": y,
                "w":
                    w_box,
                "h":
                    h_box,
                "area":
                    area,
                "ratio":
                    aspect_ratio
            })

        if len(
            detected_capsules
        ) == 0:

            cv2.imwrite(
                output_path,
                output
            )

            return {
                "good": 0,
                "defective": 0,
                "status": "PASS"
            }

        areas = [
            obj["area"]
            for obj
            in detected_capsules
        ]

        ratios = [
            obj["ratio"]
            for obj
            in detected_capsules
        ]

        median_area = (
            np.median(
                areas
            )
        )

        median_ratio = (
            np.median(
                ratios
            )
        )

        good_count = 0
        defective_count = 0

        for obj in (
            detected_capsules
        ):

            cnt = obj[
                "contour"
            ]

            x = obj["x"]
            y = obj["y"]
            w_box = obj["w"]
            h_box = obj["h"]

            area = obj[
                "area"
            ]

            ratio = obj[
                "ratio"
            ]

            extent = area / (
                (
                    w_box
                    *
                    h_box
                )
                + 1e-6
            )

            area_diff = abs(
                area
                -
                median_area
            ) / median_area

            ratio_diff = abs(
                ratio
                -
                median_ratio
            ) / median_ratio

            is_defective = (
                False
            )

            if (
                area_diff
                > 0.65
            ):
                is_defective = (
                    True
                )

            if (
                ratio_diff
                > 0.75
            ):
                is_defective = (
                    True
                )

            if (
                extent
                < 0.30
            ):
                is_defective = (
                    True
                )

            if is_defective:

                color = (
                    0,
                    0,
                    255
                )

                label = (
                    "DEFECTIVE"
                )

                defective_count += 1

            else:

                color = (
                    0,
                    255,
                    0
                )

                label = (
                    "GOOD"
                )

                good_count += 1

            cv2.rectangle(
                output,
                (
                    x,
                    y
                ),
                (
                    x+w_box,
                    y+h_box
                ),
                color,
                2
            )

            cv2.putText(
                output,
                label,
                (
                    x,
                    y-8
                ),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.55,
                color,
                2
            )

        status = (
            "FAIL"
            if
            defective_count
            > 0
            else
            "PASS"
        )

        cv2.putText(
            output,
            f"Good: "
            f"{good_count}",
            (20, 40),
            cv2.FONT_HERSHEY_SIMPLEX,
            1,
            (0,255,0),
            3
        )

        cv2.putText(
            output,
            f"Defective: "
            f"{defective_count}",
            (20, 90),
            cv2.FONT_HERSHEY_SIMPLEX,
            1,
            (0,0,255),
            3
        )

        cv2.putText(
            output,
            f"Status: "
            f"{status}",
            (20, 140),
            cv2.FONT_HERSHEY_SIMPLEX,
            1.2,
            (0,255,255),
            3
        )

        cv2.imwrite(
            output_path,
            output
        )

        return {
            "good":
                good_count,
            "defective":
                defective_count,
            "status":
                status
        }

    # =====================================
    # VIDEO PROCESSING
    # =====================================
    elif extension in video_formats:

        cap = cv2.VideoCapture(
            input_path
        )

        original_fps = int(
            cap.get(
                cv2.CAP_PROP_FPS
            )
        )

        fps = max(
            5,
            original_fps // 2
        )

        width = int(
            cap.get(
                cv2.CAP_PROP_FRAME_WIDTH
            )
        )

        height = int(
            cap.get(
                cv2.CAP_PROP_FRAME_HEIGHT
            )
        )

        fourcc = (
            cv2.VideoWriter_fourcc(
                *'avc1'
            )
        )
        output_path = (
            output_path
            .rsplit(".", 1)[0]
            + ".mp4"
        )

        out = cv2.VideoWriter(
            output_path,
            fourcc,
            fps,
            (width, height)
        )

        good_count = 0
        defective_count = 0
        status = "PASS"

        while True:

            ret, frame = (
                cap.read()
            )

            if not ret:
                break

            output = frame.copy()

            gray = cv2.cvtColor(
                frame,
                cv2.COLOR_BGR2GRAY
            )

            blur = cv2.GaussianBlur(
                gray,
                (7, 7),
                0
            )

            _, thresh = cv2.threshold(
                blur,
                135,
                255,
                cv2.THRESH_BINARY
            )

            h, w = thresh.shape

            mask = np.zeros_like(
                thresh
            )

            cv2.rectangle(
                mask,
                (int(w*0.23),0),
                (
                    int(w*0.82),
                    h
                ),
                255,
                -1
            )

            thresh = cv2.bitwise_and(
                thresh,
                mask
            )

            kernel = (
                cv2.getStructuringElement(
                    cv2.MORPH_ELLIPSE,
                    (5, 5)
                )
            )

            thresh = cv2.dilate(
                thresh,
                kernel,
                iterations=1
            )

            thresh = cv2.morphologyEx(
                thresh,
                cv2.MORPH_CLOSE,
                kernel,
                iterations=1
            )

            thresh = cv2.morphologyEx(
                thresh,
                cv2.MORPH_OPEN,
                kernel,
                iterations=1
            )

            contours, _ = (
                cv2.findContours(
                    thresh,
                    cv2.RETR_EXTERNAL,
                    cv2.CHAIN_APPROX_SIMPLE
                )
            )

            detected_capsules = []

            for cnt in contours:

                area = (
                    cv2.contourArea(
                        cnt
                    )
                )

                if area < 250:
                    continue

                x,y,w_box,h_box = (
                    cv2.boundingRect(
                        cnt
                    )
                )

                aspect_ratio = max(
                    w_box,
                    h_box
                ) / (
                    min(
                        w_box,
                        h_box
                    )
                    + 1e-6
                )

                if (
                    aspect_ratio < 1.1
                    or
                    aspect_ratio > 6
                ):
                    continue

                detected_capsules.append({
                    "contour":
                        cnt,
                    "x": x,
                    "y": y,
                    "w":
                        w_box,
                    "h":
                        h_box,
                    "area":
                        area,
                    "ratio":
                        aspect_ratio
                })

            if len(
                detected_capsules
            ) > 0:

                areas = [
                    obj["area"]
                    for obj in
                    detected_capsules
                ]

                ratios = [
                    obj["ratio"]
                    for obj in
                    detected_capsules
                ]

                median_area = (
                    np.median(
                        areas
                    )
                )

                median_ratio = (
                    np.median(
                        ratios
                    )
                )

            else:

                median_area = 1
                median_ratio = 1

            good_count = 0
            defective_count = 0

            for obj in (
                detected_capsules
            ):

                x = obj["x"]
                y = obj["y"]
                w_box = obj["w"]
                h_box = obj["h"]

                area = obj["area"]
                ratio = obj["ratio"]

                extent = (
                    area /
                    (
                        w_box
                        *
                        h_box
                        + 1e-6
                    )
                )

                area_diff = abs(
                    area
                    -
                    median_area
                ) / median_area

                ratio_diff = abs(
                    ratio
                    -
                    median_ratio
                ) / median_ratio

                is_defective = (
                    False
                )

                if (
                    area_diff
                    > 0.65
                ):
                    is_defective = (
                        True
                    )

                if (
                    ratio_diff
                    > 0.75
                ):
                    is_defective = (
                        True
                    )

                if (
                    extent
                    < 0.30
                ):
                    is_defective = (
                        True
                    )

                if is_defective:

                    color = (
                        0,
                        0,
                        255
                    )

                    label = (
                        "DEFECTIVE"
                    )

                    defective_count += 1

                else:

                    color = (
                        0,
                        255,
                        0
                    )

                    label = (
                        "GOOD"
                    )

                    good_count += 1

                cv2.rectangle(
                    output,
                    (
                        x,
                        y
                    ),
                    (
                        x+w_box,
                        y+h_box
                    ),
                    color,
                    2
                )

                cv2.putText(
                    output,
                    label,
                    (
                        x,
                        y-8
                    ),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.55,
                    color,
                    2
                )

            status = (
                "FAIL"
                if
                defective_count
                > 0
                else
                "PASS"
            )

            cv2.putText(
                output,
                f"Good: "
                f"{good_count}",
                (20,40),
                cv2.FONT_HERSHEY_SIMPLEX,
                1,
                (0,255,0),
                3
            )

            cv2.putText(
                output,
                f"Defective: "
                f"{defective_count}",
                (20,90),
                cv2.FONT_HERSHEY_SIMPLEX,
                1,
                (0,0,255),
                3
            )

            cv2.putText(
                output,
                f"Status: "
                f"{status}",
                (20,140),
                cv2.FONT_HERSHEY_SIMPLEX,
                1.2,
                (0,255,255),
                3
            )

            out.write(
                output
            )

        cap.release()
        out.release()

        return {
            "good":
                good_count,
            "defective":
                defective_count,
            "status":
                status
        }
