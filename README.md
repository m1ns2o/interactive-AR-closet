# Closet AI

통합 AI 스타일링 플랫폼 - Virtual Try-On, Personal Color 분석, 얼굴형 진단을 하나의 서비스로 제공합니다.

## Features

- **Virtual Try-On**: IDM-VTON 모델을 활용한 가상 의류 착용
- **Personal Color**: ML 기반 퍼스널 컬러 진단 (봄/여름/가을/겨울)
- **Face Shape**: Vision Transformer 기반 얼굴형 분류 및 스타일 추천

## Tech Stack

### Backend (Python)
- FastAPI - 고성능 웹 프레임워크
- Gradio Client - Hugging Face 모델 API
- OpenCV + dlib - 얼굴 인식 및 랜드마크 검출
- scikit-learn - 퍼스널 컬러 분류 모델
- Transformers - 얼굴형 분류 모델

### Frontend (Vue)
- Vue 3 + TypeScript
- Nuxt UI - 컴포넌트 라이브러리
- Vite - 빌드 도구
- ECharts - 데이터 시각화

## Project Structure

```
interactive-AR-closet/
├── backend/                    # Python FastAPI 백엔드
│   ├── app/
│   │   ├── main.py            # 메인 서버
│   │   ├── schemas.py         # Pydantic 모델
│   │   └── services/
│   │       ├── vton_service.py           # Virtual Try-On
│   │       ├── personal_color_service.py # 퍼스널 컬러
│   │       └── face_shape_service.py     # 얼굴형 분석
│   ├── models/                # ML 모델 파일
│   │   ├── dlib/
│   │   ├── personal_color_model.joblib
│   │   └── label_encoder.joblib
│   ├── requirements.txt
│   └── download_dlib_model.py
│
└── interactive-closet/         # Vue 프론트엔드
    ├── src/
    │   ├── App.vue            # 메인 레이아웃 (사이드바)
    │   └── pages/
    │       ├── index.vue      # Virtual Try-On
    │       ├── personal-color.vue
    │       └── face-shape.vue
    └── package.json
```

## Installation

### Backend

```bash
cd backend

# 가상환경 생성 (선택사항)
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 의존성 설치
pip install -r requirements.txt

# dlib 모델 다운로드
python download_dlib_model.py
```

### Frontend

```bash
cd interactive-closet

# 의존성 설치
npm install
```

## Usage

### Development

```bash
# Terminal 1: Backend
cd backend
uvicorn app.main:app --reload --port 8000

# Terminal 2: Frontend
cd interactive-closet
npm run dev
```

- Backend: http://localhost:8000
- Frontend: http://localhost:5173

### Production

```bash
# Frontend 빌드
cd interactive-closet
npm run build

# 빌드된 파일을 backend/static으로 복사
cp -r dist/* ../backend/static/

# 서버 실행
cd ../backend
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/tryon` | POST | Virtual Try-On |
| `/api/analyze` | POST | 퍼스널 컬러 분석 |
| `/api/analyze/face-shape` | POST | 얼굴형 분석 |
| `/api/progress/{session_id}` | GET | SSE 진행 상황 |
| `/api/health` | GET | 헬스 체크 |

### Virtual Try-On

```bash
curl -X POST http://localhost:8000/api/tryon \
  -F "humanImage=@person.jpg" \
  -F "garmentImage=@garment.jpg" \
  -F "description=A person wearing the garment"
```

### Personal Color

```bash
curl -X POST http://localhost:8000/api/analyze \
  -F "image=@face.jpg"
```

### Face Shape

```bash
curl -X POST http://localhost:8000/api/analyze/face-shape \
  -F "image=@face.jpg"
```

## Configuration

`.env` 파일 생성:

```env
# Hugging Face Token (Virtual Try-On 우선순위 향상)
HF_TOKEN=hf_your_token_here
```

## License

MIT
