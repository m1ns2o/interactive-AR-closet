"""
Virtual Try-On Service
Gradio API를 사용하여 가상 의류 착용을 수행합니다.
"""

import asyncio
import os
import time
import logging
from typing import Callable, Optional
from dataclasses import dataclass
from gradio_client import Client, handle_file
import tempfile
import base64

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
    description: str = "A person wearing the garment"
    auto_mask: bool = True
    auto_crop: bool = True
    denoising_steps: int = 30
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
    """Virtual Try-On 서비스"""

    def __init__(self):
        self.space_id = "m1ns2o/IDM-VTON"
        self.api_name = "/tryon"
        self.estimated_processing_time = 30  # seconds

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
            logger.info(f"Connecting to Gradio space: {self.space_id}")
            send_progress("connecting", 5, "Connecting to Gradio space...")

            # HF Token 확인
            hf_token = os.environ.get("HF_TOKEN")
            if hf_token:
                logger.info("Using Hugging Face authentication token")
            else:
                logger.info("No HF token found, connecting without authentication")

            # Gradio Client 연결
            client = Client(self.space_id, hf_token=hf_token)

            # 임시 파일로 이미지 저장
            with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as human_file:
                human_file.write(request.human_image)
                human_path = human_file.name

            with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as garment_file:
                garment_file.write(request.garment_image)
                garment_path = garment_file.name

            logger.info("Sending request to Gradio API...")
            send_progress("submitting", 10, "Submitting request to server...")

            # 진행 상황 업데이트를 위한 백그라운드 태스크
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
                        f"Generating... (~{remaining_time}s remaining)",
                        eta=remaining_time
                    )
                    await asyncio.sleep(0.5)

            # 백그라운드에서 진행률 업데이트 시작
            progress_task = asyncio.create_task(update_progress())

            try:
                # Gradio API 호출 (블로킹 호출을 스레드풀에서 실행)
                loop = asyncio.get_event_loop()
                result = await loop.run_in_executor(
                    None,
                    lambda: client.predict(
                        dict={
                            "background": handle_file(human_path),
                            "layers": [],
                            "composite": None
                        },
                        garm_img=handle_file(garment_path),
                        garment_des=request.description,
                        is_checked=request.auto_mask,
                        is_checked_crop=request.auto_crop,
                        denoise_steps=request.denoising_steps,
                        seed=request.seed,
                        api_name=self.api_name
                    )
                )
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

            send_progress("complete", 100, "Done!")

            logger.info("Received response from Gradio API")
            logger.info(f"Response data: {result}")

            # 결과 처리
            if result and len(result) >= 2:
                output_image = result[0] if isinstance(result[0], str) else None
                masked_image = result[1] if isinstance(result[1], str) else None

                logger.info(f"Output image path: {output_image}")
                logger.info(f"Masked image path: {masked_image}")

                return VTONResponse(
                    success=True,
                    output_image=output_image,
                    masked_image=masked_image
                )
            else:
                return VTONResponse(
                    success=False,
                    error="Invalid response from Gradio API"
                )

        except Exception as e:
            logger.error(f"Error processing virtual try-on: {e}")
            send_progress("error", 0, str(e))
            return VTONResponse(
                success=False,
                error=str(e)
            )
