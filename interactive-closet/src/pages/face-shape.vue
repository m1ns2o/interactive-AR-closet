<template>
	<div class="face-shape-analyzer">
		<header class="header">
			<h1>얼굴형 진단</h1>
			<p>사진을 업로드하여 나의 얼굴형을 확인하고 스타일 추천을 받아보세요</p>
		</header>

		<main class="main-content">
			<!-- 이미지 업로드 영역 -->
			<div class="upload-section">
				<div v-if="!previewImage" class="upload-options">
					<button
						class="upload-option-btn"
						:class="{ 'drag-over': isDragging }"
						@click="triggerFileInput"
						@drop.prevent="handleDrop"
						@dragover.prevent="isDragging = true"
						@dragleave.prevent="isDragging = false"
					>
						<UIcon name="i-lucide-upload" class="w-12 h-12" />
						<span>갤러리에서 선택</span>
						<span class="drag-hint">또는 드래그하여 업로드</span>
					</button>
					<button class="upload-option-btn" @click="openCamera">
						<UIcon name="i-lucide-camera" class="w-12 h-12" />
						<span>카메라로 촬영</span>
					</button>
				</div>

				<div v-if="showCamera" class="camera-container">
					<video
						ref="videoElement"
						autoplay
						playsinline
						class="camera-preview"
					></video>
					<div class="camera-controls">
						<button class="camera-btn capture-btn" @click="capturePhoto">
							<div class="capture-circle"></div>
						</button>
						<UButton color="neutral" variant="ghost" @click="closeCamera">
							취소
						</UButton>
					</div>
				</div>

				<div v-if="previewImage" class="preview-container">
					<img :src="previewImage" alt="Preview" class="preview-image" />
					<button class="remove-image" @click="removeImage">
						<UIcon name="i-lucide-x" class="w-4 h-4" />
					</button>
				</div>

				<input
					ref="fileInput"
					type="file"
					accept="image/*"
					@change="handleFileSelect"
					style="display: none"
				/>
				<UButton
					block
					size="lg"
					:disabled="!selectedFile || isAnalyzing"
					:loading="isAnalyzing"
					@click="analyzeFaceShape"
				>
					{{ isAnalyzing ? "분석 중..." : "얼굴형 진단하기" }}
				</UButton>
			</div>

			<!-- 분석 결과 영역 -->
			<div v-if="analysisResult" class="result-section">
				<div class="result-header">
					<h2>진단 결과</h2>
					<UBadge color="primary" size="lg">
						{{ analysisResult.face_shape }}
					</UBadge>
				</div>

				<div class="result-content">
					<div class="confidence-meter">
						<label>신뢰도</label>
						<div class="meter">
							<div
								class="meter-fill"
								:style="{ width: analysisResult.confidence + '%' }"
							></div>
						</div>
						<span>{{ analysisResult.confidence }}%</span>
					</div>

					<div class="description">
						<h3>얼굴형 설명</h3>
						<p>{{ analysisResult.description }}</p>
					</div>

					<!-- 레이더 차트 -->
					<div class="chart-section">
						<h3>얼굴형 확률 분포</h3>
						<div class="chart-container">
							<v-chart :option="chartOption" autoresize />
						</div>
					</div>

					<!-- 추천 헤어스타일 -->
					<div class="recommendations">
						<h3>추천 헤어스타일</h3>
						<ul class="recommendation-list">
							<li
								v-for="(style, index) in analysisResult.recommended_hairstyles"
								:key="'hair-' + index"
							>
								<UIcon name="i-lucide-scissors" class="w-4 h-4" />
								{{ style }}
							</li>
						</ul>
					</div>

					<!-- 추천 안경테 -->
					<div class="recommendations">
						<h3>추천 안경테</h3>
						<ul class="recommendation-list">
							<li
								v-for="(glasses, index) in analysisResult.recommended_glasses"
								:key="'glasses-' + index"
							>
								<UIcon name="i-lucide-glasses" class="w-4 h-4" />
								{{ glasses }}
							</li>
						</ul>
					</div>
				</div>
			</div>

			<!-- 에러 메시지 -->
			<UAlert
				v-if="errorMessage"
				color="error"
				icon="i-lucide-alert-circle"
				:title="errorMessage"
			/>
		</main>
	</div>
</template>

