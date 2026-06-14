import cv2
import pandas as pd
from paddleocr import PaddleOCR
from rapidfuzz import fuzz

VIDEO_FILE = "/Users/hieu.dang/Downloads/text.mp4"
OUTPUT_CSV = "questions.csv"

# OCR
ocr = PaddleOCR(
    use_doc_orientation_classify=False,
    use_doc_unwarping=False,
    use_textline_orientation=False,
    lang="en"
)

cap = cv2.VideoCapture(VIDEO_FILE)

fps = cap.get(cv2.CAP_PROP_FPS)

prev_small = None
last_question = ""

rows = []

frame_no = 0

while True:

    ret, frame = cap.read()

    if not ret:
        break

    # giảm tải: kiểm tra 5 frame/lần
    if frame_no % 5 != 0:
        frame_no += 1
        continue

    h, w = frame.shape[:2]

    # detect scene change
    small = cv2.resize(
        cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY),
        (320, 180)
    )

    if prev_small is not None:

        diff = cv2.absdiff(small, prev_small)
        score = diff.mean()

        # màn hình chưa đổi
        if score < 3:
            frame_no += 1
            continue

    prev_small = small

    # đợi text ổn định
    target_frame = frame_no + int(fps * 0.8)

    cap.set(cv2.CAP_PROP_POS_FRAMES, target_frame)

    ret, frame = cap.read()

    if not ret:
        break

    h, w = frame.shape[:2]

    # ===== CROP =====

    question_crop = frame[
        int(h * 0.32):int(h * 0.65),
        int(w * 0.12):int(w * 0.75)
    ]

    a_crop = frame[
        int(h * 0.7):int(h * 0.95),
        int(w * 0.12):int(w * 0.48)
    ]

    b_crop = frame[
        int(h * 0.7):int(h * 0.95),
        int(w * 0.51):int(w * 0.88)
    ]

    # ===== OCR =====

    def extract_text(img):

        result = ocr.predict(img)

        lines = []

        try:
            for block in result:
                rec_texts = block.get("rec_texts", [])

                for text in rec_texts:
                    text = text.strip()

                    if text:
                        lines.append(text)

        except Exception:
            pass

        return " ".join(lines).strip()

    question = extract_text(question_crop)
    answer_a = extract_text(a_crop)
    answer_b = extract_text(b_crop)

    if len(question) < 10:
        frame_no += 1
        continue

    # loại trùng
    if fuzz.ratio(question, last_question) > 90:
        frame_no += 1
        continue

    last_question = question

    rows.append({
        "Question": question,
        "A": answer_a,
        "B": answer_b
    })

    print(f"Found: {question} -> A: {answer_a} | B: {answer_b}")

    frame_no = target_frame + 1

cap.release()

df = pd.DataFrame(rows)

df.drop_duplicates(
    subset=["Question"],
    inplace=True
)

df.to_csv(
    OUTPUT_CSV,
    index=False,
    encoding="utf-8-sig"
)

print()
print(f"Saved {len(df)} questions -> {OUTPUT_CSV}")