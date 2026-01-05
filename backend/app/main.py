"""
Closet AI Backend - Unified API Server
Virtual Try-On + Personal Color Analysis + Face Shape Classification
"""

from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, StreamingResponse
from PIL import Image
from pathlib import Path
import io
import json
import asyncio
import uuid
from typing import Optional

from .schemas import AnalysisResponse, FaceShapeResponse, VTONResponse, ProgressInfo
from .services import analyze_image, pil_to_cv2, analyze_face_shape, VTONService


app = FastAPI(title="Closet AI API", description="Virtual Try-On, Personal Color & Face Shape Analysis")

# 정적 파일 경로 설정 (프로젝트 루트의 public 폴더)
STATIC_DIR = Path(__file__).parent.parent.parent / "public"

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://localhost:3000",
        "http://localhost:8000",
        "http://127.0.0.1:5173",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:8000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# VTON 서비스 인스턴스
vton_service = VTONService()

# SSE 세션 저장소
sse_sessions: dict[str, asyncio.Queue] = {}


# ======================
#       Health Check
# ======================

@app.get("/api/health")
async def api_health():
    return {
        "message": "Closet AI API",
        "status": "running",
        "services": ["virtual-tryon", "personal-color", "face-shape"]
    }


@app.get("/health")
async def health_check():
    return {"status": "healthy"}


# ======================
#    Virtual Try-On
# ======================

@app.get("/api/progress/{session_id}")
async def progress_stream(session_id: str):
    """SSE 엔드포인트 - 진행 상황 스트리밍"""

    if session_id not in sse_sessions:
        sse_sessions[session_id] = asyncio.Queue()

    queue = sse_sessions[session_id]

    async def event_generator():
        try:
            while True:
                try:
                    # 30초 타임아웃으로 대기
                    data = await asyncio.wait_for(queue.get(), timeout=30.0)
                    yield f"data: {json.dumps(data)}\n\n"

                    # complete 또는 error 상태면 종료
                    if data.get("status") in ["complete", "error"]:
                        break
                except asyncio.TimeoutError:
                    # Keep-alive
                    yield f": keepalive\n\n"
        finally:
            # 세션 정리
            if session_id in sse_sessions:
                del sse_sessions[session_id]

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        }
    )


@app.post("/api/tryon", response_model=VTONResponse)
async def virtual_tryon(
    humanImage: UploadFile = File(...),
    topImage: Optional[UploadFile] = File(None),
    bottomImage: Optional[UploadFile] = File(None),
    dressImage: Optional[UploadFile] = File(None),
    topDescription: str = Form("A stylish top"),
    bottomDescription: str = Form("Stylish pants"),
    dressDescription: str = Form("A stylish dress"),
    sessionId: Optional[str] = Form(None),
):
    """
    Virtual Try-On API (Replicate IDM-VTON)
    - 상의/하의 개별 또는 동시 착용 지원
    - 원피스 지원 (dresses 카테고리)
    - 둘 다 업로드 시: 하의 먼저 적용 -> 상의 적용
    - SSE를 통한 실시간 진행 상황 업데이트 지원
    """
    try:
        # 이미지 읽기
        human_bytes = await humanImage.read()
        top_bytes = await topImage.read() if topImage else None
        bottom_bytes = await bottomImage.read() if bottomImage else None
        dress_bytes = await dressImage.read() if dressImage else None

        # 최소 하나의 의류 이미지 필요
        if not top_bytes and not bottom_bytes and not dress_bytes:
            return VTONResponse(
                success=False,
                error="상의, 하의 또는 원피스 이미지를 최소 하나 업로드해주세요."
            )

        # 진행 상황 콜백 설정
        def on_progress(info):
            if sessionId and sessionId in sse_sessions:
                asyncio.create_task(
                    sse_sessions[sessionId].put({
                        "status": info.status,
                        "progress": info.progress,
                        "message": info.message,
                        "eta": info.eta,
                        "queuePosition": info.queue_position,
                        "queueSize": info.queue_size,
                    })
                )

        # VTON 서비스 호출
        result = await vton_service.process_tryon_with_both(
            human_image=human_bytes,
            top_image=top_bytes,
            bottom_image=bottom_bytes,
            dress_image=dress_bytes,
            top_description=topDescription,
            bottom_description=bottomDescription,
            dress_description=dressDescription,
            on_progress=on_progress
        )

        return VTONResponse(
            success=result.success,
            outputImage=result.output_image,
            maskedImage=result.masked_image,
            error=result.error,
        )

    except Exception as e:
        return VTONResponse(
            success=False,
            error=str(e)
        )