<script setup lang="ts">
import { ref, computed } from "vue";
import VChart from "vue-echarts";
import { use } from "echarts/core";
import { CanvasRenderer } from "echarts/renderers";
import { RadarChart } from "echarts/charts";
import {
	TitleComponent,
	TooltipComponent,
	LegendComponent,
} from "echarts/components";

// ECharts 컴포넌트 등록
use([
	CanvasRenderer,
	RadarChart,
	TitleComponent,
	TooltipComponent,
	LegendComponent,
]);

interface FaceShapeResult {
	face_shape: string;
	confidence: number;
	description: string;
	recommended_hairstyles: string[];
	recommended_glasses: string[];
	probabilities: Record<string, number>;
	face_box?: [number, number, number, number];
	labeled_image?: string;
}

// 얼굴형 타입 고정 순서 (레이더 차트 축 일관성 유지)
const FACE_SHAPE_ORDER = ["긴형", "하트형", "사각형", "둥근형", "계란형"];

const API_URL = import.meta.env.PROD ? "" : "http://localhost:8000";

const fileInput = ref<HTMLInputElement | null>(null);
const videoElement = ref<HTMLVideoElement | null>(null);
const selectedFile = ref<File | null>(null);
const previewImage = ref<string | null>(null);
const isDragging = ref(false);
const isAnalyzing = ref(false);
const showCamera = ref(false);
const mediaStream = ref<MediaStream | null>(null);
const analysisResult = ref<FaceShapeResult | null>(null);
const errorMessage = ref<string | null>(null);

// ECharts 레이더 차트 옵션 - violet 테마 적용
const chartOption = computed(() => {
	if (!analysisResult.value) return {};

	const probabilities = analysisResult.value.probabilities;
	const labels = FACE_SHAPE_ORDER;
	const values = FACE_SHAPE_ORDER.map((shape) => probabilities[shape] || 0);

	return {
		tooltip: {
			trigger: "item",
			formatter: (params: any) => {
				return `${params.name}: ${params.value}%`;
			},
		},
		radar: {
			indicator: labels.map((label) => ({
				name: label,
				max: 100,
			})),
			shape: "polygon",
			splitNumber: 5,
			axisName: {
				color: "#333",
				fontSize: 14,
			},
			splitLine: {
				lineStyle: {
					color: ["#e5e7eb", "#e5e7eb", "#e5e7eb", "#e5e7eb", "#e5e7eb"],
				},
			},
			splitArea: {
				show: true,
				areaStyle: {
					color: ["rgba(139, 92, 246, 0.05)", "rgba(139, 92, 246, 0.1)"],
				},
			},
		},
		series: [
			{
				name: "얼굴형 확률",
				type: "radar",
				data: [
					{
						value: values,
						name: "확률 분포",
						areaStyle: {
							color: "rgba(139, 92, 246, 0.3)",
						},
						lineStyle: {
							color: "rgba(139, 92, 246, 1)",
							width: 2,
						},
						itemStyle: {
							color: "rgba(139, 92, 246, 1)",
						},
					},
				],
			},
		],
	};
});

const triggerFileInput = () => {
	fileInput.value?.click();
};

const handleFileSelect = (event: Event) => {
	const target = event.target as HTMLInputElement;
	const file = target.files?.[0];
	if (file) {
		processFile(file);
	}
};

const handleDrop = (event: DragEvent) => {
	isDragging.value = false;
	const file = event.dataTransfer?.files[0];
	if (file && file.type.startsWith("image/")) {
		processFile(file);
	}
};

const processFile = (file: File) => {
	if (file.size > 10 * 1024 * 1024) {
		errorMessage.value = "파일 크기는 10MB 이하여야 합니다.";
		return;
	}

	selectedFile.value = file;
	errorMessage.value = null;
	analysisResult.value = null;

	const reader = new FileReader();
	reader.onload = (e) => {
		previewImage.value = e.target?.result as string;
	};
	reader.readAsDataURL(file);
};

const removeImage = () => {
	selectedFile.value = null;
	previewImage.value = null;
	analysisResult.value = null;
	if (fileInput.value) {
		fileInput.value.value = "";
	}
};

