"""
Dlib 얼굴 랜드마크 모델 다운로드 스크립트
"""

import os
import requests
import bz2
from pathlib import Path

MODEL_URL = "http://dlib.net/files/shape_predictor_68_face_landmarks.dat.bz2"
MODELS_DIR = Path(__file__).parent / "models" / "dlib"
MODEL_PATH = MODELS_DIR / "shape_predictor_68_face_landmarks.dat"


def download_and_extract():
    """모델 다운로드 및 압축 해제"""

    # 디렉토리 생성
    MODELS_DIR.mkdir(parents=True, exist_ok=True)

    # 이미 존재하면 스킵
    if MODEL_PATH.exists():
        print(f"Model already exists at {MODEL_PATH}")
        return

    print(f"Downloading dlib model from {MODEL_URL}...")

    # 다운로드
    response = requests.get(MODEL_URL, stream=True)
    response.raise_for_status()

    # 압축 해제 및 저장
    compressed_path = MODELS_DIR / "shape_predictor_68_face_landmarks.dat.bz2"

    # 먼저 압축 파일 저장
    with open(compressed_path, "wb") as f:
        for chunk in response.iter_content(chunk_size=8192):
            f.write(chunk)

    print("Extracting...")

    # bz2 압축 해제
    with bz2.BZ2File(compressed_path, "rb") as f_in:
        with open(MODEL_PATH, "wb") as f_out:
            f_out.write(f_in.read())

    # 압축 파일 삭제
    compressed_path.unlink()

    print(f"Model downloaded and extracted to {MODEL_PATH}")


if __name__ == "__main__":
    download_and_extract()
