import cv2
import numpy as np


# ============================================================
# SETTINGS
# ============================================================

# Hough circle settings
CIRCLE_DP = 1.2
CIRCLE_MIN_DIST = 100

CIRCLE_PARAM1 = 100

# Increase this to make Hough more selective
CIRCLE_PARAM2 = 45

CIRCLE_MIN_RADIUS = 40
CIRCLE_MAX_RADIUS = 250


# White detection
WHITE_VALUE = 150
WHITE_SATURATION = 100

# Minimum percentage of the circle that must be white
MIN_WHITE_FRACTION = 0.45


# ============================================================
# CAMERA
# ============================================================

camera = cv2.VideoCapture(0)

if not camera.isOpened():
    print("Could not open camera")
    exit()


while True:

    ret, frame = camera.read()

    if not ret:
        break


    # ========================================================
    # GRAYSCALE
    # ========================================================

    gray = cv2.cvtColor(
        frame,
        cv2.COLOR_BGR2GRAY
    )

    blurred = cv2.GaussianBlur(
        gray,
        (7, 7),
        1.5
    )


    # ========================================================
    # WHITE MASK
    # ========================================================

    hsv = cv2.cvtColor(
        frame,
        cv2.COLOR_BGR2HSV
    )

    white_mask = cv2.inRange(
        hsv,
        np.array([
            0,
            0,
            WHITE_VALUE
        ]),
        np.array([
            180,
            WHITE_SATURATION,
            255
        ])
    )


    # ========================================================
    # HOUGH CIRCLES
    # ========================================================

    circles = cv2.HoughCircles(
        blurred,
        cv2.HOUGH_GRADIENT,
        dp=CIRCLE_DP,
        minDist=CIRCLE_MIN_DIST,
        param1=CIRCLE_PARAM1,
        param2=CIRCLE_PARAM2,
        minRadius=CIRCLE_MIN_RADIUS,
        maxRadius=CIRCLE_MAX_RADIUS
    )


    output = frame.copy()

    candidates = []


    # ========================================================
    # CHECK CIRCLE CANDIDATES
    # ========================================================

    if circles is not None:

        circles = np.round(
            circles[0]
        ).astype(int)


        for cx, cy, radius in circles:

            # -----------------------------------------------
            # Make sure circle is inside image
            # -----------------------------------------------

            if (
                cx - radius < 0 or
                cy - radius < 0 or
                cx + radius >= frame.shape[1] or
                cy + radius >= frame.shape[0]
            ):
                continue


            # -----------------------------------------------
            # Create circular mask
            # -----------------------------------------------

            # Create circular mask for the OUTER part of the sign
            circle_mask = np.zeros(
                gray.shape,
                dtype=np.uint8
            )

            cv2.circle(
                circle_mask,
                (cx, cy),
                int(radius * 0.90),
                255,
                -1
            )

            # Remove center of circle
            # This prevents the icon itself from affecting the score.
            cv2.circle(
                circle_mask,
                (cx, cy),
                int(radius * 0.55),
                0,
                -1
            )

            # Pixels in the outer ring
            ring_pixels = hsv[circle_mask > 0]

            if len(ring_pixels) == 0:
                continue

            # HSV values
            saturation = ring_pixels[:, 1]
            value = ring_pixels[:, 2]

            # "Background-like" pixels:
            # relatively bright + low saturation
            background_pixels = (
                    (saturation < 120) &
                    (value > 120)
            )

            background_fraction = np.mean(
                background_pixels
            )

            # Reject circles that don't have enough
            # background-like pixels around their perimeter
            if background_fraction < 0.45:
                continue


            # -----------------------------------------------
            # Save candidate
            # -----------------------------------------------
            candidates.append(
                (cx, cy, radius, background_fraction)
            )

    # ========================================================
    # REMOVE DUPLICATE CIRCLES
    # ========================================================

    # Sort best candidates first
    candidates.sort(
        key=lambda c: c[3],
        reverse=True
    )


    selected = []

    mask = np.zeros(frame.shape[:2], dtype=np.uint8)

    for candidate in candidates:

        cx, cy, radius, background_fraction = candidate

        duplicate = False


        for selected_circle in selected:

            sx, sy, sr, sw = selected_circle


            # Distance between centers
            distance = np.sqrt(
                (cx - sx) ** 2 +
                (cy - sy) ** 2
            )


            # If centers are close relative to the circle
            if distance < min(radius, sr) * 0.6:

                duplicate = True
                break


        if not duplicate:

            selected.append(candidate)
            cv2.circle(mask, center=(cx, cy), radius=radius, color=255, thickness=-1)
    masked = frame.copy()
    masked = cv2.bitwise_and(masked, masked, mask=mask)

    # ========================================================
    # DRAW SELECTED CIRCLES
    # ========================================================

    for cx, cy, radius, background_fraction in selected:

        # Circle
        cv2.circle(
            output,
            (cx, cy),
            radius,
            (0, 255, 0),
            3
        )


        # Bounding box
        cv2.rectangle(
            output,
            (
                cx - radius,
                cy - radius
            ),
            (
                cx + radius,
                cy + radius
            ),
            (0, 255, 0),
            2
        )


        # Label
        label = (
            f"CIRCLE "
            f"white={background_fraction:.2f}"
        )

        cv2.putText(
            output,
            label,
            (
                cx - radius,
                max(cy - radius - 10, 20)
            ),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.6,
            (0, 255, 0),
            2
        )


    # ========================================================
    # DISPLAY
    # ========================================================

    cv2.imshow(
        "Original",
        frame
    )

    cv2.imshow(
        "White Mask",
        white_mask
    )

    cv2.imshow(
        "Detected Circles",
        output
    )

    cv2.imshow(
        "Masked Image",
        masked
    )

    # ========================================================
    # QUIT
    # ========================================================

    if cv2.waitKey(1) & 0xFF == ord("q"):
        break


camera.release()
cv2.destroyAllWindows()