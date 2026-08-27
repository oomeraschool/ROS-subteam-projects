import cv2
import numpy as np

camera = cv2.VideoCapture(0)

ret, frame = camera.read()
cv2.imwrite('test2.png', frame)

gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
gray = cv2.GaussianBlur(gray, (5, 5), 0)

# Detect circles
circles = cv2.HoughCircles(
    gray,
    cv2.HOUGH_GRADIENT,
    dp=1,
    minDist=60,
    param1=100,
    param2=35,
    minRadius=30,
    maxRadius=110
)
# Step 5: Draw detected lines on the original image
if circles is not None:
    circles = np.round(circles[0]).astype(int)
    circle = circles[0]
    x, y, r = circle
    cv2.circle(frame, (x, y), r, (0, 255, 0), 2)  # Circle outline
    mask = np.zeros_like(gray)
    cv2.circle(mask,(x, y), int(r*0.75),255, -1)
    circle_pixels = cv2.bitwise_and(
        gray,
        gray,
        mask=mask
    )
    circle_values = gray[mask > 0]

    threshold = np.percentile(circle_values, 90)

    bright = cv2.threshold(
        circle_pixels,
        threshold,
        255,
        cv2.THRESH_BINARY
    )[1]
    num_labels, labels, stats, centroids = cv2.connectedComponentsWithStats(
        bright
    )
    num_lines = 0
    for i in range(1, num_labels):

        area = stats[i, cv2.CC_STAT_AREA]
        width = stats[i, cv2.CC_STAT_WIDTH]
        height = stats[i, cv2.CC_STAT_HEIGHT]

        # Ignore tiny noise
        if np.sqrt(height**2+width**2) > 20 and 50 < area < 1000:
            num_lines += 1
    if num_lines == 0:
        print("0 line circle")
    elif num_lines == 1:
        print("1 line circle")
    elif num_lines == 2:
        print("2 line circle")
    else:
        print("3 line circle")
else:
    print("No circles detected")
# Step 6: Display results
cv2.imshow('Original Image', frame)
cv2.waitKey(0)
cv2.destroyAllWindows()