const openCamera = async () => {
	try {
		showCamera.value = true;
		errorMessage.value = null;

		const stream = await navigator.mediaDevices.getUserMedia({
			video: { facingMode: "user" },
		});

		mediaStream.value = stream;

		if (videoElement.value) {
			videoElement.value.srcObject = stream;
		}
	} catch (error) {
		errorMessage.value = "카메라에 접근할 수 없습니다. 권한을 확인해주세요.";
		showCamera.value = false;
		console.error("Camera error:", error);
	}
};

const closeCamera = () => {
	if (mediaStream.value) {
		mediaStream.value.getTracks().forEach((track) => track.stop());
		mediaStream.value = null;
	}
	showCamera.value = false;
};

const capturePhoto = () => {
	if (!videoElement.value) return;

	const canvas = document.createElement("canvas");
	canvas.width = videoElement.value.videoWidth;
	canvas.height = videoElement.value.videoHeight;

	const context = canvas.getContext("2d");
	if (!context) return;

	context.translate(canvas.width, 0);
	context.scale(-1, 1);
	context.drawImage(videoElement.value, 0, 0);

	canvas.toBlob(
		(blob) => {
			if (!blob) return;

			const file = new File([blob], "camera-photo.jpg", { type: "image/jpeg" });
			processFile(file);
			closeCamera();
		},
		"image/jpeg",
		0.9
	);
};

const analyzeFaceShape = async () => {
	console.log("analyzeFaceShape called");
	if (!selectedFile.value) {
		console.log("No file selected");
		return;
	}

	isAnalyzing.value = true;
	errorMessage.value = null;

	try {
		const formData = new FormData();
		formData.append("image", selectedFile.value);

		const response = await fetch(`${API_URL}/api/analyze/face-shape`, {
			method: "POST",
			body: formData,
		});

		if (!response.ok) {
			throw new Error("분석 요청에 실패했습니다.");
		}

		const result = await response.json();
		console.log("Analysis Result:", result);
		analysisResult.value = result;
		if (result.labeled_image) {
			console.log("Labeled image found, updating preview.");
			previewImage.value = result.labeled_image;
		} else {
			console.warn("No labeled_image in result");
		}
	} catch (error) {
		errorMessage.value =
			error instanceof Error ? error.message : "분석 중 오류가 발생했습니다.";
		console.error("Analysis error:", error);
	} finally {
		isAnalyzing.value = false;
	}
};
</script>

<style scoped>
.face-shape-analyzer {
	max-width: 1200px;
	margin: 0 auto;
}

.header {
	text-align: center;
	margin-bottom: 2rem;
}

.header h1 {
	font-size: 2rem;
	margin-bottom: 0.5rem;
	color: var(--ui-text);
}

.header p {
	color: var(--ui-text-muted);
	font-size: 1rem;
}

.main-content {
	display: grid;
	gap: 1.5rem;
}

.upload-section {
	background: var(--ui-bg);
	border: 1px solid var(--ui-border);
	border-radius: 12px;
	padding: 1.5rem;
}

.upload-options {
	display: grid;
	grid-template-columns: 1fr 1fr;
	gap: 1rem;
	margin-bottom: 1.5rem;
}

.upload-option-btn {
	display: flex;
	flex-direction: column;
	align-items: center;
	gap: 0.75rem;
	padding: 2rem 1rem;
	background: var(--ui-bg);
	border: 2px dashed var(--ui-border);
	border-radius: 12px;
	cursor: pointer;
	transition: all 0.3s ease;
	color: var(--ui-text);
	font-size: 1rem;
	font-weight: 500;
}

.upload-option-btn:hover {
	border-color: var(--ui-primary);
	background: var(--ui-bg-elevated);
}

.upload-option-btn .w-12 {
	color: var(--ui-primary);
}

.upload-option-btn.drag-over {
	border-color: var(--ui-primary);
	background: var(--ui-bg-elevated);
}

.drag-hint {
	font-size: 0.85rem;
	color: var(--ui-text-muted);
	font-weight: 400;
}

.camera-container {
	position: relative;
	margin-bottom: 1.5rem;
	border-radius: 12px;
	overflow: hidden;
	background: #000000;
}

.camera-preview {
	width: 100%;
	max-height: 500px;
	object-fit: contain;
	display: block;
	transform: scaleX(-1);
}

