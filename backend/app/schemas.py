"""
API Request/Response Schemas (Pydantic Models)
"""

from pydantic import BaseModel, ConfigDict


class AnalysisResponse(BaseModel):
    """퍼스널 컬러 분석 결과"""

    season: str
    confidence: float
    description: str
    recommended_colors: list[str]
    avoid_colors: list[str]
    skin_tone: str
    undertone: str
    face_box: list[int] | None = None
    labeled_image: str | None = None


class FaceShapeResponse(BaseModel):
    """얼굴형 분석 결과"""

    face_shape: str
    confidence: float
    description: str
    recommended_hairstyles: list[str]
    recommended_glasses: list[str]
    probabilities: dict[str, float]
    face_box: list[int] | None = None
    labeled_image: str | None = None


class VTONRequest(BaseModel):
    """Virtual Try-On 요청"""

    description: str = "A person wearing the garment"
    auto_mask: bool = True
    auto_crop: bool = True
    denoising_steps: int = 30
    seed: int = 42


class VTONResponse(BaseModel):
    """Virtual Try-On 응답"""
    model_config = ConfigDict(populate_by_name=True)

    success: bool
    outputImage: str | None = None
    maskedImage: str | None = None
    error: str | None = None


class ProgressInfo(BaseModel):
    """진행 상태 정보"""
    model_config = ConfigDict(populate_by_name=True)

    status: str  # connecting, submitting, pending, generating, complete, error
    progress: float
    message: str
    eta: float | None = None
    queuePosition: int | None = None
    queueSize: int | None = None
