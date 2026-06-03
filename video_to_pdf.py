import cv2
import os
import img2pdf
import shutil
import numpy as np

# ▼▼ 設定エリア ▼▼
VIDEO_PATH = "Lecture1.mp4"          # 動画ファイル名
OUTPUT_DIR = "work_images"          # 一時保存する画像フォルダ名
OUTPUT_PDF = "lecture_complete.pdf" # 完成するPDF名
THRESHOLD = 1                      # 感度 (小さいほど敏感)
CHECK_INTERVAL = 13                 # チェック間隔

# ★ フォルダ削除設定
# 0 = PDF作成後に画像フォルダを「削除する」（デフォルト）
# 1 = 「削除しない」（残す）
KEEP_WORK_IMAGES = 0 
# ▲▲▲▲▲▲▲▲▲▲▲▲

def main():
    # ---------------------------------------------------------
    # STEP 1: 画像の抽出
    # ---------------------------------------------------------
    print(f"■ STEP 1: 動画 '{VIDEO_PATH}' から画像を抽出します...")
    
    cap = cv2.VideoCapture(VIDEO_PATH)
    if not cap.isOpened():
        print(f"エラー: '{VIDEO_PATH}' が見つかりません。")
        return

    if os.path.exists(OUTPUT_DIR):
        shutil.rmtree(OUTPUT_DIR)
    os.makedirs(OUTPUT_DIR)

    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    prev_frame_gray = None
    slide_count = 0
    frame_count = 0

    while True:
        ret, frame = cap.read()
        if not ret: break

        if total_frames > 0 and frame_count % (total_frames // 10) == 0:
            print(f"   進捗: {int(frame_count/total_frames*100)}% ... ({slide_count}枚 保存)")

        if frame_count % CHECK_INTERVAL == 0:
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            is_new_slide = False
            
            if prev_frame_gray is None:
                is_new_slide = True
            else:
                diff = cv2.absdiff(prev_frame_gray, gray)
                if np.mean(diff) > THRESHOLD:
                    is_new_slide = True

            if is_new_slide:
                filename = os.path.join(OUTPUT_DIR, f"slide_{slide_count:04d}.jpg")
                cv2.imwrite(filename, frame)
                prev_frame_gray = gray
                slide_count += 1

        frame_count += 1
    cap.release()

    # ---------------------------------------------------------
    # STEP 2: 一時停止 (手作業タイム)
    # ---------------------------------------------------------
    print("\n" + "="*60)
    print(f"★ 画像抽出完了！フォルダ '{OUTPUT_DIR}' が作成されました。")
    print("1. エクスプローラーでこのフォルダを開いてください。")
    print("2. 不要な画像（顔のアップなど）を目視で削除してください。")
    print("="*60)
    
    input(" >> 削除作業が終わったら、ここで [Enterキー] を押してPDF化を開始してください...")

    # ---------------------------------------------------------
    # STEP 3: PDF結合
    # ---------------------------------------------------------
    print("\n■ STEP 3: 残った画像をPDFにまとめています...")

    img_files = [f for f in os.listdir(OUTPUT_DIR) if f.endswith(".jpg")]
    img_files.sort()

    if not img_files:
        print("エラー: 画像がすべて削除されたか、見つかりません。処理を中止します。")
        return

    img_paths = [os.path.join(OUTPUT_DIR, f) for f in img_files]

    try:
        with open(OUTPUT_PDF, "wb") as f:
            f.write(img2pdf.convert(img_paths))
        print(f"\n成功！ '{OUTPUT_PDF}' が作成されました！")
        
        # ▼▼ 設定に基づく削除処理 ▼▼
        if KEEP_WORK_IMAGES == 0:
            print(f"設定(0)に基づき、作業用フォルダ '{OUTPUT_DIR}' を削除しています...")
            shutil.rmtree(OUTPUT_DIR)
            print("削除完了。お疲れ様でした！")
        else:
            print(f"設定(1)に基づき、作業用フォルダ '{OUTPUT_DIR}' は削除せずに残します。")

    except Exception as e:
        print(f"PDF作成エラー: {e}")

if __name__ == "__main__":
    main()
