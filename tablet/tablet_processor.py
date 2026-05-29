
import cv2
import numpy as np
import math


def process_tablet(
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
            190,
            255,
            cv2.THRESH_BINARY
        )

        kernel = np.ones(
            (5, 5),
            np.uint8
        )

        thresh = cv2.morphologyEx(
            thresh,
            cv2.MORPH_OPEN,
            kernel
        )

        thresh = cv2.morphologyEx(
            thresh,
            cv2.MORPH_CLOSE,
            kernel
        )

        contours, _ = cv2.findContours(
            thresh,
            cv2.RETR_EXTERNAL,
            cv2.CHAIN_APPROX_SIMPLE
        )

        objects = []

        for cnt in contours:

            area = cv2.contourArea(
                cnt
            )

            if area < 1500:
                continue

            x, y, w, h = (
                cv2.boundingRect(
                    cnt
                )
            )

            aspect_ratio = (
                w / float(h)
            )

            if (
                aspect_ratio < 0.4
                or
                aspect_ratio > 2.5
            ):
                continue

            perimeter = (
                cv2.arcLength(
                    cnt,
                    True
                )
            )

            circularity = (
                4 * np.pi * area
            ) / (
                perimeter**2
                + 1e-6
            )

            hull = cv2.convexHull(
                cnt
            )

            hull_area = (
                cv2.contourArea(
                    hull
                )
            )

            solidity = (
                area /
                (hull_area + 1e-6)
            )

            objects.append({
                "contour":
                    cnt,
                "x": x,
                "y": y,
                "w": w,
                "h": h,
                "area":
                    area,
                "aspect_ratio":
                    aspect_ratio,
                "circularity":
                    circularity,
                "solidity":
                    solidity
            })

        if len(objects) == 0:

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
            o["area"]
            for o in objects
        ]

        ratios = [
            o[
                "aspect_ratio"
            ]
            for o in objects
        ]

        circularities = [
            o[
                "circularity"
            ]
            for o in objects
        ]

        solidities = [
            o[
                "solidity"
            ]
            for o in objects
        ]

        median_area = np.median(
            areas
        )

        median_ratio = np.median(
            ratios
        )

        median_circularity = (
            np.median(
                circularities
            )
        )

        median_solidity = (
            np.median(
                solidities
            )
        )

        good_count = 0
        defective_count = 0

        for obj in objects:

            area_diff = abs(
                obj["area"]
                - median_area
            ) / median_area

            ratio_diff = abs(
                obj[
                    "aspect_ratio"
                ]
                - median_ratio
            ) / median_ratio

            circularity_diff = abs(
                obj[
                    "circularity"
                ]
                - median_circularity
            ) / (
                median_circularity
            )

            solidity_diff = abs(
                obj[
                    "solidity"
                ]
                - median_solidity
            ) / median_solidity

            anomaly_score = (
                area_diff
                + ratio_diff
                + circularity_diff
                + solidity_diff
            )

            is_defective = (
                anomaly_score
                > 0.55
            )

            if is_defective:

                color = (
                    0,0,255
                )

                label = (
                    "DEFECTIVE"
                )

                defective_count += 1

            else:

                color = (
                    0,255,0
                )

                label = "GOOD"

                good_count += 1

            x = obj["x"]
            y = obj["y"]
            w = obj["w"]
            h = obj["h"]

            cv2.rectangle(
                output,
                (x, y),
                (x+w, y+h),
                color,
                3
            )

            cv2.putText(
                output,
                label,
                (x, y-10),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.6,
                color,
                2
            )

        status = (
            "FAIL"
            if defective_count
            > 0
            else "PASS"
        )

        cv2.putText(
            output,
            f"Good: {good_count}",
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

        object_memory = {}
        next_id = 0

        MAX_DISTANCE = 80

        calibration_circularities = []
        calibration_solidities = []

        CALIBRATION_FRAMES = 50

        reference_ready = False

        median_circularity = 1
        median_solidity = 1

        frame_count = 0

        def get_centroid(
            x,
            y,
            w,
            h
        ):

            return (
                x + w // 2,
                y + h // 2
            )

        good_count = 0
        defective_count = 0
        status = "PASS"

        while True:

            ret, frame = cap.read()

            if not ret:
                break

            frame_count += 1

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
                190,
                255,
                cv2.THRESH_BINARY
            )

            h, w = thresh.shape

            mask = np.zeros_like(
                thresh
            )

            cv2.rectangle(
                mask,
                (int(w*0.20),0),
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

            thresh = (
                cv2.morphologyEx(
                    thresh,
                    cv2.MORPH_OPEN,
                    kernel,
                    iterations=1
                )
            )

            thresh = (
                cv2.morphologyEx(
                    thresh,
                    cv2.MORPH_CLOSE,
                    kernel,
                    iterations=1
                )
            )

            contours, _ = (
                cv2.findContours(
                    thresh,
                    cv2.RETR_EXTERNAL,
                    cv2.CHAIN_APPROX_SIMPLE
                )
            )

            detections = []

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

                aspect_ratio = (
                    w_box /
                    (
                        h_box
                        + 1e-6
                    )
                )

                if (
                    aspect_ratio < 0.5
                    or
                    aspect_ratio > 2.5
                ):
                    continue

                perimeter = (
                    cv2.arcLength(
                        cnt,
                        True
                    )
                )

                circularity = (
                    4*np.pi*area
                ) / (
                    perimeter**2
                    + 1e-6
                )

                hull = (
                    cv2.convexHull(
                        cnt
                    )
                )

                hull_area = (
                    cv2.contourArea(
                        hull
                    )
                )

                solidity = (
                    area /
                    (
                        hull_area
                        + 1e-6
                    )
                )

                if area > 3500:
                    continue

                detections.append({
                    "contour":
                        cnt,
                    "x": x,
                    "y": y,
                    "w":
                        w_box,
                    "h":
                        h_box,
                    "circularity":
                        circularity,
                    "solidity":
                        solidity
                })

            if (
                frame_count
                <=
                CALIBRATION_FRAMES
            ):

                for det in (
                    detections
                ):

                    calibration_circularities.append(
                        det[
                            "circularity"
                        ]
                    )

                    calibration_solidities.append(
                        det[
                            "solidity"
                        ]
                    )

            elif (
                not
                reference_ready
            ):

                median_circularity = (
                    np.median(
                        calibration_circularities
                    )
                )

                median_solidity = (
                    np.median(
                        calibration_solidities
                    )
                )

                reference_ready = True

            current_objects = {}

            good_count = 0
            defective_count = 0

            id="jbmjlwm"
            for det in detections:

                x = det["x"]
                y = det["y"]
                w_box = det["w"]
                h_box = det["h"]

                cx, cy = get_centroid(
                    x,
                    y,
                    w_box,
                    h_box
                )

                matched_id = None
                min_distance = (
                    999999
                )

                # -------------------------
                # TRACK OBJECT
                # -------------------------
                for (
                    obj_id,
                    data
                ) in (
                    object_memory
                    .items()
                ):

                    old_x, old_y = (
                        data[
                            "centroid"
                        ]
                    )

                    dist = (
                        math.sqrt(
                            (
                                cx
                                - old_x
                            )**2
                            +
                            (
                                cy
                                - old_y
                            )**2
                        )
                    )

                    if (
                        dist
                        <
                        min_distance
                        and
                        dist
                        <
                        MAX_DISTANCE
                    ):

                        min_distance = (
                            dist
                        )

                        matched_id = (
                            obj_id
                        )

                # -------------------------
                # NEW OBJECT
                # -------------------------
                if (
                    matched_id
                    is None
                ):

                    matched_id = (
                        next_id
                    )

                    next_id += 1

                    object_memory[
                        matched_id
                    ] = {

                        "centroid":
                        (
                            cx,
                            cy
                        ),

                        "defective":
                        False,

                        "bad_frames":
                        0,

                        "defect_memory":
                        0
                    }

                # -------------------------
                # DEFECT LOGIC
                # -------------------------
                is_defective = (
                    False
                )

                if (
                    reference_ready
                ):

                    circularity_diff = abs(
                        det[
                            "circularity"
                        ]
                        -
                        median_circularity
                    ) / (
                        median_circularity
                        + 1e-6
                    )

                    contour = det[
                        "contour"
                    ]

                    perimeter = (
                        cv2.arcLength(
                            contour,
                            True
                        )
                    )

                    approx = (
                        cv2.approxPolyDP(
                            contour,
                            0.02
                            *
                            perimeter,
                            True
                        )
                    )

                    roughness = (
                        len(
                            approx
                        )
                    )

                    # chipped edge
                    if (
                        circularity_diff
                        > 0.28
                    ):
                        is_defective = (
                            True
                        )

                    # missing chunk
                    if (
                        det[
                            "solidity"
                        ]
                        < 0.86
                    ):
                        is_defective = (
                            True
                        )

                    # weird contour
                    if (
                        roughness
                        > 10
                    ):
                        is_defective = (
                            True
                        )

                # -------------------------
                # DEFECT MEMORY
                # -------------------------
                if (
                    is_defective
                ):

                    object_memory[
                        matched_id
                    ][
                        "defect_memory"
                    ] = 20

                else:

                    object_memory[
                        matched_id
                    ][
                        "defect_memory"
                    ] = max(
                        0,

                        object_memory[
                            matched_id
                        ][
                            "defect_memory"
                        ] - 1
                    )

                # -------------------------
                # 2 FRAME CONFIRMATION
                # -------------------------
                if (
                    is_defective
                ):

                    object_memory[
                        matched_id
                    ][
                        "bad_frames"
                    ] += 1

                else:

                    object_memory[
                        matched_id
                    ][
                        "bad_frames"
                    ] = max(
                        0,

                        object_memory[
                            matched_id
                        ][
                            "bad_frames"
                        ] - 1
                    )

                if (
                    object_memory[
                        matched_id
                    ][
                        "bad_frames"
                    ]
                    >= 2
                ):

                    object_memory[
                        matched_id
                    ][
                        "defective"
                    ] = True

                persistent_defect = (
                    object_memory[
                        matched_id
                    ][
                        "defective"
                    ]
                )

                current_objects[
                    matched_id
                ] = {

                    "centroid":
                    (
                        cx,
                        cy
                    ),

                    "defective":
                    persistent_defect,

                    "bad_frames":
                    object_memory[
                        matched_id
                    ][
                        "bad_frames"
                    ],

                    "defect_memory":
                    object_memory[
                        matched_id
                    ][
                        "defect_memory"
                    ]
                }

                # -------------------------
                # DRAW
                # -------------------------
                if (
                    persistent_defect
                ):

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

            object_memory = (
                current_objects
            )

            # -------------------------
            # DASHBOARD
            # -------------------------
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
                f"Defective:"
                f"{defective_count}",
                (20, 90),
                cv2.FONT_HERSHEY_SIMPLEX,
                1,
                (0,0,255),
                3
            )

            cv2.putText(
                output,
                f"Status:"
                f"{status}",
                (20, 140),
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
            "good": good_count,
            "defective": defective_count,
            "status": status
        }

    # fallback
    return {
        "good": 0,
        "defective": 0,
        "status": "PASS"
    }