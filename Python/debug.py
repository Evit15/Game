import cv2

VIDEO_FILE = "/Users/hieu.dang/Downloads/text.mp4"

cap = cv2.VideoCapture(VIDEO_FILE)

fps = cap.get(cv2.CAP_PROP_FPS)

# lấy frame ở giây 30
target_sec = 27

cap.set(
    cv2.CAP_PROP_POS_FRAMES,
    int(fps * target_sec)
)

ret, frame = cap.read()

if not ret:
    raise Exception("Cannot read frame")

h, w = frame.shape[:2]

# ===== QUESTION =====

q_y1 = int(h * 0.32)
q_y2 = int(h * 0.65)

q_x1 = int(w * 0.12)
q_x2 = int(w * 0.75)

# ===== A =====

a_y1 = int(h * 0.7)
a_y2 = int(h * 0.95)

a_x1 = int(w * 0.15)
a_x2 = int(w * 0.48)

# ===== B =====

b_y1 = int(h * 0.7)
b_y2 = int(h * 0.95)

b_x1 = int(w * 0.55)
b_x2 = int(w * 0.88)

# draw rectangles

cv2.rectangle(
    frame,
    (q_x1, q_y1),
    (q_x2, q_y2),
    (0, 255, 0),
    3
)

cv2.putText(
    frame,
    "QUESTION",
    (q_x1, q_y1 - 10),
    cv2.FONT_HERSHEY_SIMPLEX,
    1,
    (0, 255, 0),
    2
)

cv2.rectangle(
    frame,
    (a_x1, a_y1),
    (a_x2, a_y2),
    (255, 0, 0),
    3
)

cv2.putText(
    frame,
    "ANSWER A",
    (a_x1, a_y1 - 10),
    cv2.FONT_HERSHEY_SIMPLEX,
    1,
    (255, 0, 0),
    2
)

cv2.rectangle(
    frame,
    (b_x1, b_y1),
    (b_x2, b_y2),
    (0, 0, 255),
    3
)

cv2.putText(
    frame,
    "ANSWER B",
    (b_x1, b_y1 - 10),
    cv2.FONT_HERSHEY_SIMPLEX,
    1,
    (0, 0, 255),
    2
)

cv2.imwrite("debug_crop.jpg", frame)

print("Saved: debug_crop.jpg")

cap.release()