# ======================
#    Personal Color
# ======================

@app.post("/api/analyze", response_model=AnalysisResponse)
async def analyze_personal_color(
    image: UploadFile = File(...),
):
    """
    이미지를 분석하여 퍼스널 컬러를 진단합니다.
    - Dlib 68 랜드마크 기반 얼굴/눈 검출
    - 피부/머리/눈 색상 특징 추출 (Lab, HSV)
    - RandomForest 머신러닝 모델 기반 4계절 분류 (봄/여름/가을/겨울)
    """
    try:
        contents = await image.read()
        pil_img = Image.open(io.BytesIO(contents)).convert("RGB")
    except Exception:
        raise HTTPException(status_code=400, detail="유효한 이미지 파일이 아닙니다.")

    try:
        cv_img = pil_to_cv2(pil_img)
        result_dict = analyze_image(cv_img)
        return AnalysisResponse(**result_dict)
    except Exception as e:
        error_message = f"분석 실패: {str(e)}"
        if "얼굴을 찾을 수 없습니다" in str(e):
            error_message = "분석 실패: 이미지에서 얼굴을 찾을 수 없습니다. 더 선명하거나 정면을 바라보는 사진을 사용해 보세요."

        return AnalysisResponse(
            season="Unknown",
            confidence=0,
            description=error_message,
            recommended_colors=["#FFFFFF"],
            avoid_colors=["#000000"],
            skin_tone="unknown",
            undertone="unknown",
        )


# ======================
#    Face Shape
# ======================

@app.post("/api/analyze/face-shape", response_model=FaceShapeResponse)
async def analyze_face_shape_endpoint(
    image: UploadFile = File(...),
):
    """
    이미지를 분석하여 얼굴형을 진단합니다.
    - Hugging Face Vision Transformer 모델 (metadome/face_shape_classification)
    - 5가지 얼굴형 분류: Heart(하트형), Oblong(긴형), Oval(계란형), Round(둥근형), Square(사각형)
    - 정확도: 85.3%
    """
    try:
        contents = await image.read()
        pil_img = Image.open(io.BytesIO(contents)).convert("RGB")
    except Exception:
        raise HTTPException(status_code=400, detail="유효한 이미지 파일이 아닙니다.")

    try:
        cv_img = pil_to_cv2(pil_img)
        result_dict = analyze_face_shape(cv_img)
        return FaceShapeResponse(**result_dict)
    except Exception as e:
        error_message = f"분석 실패: {str(e)}"
        if "얼굴을 감지할 수 없습니다" in str(e):
            error_message = "분석 실패: 이미지에서 얼굴을 감지할 수 없습니다. 더 선명하거나 정면을 바라보는 사진을 사용해 보세요."

        return FaceShapeResponse(
            face_shape="Unknown",
            confidence=0,
            description=error_message,
            recommended_hairstyles=["분석 실패"],
            recommended_glasses=["분석 실패"],
            probabilities={
                "둥근형": 20.0,
                "계란형": 20.0,
                "사각형": 20.0,
                "긴형": 20.0,
                "하트형": 20.0,
            },
        )


# ======================
#   Static File Serving
# ======================

if STATIC_DIR.exists():
    # assets 폴더가 있으면 마운트
    assets_dir = STATIC_DIR / "assets"
    if assets_dir.exists():
        app.mount("/assets", StaticFiles(directory=str(assets_dir)), name="assets")

    @app.get("/{full_path:path}")
    async def serve_spa(full_path: str):
        # API 경로는 스킵
        if full_path.startswith("api/"):
            raise HTTPException(status_code=404, detail="API endpoint not found")

        file_path = STATIC_DIR / full_path
        if file_path.is_file():
            return FileResponse(file_path)

        index_path = STATIC_DIR / "index.html"
        if index_path.exists():
            return FileResponse(index_path)

        return {
            "message": "Static files not found. Please build the frontend first."
        }
else:
    @app.get("/")
    async def root():
        return {
            "message": "Closet AI API",
            "status": "running",
            "endpoints": {
                "virtual_tryon": "POST /api/tryon",
                "personal_color": "POST /api/analyze",
                "face_shape": "POST /api/analyze/face-shape",
                "progress": "GET /api/progress/{session_id}",
            },
            "note": "Frontend not built. Run 'npm run build' in the interactive-closet directory.",
        }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
