"""
Virtual Try-On Service
Replicate API를 사용하여 가상 의류 착용을 수행합니다.
"""

import asyncio
import os
import logging
import base64
import tempfile
from typing import Callable, Optional
from dataclasses import dataclass

import replicate

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class ProgressInfo:
    """진행 상태 정보"""
    status: str  # connecting, submitting, pending, generating, complete, error
    progress: float
    message: str
    eta: Optional[float] = None
    queue_position: Optional[int] = None
    queue_size: Optional[int] = None


@dataclass
class VTONRequest:
    """Virtual Try-On 요청"""
    human_image: bytes
    garment_image: bytes
    description: str = "A stylish garment"
    category: str = "upper_body"  # upper_body, lower_body, dresses
    seed: int = 42


@dataclass
class VTONResponse:
    """Virtual Try-On 응답"""
    success: bool
    output_image: Optional[str] = None
    masked_image: Optional[str] = None
    error: Optional[str] = None


ProgressCallback = Callable[[ProgressInfo], None]


class VTONService:
    """Virtual Try-On 서비스 (Replicate API)"""

    def __init__(self):
        self.model_id = "cuuupid/idm-vton:0513734a452173b8173e907e3a59d19a36266e55b48528559432bd21c7d7e985"
        self.estimated_processing_time = 60  # seconds

    async def process_tryon(
        self,
        request: VTONRequest,
        on_progress: Optional[ProgressCallback] = None
    ) -> VTONResponse:
        """Virtual Try-On 처리"""

        def send_progress(
            status: str,
            progress: float,
            message: str,
            eta: Optional[float] = None,
            queue_position: Optional[int] = None,
            queue_size: Optional[int] = None
        ):
            if on_progress:
                on_progress(ProgressInfo(
                    status=status,
                    progress=progress,
                    message=message,
                    eta=eta,
                    queue_position=queue_position,
                    queue_size=queue_size
                ))

        try:
            # Replicate API 토큰 확인
            replicate_token = os.environ.get("REPLICATE_API_TOKEN")
            if not replicate_token:
                raise ValueError("REPLICATE_API_TOKEN 환경 변수가 설정되지 않았습니다.")

            logger.info("Starting Replicate VTON request...")
            send_progress("connecting", 5, "Replicate API에 연결 중...")

            # 임시 파일로 이미지 저장
            with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as human_file:
                human_file.write(request.human_image)
                human_path = human_file.name

            with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as garment_file:
                garment_file.write(request.garment_image)
                garment_path = garment_file.name

            send_progress("submitting", 10, "요청 제출 중...")

            # 진행 상황 업데이트를 위한 백그라운드 태스크
            import time
            processing_start_time = time.time()
            progress_task_running = True

            async def update_progress():
                while progress_task_running:
                    elapsed = time.time() - processing_start_time
                    estimated_total = self.estimated_processing_time

                    # 15% ~ 95% 진행률 계산 (easing 적용)
                    raw_progress = elapsed / estimated_total
                    eased_progress = 1 - (1 - min(raw_progress, 1)) ** 2
                    progress_percent = 15 + eased_progress * 80

                    remaining_time = max(0, int(estimated_total - elapsed))

                    send_progress(
                        "generating",
                        min(95, progress_percent),
                        f"AI가 이미지를 생성 중입니다... (~{remaining_time}초 남음)",
                        eta=remaining_time
                    )
                    await asyncio.sleep(0.5)

            # 백그라운드에서 진행률 업데이트 시작
            progress_task = asyncio.create_task(update_progress())

            try:
                # Replicate API 호출
                loop = asyncio.get_event_loop()

                def run_replicate():
                    with open(human_path, "rb") as hf, open(garment_path, "rb") as gf:
                        output = replicate.run(
                            self.model_id,
                            input={
                                "human_img": hf,
                                "garm_img": gf,
                                "garment_des": request.description,
                                "category": request.category,
                            }
                        )
                        return output

                result = await loop.run_in_executor(None, run_replicate)

            finally:
                # 진행률 업데이트 중지
                progress_task_running = False
                progress_task.cancel()
                try:
                    await progress_task
                except asyncio.CancelledError:
                    pass

                # 임시 파일 정리
                try:
                    os.unlink(human_path)
                    os.unlink(garment_path)
                except:
                    pass

            send_progress("complete", 100, "완료!")

            logger.info(f"Replicate response: {result}")

            # 결과 처리
            if result:
                # Replicate는 FileOutput 객체를 반환
                output_url = str(result) if hasattr(result, '__str__') else result.url if hasattr(result, 'url') else None

                if output_url:
                    # URL에서 이미지 다운로드하여 base64로 변환
                    import requests
                    response = requests.get(output_url)
                    if response.status_code == 200:
                        image_data = response.content
                        output_image_base64 = f"data:image/png;base64,{base64.b64encode(image_data).decode('utf-8')}"

                        return VTONResponse(
                            success=True,
                            output_image=output_image_base64,
                            masked_image=None
                        )

            return VTONResponse(
                success=False,
                error="Replicate API에서 유효한 응답을 받지 못했습니다."
            )

        except Exception as e:
            logger.error(f"Error processing virtual try-on: {e}")
            send_progress("error", 0, str(e))
            return VTONResponse(
                success=False,
                error=str(e)
            )

    async def process_tryon_with_both(
        self,
        human_image: bytes,
        top_image: Optional[bytes],
        bottom_image: Optional[bytes],
        dress_image: Optional[bytes] = None,
        top_description: str = "A stylish top",
        bottom_description: str = "Stylish pants",
        dress_description: str = "A stylish dress",
        on_progress: Optional[ProgressCallback] = None
    ) -> VTONResponse:
        """
        상의, 하의, 원피스를 처리하는 Virtual Try-On
        - 원피스가 있으면: 원피스만 단독 적용 (category="dresses")
        - 상의/하의 둘 다 있으면: 하의 먼저 적용 -> 그 결과에 상의 적용
        - 하나만 있으면: 해당 의류만 적용
        """

        def send_progress(
            status: str,
            progress: float,
            message: str,
            eta: Optional[float] = None
        ):
            if on_progress:
                on_progress(ProgressInfo(
                    status=status,
                    progress=progress,
                    message=message,
                    eta=eta
                ))

        try:
            current_human_image = human_image

            # 원피스가 있는 경우 (단독 처리)
            if dress_image:
                send_progress("generating", 10, "원피스를 적용 중...")
                result = await self.process_tryon(
                    VTONRequest(
                        human_image=current_human_image,
                        garment_image=dress_image,
                        description=dress_description,
                        category="dresses"
                    ),
                    on_progress
                )
                return result

            # 상의만 있는 경우
            if top_image and not bottom_image:
                send_progress("generating", 10, "상의를 적용 중...")
                result = await self.process_tryon(
                    VTONRequest(
                        human_image=current_human_image,
                        garment_image=top_image,
                        description=top_description,
                        category="upper_body"
                    ),
                    on_progress
                )
                return result

            # 하의만 있는 경우
            if bottom_image and not top_image:
                send_progress("generating", 10, "하의를 적용 중...")
                result = await self.process_tryon(
                    VTONRequest(
                        human_image=current_human_image,
                        garment_image=bottom_image,
                        description=bottom_description,
                        category="lower_body"
                    ),
                    on_progress
                )
                return result

            # 둘 다 있는 경우: 하의 먼저 -> 상의
            if top_image and bottom_image:
                # 1단계: 하의 적용
                send_progress("generating", 10, "1/2 단계: 하의를 적용 중...")
                bottom_result = await self.process_tryon(
                    VTONRequest(
                        human_image=current_human_image,
                        garment_image=bottom_image,
                        description=bottom_description,
                        category="lower_body"
                    )
                )

                if not bottom_result.success or not bottom_result.output_image:
                    return VTONResponse(
                        success=False,
                        error=f"하의 적용 실패: {bottom_result.error}"
                    )

                # 하의 적용 결과를 다음 단계의 입력으로 사용
                # base64 디코딩
                bottom_image_data = bottom_result.output_image
                if bottom_image_data.startswith("data:"):
                    bottom_image_data = bottom_image_data.split(",")[1]
                current_human_image = base64.b64decode(bottom_image_data)

                # 2단계: 상의 적용
                send_progress("generating", 55, "2/2 단계: 상의를 적용 중...")
                top_result = await self.process_tryon(
                    VTONRequest(
                        human_image=current_human_image,
                        garment_image=top_image,
                        description=top_description,
                        category="upper_body"
                    )
                )

                return top_result

            # 아무것도 없는 경우
            return VTONResponse(
                success=False,
                error="상의 또는 하의 이미지를 업로드해주세요."
            )

        except Exception as e:
            logger.error(f"Error in process_tryon_with_both: {e}")
            return VTONResponse(
                success=False,
                error=str(e)
            )