.camera-controls {
	position: absolute;
	bottom: 0;
	left: 0;
	right: 0;
	display: flex;
	justify-content: center;
	align-items: center;
	gap: 1rem;
	padding: 1.5rem;
	background: linear-gradient(to top, rgba(0, 0, 0, 0.7), transparent);
}

.capture-btn {
	width: 70px;
	height: 70px;
	background: white;
	border: none;
	border-radius: 50%;
	cursor: pointer;
	display: flex;
	align-items: center;
	justify-content: center;
	transition: transform 0.2s;
}

.capture-btn:hover {
	transform: scale(1.1);
}

.capture-circle {
	width: 50px;
	height: 50px;
	background: var(--ui-primary);
	border-radius: 50%;
}

.preview-container {
	position: relative;
	max-width: 500px;
	margin: 0 auto 1.5rem;
}

.preview-image {
	width: 100%;
	border-radius: 8px;
	box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
}

.remove-image {
	position: absolute;
	top: 10px;
	right: 10px;
	background: rgba(0, 0, 0, 0.7);
	color: white;
	border: none;
	border-radius: 50%;
	width: 32px;
	height: 32px;
	cursor: pointer;
	display: flex;
	align-items: center;
	justify-content: center;
	transition: background 0.2s;
}

.remove-image:hover {
	background: rgba(0, 0, 0, 0.9);
}

.result-section {
	background: var(--ui-bg);
	border: 1px solid var(--ui-border);
	border-radius: 12px;
	padding: 1.5rem;
}

.result-header {
	display: flex;
	justify-content: space-between;
	align-items: center;
	margin-bottom: 1.5rem;
	padding-bottom: 1rem;
	border-bottom: 1px solid var(--ui-border);
}

.result-header h2 {
	font-size: 1.5rem;
	color: var(--ui-text);
}

.confidence-meter {
	margin-bottom: 1.5rem;
}

.confidence-meter label {
	display: block;
	margin-bottom: 0.5rem;
	font-weight: 600;
	color: var(--ui-text);
}

.meter {
	height: 20px;
	background: var(--ui-bg-elevated);
	border-radius: 10px;
	overflow: hidden;
	margin-bottom: 0.5rem;
}

.meter-fill {
	height: 100%;
	background: var(--ui-primary);
	transition: width 0.5s ease;
	border-radius: 10px;
}

.description {
	margin-bottom: 1.5rem;
}

.description h3 {
	margin-bottom: 0.75rem;
	color: var(--ui-text);
}

.description p {
	line-height: 1.6;
	color: var(--ui-text-muted);
}

.chart-section {
	margin-bottom: 1.5rem;
	padding: 1.5rem;
	background: var(--ui-bg-elevated);
	border-radius: 12px;
}

.chart-section h3 {
	margin-bottom: 1rem;
	color: var(--ui-text);
	text-align: center;
}

.chart-container {
	max-width: 500px;
	height: 350px;
	margin: 0 auto;
}

.recommendations {
	margin-bottom: 1.5rem;
}

.recommendations:last-child {
	margin-bottom: 0;
}

.recommendations h3 {
	margin-bottom: 0.75rem;
	color: var(--ui-text);
}

.recommendation-list {
	list-style: none;
	padding: 0;
	margin: 0;
	display: grid;
	gap: 0.5rem;
}

.recommendation-list li {
	display: flex;
	align-items: center;
	gap: 0.75rem;
	padding: 0.875rem 1rem;
	background: var(--ui-bg-elevated);
	border-left: 3px solid var(--ui-primary);
	border-radius: 8px;
	color: var(--ui-text);
	transition: all 0.2s;
}

.recommendation-list li:hover {
	background: var(--ui-bg-accented);
	transform: translateX(4px);
}

.recommendation-list li .w-4 {
	color: var(--ui-primary);
	flex-shrink: 0;
}

/* 반응형 */
@media (max-width: 768px) {
	.header h1 {
		font-size: 1.5rem;
	}

	.upload-options {
		grid-template-columns: 1fr;
	}

	.upload-option-btn:hover {
		border-color: var(--ui-border);
		background: var(--ui-bg);
	}

	.result-header {
		flex-direction: column;
		gap: 1rem;
		align-items: flex-start;
	}

	.chart-container {
		height: 300px;
	}

	.recommendation-list li:hover {
		background: var(--ui-bg-elevated);
		transform: none;
	}
}
</style>
