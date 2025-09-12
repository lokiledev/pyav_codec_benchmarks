import cv2
import numpy as np
from av import VideoFrame


def make_image(width: int, height: int, frame_i: int, fps: int) -> VideoFrame:
    ball_radius = 30

    img = np.zeros((height, width, 3), dtype=np.uint8)
    for h in range(height):
        img[h, :] = [
            0,
            int(100 * h / height),
            int(200 * h / height),
        ]  # Blue to purple gradient.

    x_pos = width // 2  # Center horizontally.
    y_pos = height // 2 + 80 * np.sin(2 * np.pi * frame_i / fps)
    y, x = np.ogrid[:height, :width]
    r_sq = (x - x_pos) ** 2 + (y - y_pos) ** 2
    img[r_sq < ball_radius**2] = [255, 200, 0]  # Gold color
    # Use OpenCV to embed the frame_i value in a big text label
    font = cv2.FONT_HERSHEY_SIMPLEX
    text = f"Frame {frame_i}"
    font_scale = 3
    thickness = 6
    text_size, _ = cv2.getTextSize(text, font, font_scale, thickness)
    text_x = (width - text_size[0]) // 2
    text_y = height - 60  # Place near the bottom
    cv2.putText(
        img,
        text,
        (text_x, text_y),
        font,
        font_scale,
        (255, 255, 255),
        thickness,
        lineType=cv2.LINE_AA,
    )

    return VideoFrame.from_ndarray(img, format="rgb24")
