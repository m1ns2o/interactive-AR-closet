<script setup lang="ts">
import { ref, computed, shallowRef, onUnmounted, useTemplateRef } from "vue";

const API_BASE_URL = import.meta.env.VITE_API_URL || "";

// Template refs for file inputs
const humanInputRef = useTemplateRef<HTMLInputElement>("humanInput");
const topInputRef = useTemplateRef<HTMLInputElement>("topInput");
const bottomInputRef = useTemplateRef<HTMLInputElement>("bottomInput");
const dressInputRef = useTemplateRef<HTMLInputElement>("dressInput");

// Mode: 'separate' for top/bottom, 'dress' for one-piece
const garmentMode = ref<"separate" | "dress">("separate");

// Form data
const humanImage = ref<File | null>(null);
const topImage = ref<File | null>(null);
const bottomImage = ref<File | null>(null);
const dressImage = ref<File | null>(null);
const garmentDescription = ref("");

// Preview URLs
const humanPreview = ref<string | null>(null);
const topPreview = ref<string | null>(null);
const bottomPreview = ref<string | null>(null);
const dressPreview = ref<string | null>(null);

// Drag states
const humanDragging = ref(false);
const topDragging = ref(false);
const bottomDragging = ref(false);
const dressDragging = ref(false);

// Processing state
const isProcessing = ref(false);
const progress = ref(0);
const progressMessage = ref("");
const elapsedTime = ref(0);
const eta = ref<number | undefined>(undefined);
const queuePosition = ref<number | undefined>(undefined);
const queueSize = ref<number | undefined>(undefined);
const stepProgress = ref<
  { current: number; total: number; unit: string } | undefined
>(undefined);
const processingStatus = ref("");

// Non-reactive references (shallowRef for objects that don't need deep reactivity)
const elapsedTimer = shallowRef<ReturnType<typeof setInterval> | null>(null);
const eventSourceRef = shallowRef<EventSource | null>(null);

// Results
const outputImage = ref<string | null>(null);
const maskedImage = ref<string | null>(null);
const error = ref<string | null>(null);

// Computed
const canSubmit = computed(() => {
  if (!humanImage.value || isProcessing.value) return false;
  if (garmentMode.value === "dress") {
    return !!dressImage.value;
  }
  return !!(topImage.value || bottomImage.value);
});

const hasGarments = computed(() => {
  if (garmentMode.value === "dress") {
    return !!dressImage.value;
  }
  return !!(topImage.value || bottomImage.value);
});

// Cleanup on unmount
onUnmounted(() => {
  stopElapsedTimer();
  closeEventSource();
});

function handleImageUpload(
  file: File,
  type: "human" | "top" | "bottom" | "dress"
) {
  const reader = new FileReader();
  reader.onload = (e) => {
    if (type === "human") {
      humanImage.value = file;
      humanPreview.value = e.target?.result as string;
    } else if (type === "top") {
      topImage.value = file;
      topPreview.value = e.target?.result as string;
    } else if (type === "bottom") {
      bottomImage.value = file;
      bottomPreview.value = e.target?.result as string;
    } else {
      dressImage.value = file;
      dressPreview.value = e.target?.result as string;
    }
  };
  reader.readAsDataURL(file);
}

function handleDrop(e: DragEvent, type: "human" | "top" | "bottom" | "dress") {
  if (type === "human") {
    humanDragging.value = false;
  } else if (type === "top") {
    topDragging.value = false;
  } else if (type === "bottom") {
    bottomDragging.value = false;
  } else {
    dressDragging.value = false;
  }

  const file = e.dataTransfer?.files?.[0];
  if (file && file.type.startsWith("image/")) {
    handleImageUpload(file, type);
  }
}

function handleDragOver(type: "human" | "top" | "bottom" | "dress") {
  if (type === "human") {
    humanDragging.value = true;
  } else if (type === "top") {
    topDragging.value = true;
  } else if (type === "bottom") {
    bottomDragging.value = true;
  } else {
    dressDragging.value = true;
  }
}

function handleDragLeave(type: "human" | "top" | "bottom" | "dress") {
  if (type === "human") {
    humanDragging.value = false;
  } else if (type === "top") {
    topDragging.value = false;
  } else if (type === "bottom") {
    bottomDragging.value = false;
  } else {
    dressDragging.value = false;
  }
}

function triggerFileInput(type: "human" | "top" | "bottom" | "dress") {
  const inputRef =
    type === "human"
      ? humanInputRef
      : type === "top"
      ? topInputRef
      : type === "bottom"
      ? bottomInputRef
      : dressInputRef;
  inputRef.value?.click();
}

function handleFileInputChange(
  e: Event,
  type: "human" | "top" | "bottom" | "dress"
) {
  const target = e.target as HTMLInputElement;
  const file = target.files?.[0];
  if (file) {
    handleImageUpload(file, type);
  }
}

function removeImage(type: "top" | "bottom" | "dress") {
  if (type === "top") {
    topImage.value = null;
    topPreview.value = null;
  } else if (type === "bottom") {
    bottomImage.value = null;
    bottomPreview.value = null;
  } else {
    dressImage.value = null;
    dressPreview.value = null;
  }
}

function startElapsedTimer() {
  const startTime = Date.now();
  elapsedTimer.value = setInterval(() => {
    elapsedTime.value = Math.floor((Date.now() - startTime) / 1000);
  }, 1000);
}

function stopElapsedTimer() {
  if (elapsedTimer.value) {
    clearInterval(elapsedTimer.value);
    elapsedTimer.value = null;
  }
}

function closeEventSource() {
  if (eventSourceRef.value) {
    eventSourceRef.value.close();
    eventSourceRef.value = null;
  }
}

async function handleSubmit() {
  if (!humanImage.value) return;
  if (garmentMode.value === "dress" && !dressImage.value) return;
  if (garmentMode.value === "separate" && !topImage.value && !bottomImage.value)
    return;

  // Reset state
  error.value = null;
  outputImage.value = null;
  maskedImage.value = null;
  isProcessing.value = true;
  progress.value = 0;
  processingStatus.value = "connecting";
  eta.value = undefined;
  queuePosition.value = undefined;
  queueSize.value = undefined;
  stepProgress.value = undefined;
  elapsedTime.value = 0;
  startElapsedTimer();

  const sessionId = `session_${Date.now()}_${Math.random()
    .toString(36)
    .substring(2, 11)}`;

  // Setup SSE for progress updates
  const eventSource = new EventSource(
    `${API_BASE_URL}/api/progress/${sessionId}`
  );
  eventSourceRef.value = eventSource;

  eventSource.onmessage = (event) => {
    const data = JSON.parse(event.data);
    if (data.progress !== undefined) {
      progress.value = data.progress;
    }
    if (data.message) {
      progressMessage.value = data.message;
    }
    if (data.status) {
      processingStatus.value = data.status;
    }
    if (data.eta !== undefined) {
      eta.value = data.eta;
    }
    if (data.queuePosition !== undefined) {
      queuePosition.value = data.queuePosition;
    }
    if (data.queueSize !== undefined) {
      queueSize.value = data.queueSize;
    }
    if (data.stepProgress) {
      stepProgress.value = data.stepProgress;
    }
  };

  eventSource.onerror = () => {
    closeEventSource();
  };

  // Build form data
  const formData = new FormData();
  formData.append("humanImage", humanImage.value);

  if (garmentMode.value === "dress" && dressImage.value) {
    formData.append("dressImage", dressImage.value);
    formData.append(
      "dressDescription",
      garmentDescription.value || "A stylish dress"
    );
  } else {
    if (topImage.value) {
      formData.append("topImage", topImage.value);
      formData.append(
        "topDescription",
        garmentDescription.value || "A stylish garment"
      );
    }

    if (bottomImage.value) {
      formData.append("bottomImage", bottomImage.value);
      formData.append(
        "bottomDescription",
        garmentDescription.value || "A stylish garment"
      );
    }
  }

  formData.append("sessionId", sessionId);

  try {
    const response = await fetch(`${API_BASE_URL}/api/tryon`, {
      method: "POST",
      body: formData,
    });

    closeEventSource();

    const result = await response.json();

    if (result.success) {
      outputImage.value = result.outputImage;
      maskedImage.value = result.maskedImage;
      progress.value = 100;
      progressMessage.value = "완료되었습니다!";
    } else {
      error.value = result.error || "오류가 발생했습니다";
    }
  } catch (err) {
    closeEventSource();
    error.value =
      err instanceof Error ? err.message : "네트워크 오류가 발생했습니다";
  } finally {
    stopElapsedTimer();
    isProcessing.value = false;
  }
}
</script>

<template>
  <div class="max-w-7xl mx-auto">
    <!-- Mode Toggle -->
    <div class="mb-4 flex justify-center">
      <div class="inline-flex rounded-lg border border-gray-200 bg-white p-1">
        <button
          :class="[
            'px-4 py-2 text-sm font-medium rounded-md transition-colors',
            garmentMode === 'separate'
              ? 'bg-primary-500 text-white'
              : 'text-gray-600 hover:text-gray-900',
          ]"
          @click="garmentMode = 'separate'"
        >
          상의 / 하의
        </button>
        <button
          :class="[
            'px-4 py-2 text-sm font-medium rounded-md transition-colors',
            garmentMode === 'dress'
              ? 'bg-primary-500 text-white'
              : 'text-gray-600 hover:text-gray-900',
          ]"
          @click="garmentMode = 'dress'"
        >
          원피스
        </button>
      </div>
    </div>

    <!-- Main Grid: Dynamic width/cols for centering -->
    <div
      class="grid gap-4 items-start grid-cols-1 transition-all duration-300"
      :class="
        garmentMode === 'dress'
          ? 'md:grid-cols-3 md:w-3/4 md:mx-auto'
          : 'md:grid-cols-4 w-full'
      "
    >
      <!-- Human Image Upload -->
      <div
        class="bg-white rounded-lg border border-gray-200 overflow-hidden flex flex-col"
      >
        <div
          class="px-4 py-3 border-b border-gray-200 flex items-center justify-between bg-gray-50/50"
        >
          <div class="flex items-center gap-2">
            <UIcon name="i-lucide-user" class="w-5 h-5 text-primary-500" />
            <h3 class="font-medium">나의 사진</h3>
          </div>
          <UBadge v-if="humanImage" color="green" variant="subtle" size="xs">
            업로드됨
          </UBadge>
        </div>

        <div
          class="relative group cursor-pointer bg-gray-50 hover:bg-gray-100 transition-colors aspect-3/4 flex items-center justify-center"
          @click="triggerFileInput('human')"
          @drop.prevent="(e) => handleDrop(e, 'human')"
          @dragover.prevent="handleDragOver('human')"
          @dragleave.prevent="handleDragLeave('human')"
        >
          <div
            v-if="humanPreview"
            class="absolute inset-0 flex items-center justify-center"
          >
            <img
              :src="humanPreview"
              class="max-w-full max-h-full object-contain"
            />
            <div
              class="absolute inset-0 bg-black/40 opacity-0 group-hover:opacity-100 transition-opacity flex items-center justify-center"
            >
              <UButton color="white" icon="i-lucide-refresh-cw"> 변경 </UButton>
            </div>
          </div>
          <div v-else class="text-center p-6">
            <div
              class="w-14 h-14 rounded-full bg-primary-50 flex items-center justify-center mx-auto mb-3 group-hover:scale-110 transition-transform"
            >
              <UIcon
                name="i-lucide-upload-cloud"
                class="w-7 h-7 text-primary-500"
              />
            </div>
            <p class="font-medium mb-1 text-sm">사진 업로드</p>
            <p class="text-xs text-gray-500">클릭하거나 드래그하세요</p>
          </div>

          <input
            ref="humanInput"
            type="file"
            accept="image/*"
            class="hidden"
            @change="(e) => handleFileInputChange(e, 'human')"
          />
        </div>
      </div>

      <!-- Top (Upper Body) Image Upload -->
      <div
        v-if="garmentMode === 'separate'"
        class="bg-white rounded-lg border border-gray-200 overflow-hidden flex flex-col"
      >
        <div
          class="px-4 py-3 border-b border-gray-200 flex items-center justify-between bg-gray-50/50"
        >
          <div class="flex items-center gap-2">
            <UIcon name="i-lucide-shirt" class="w-5 h-5 text-blue-500" />
            <h3 class="font-medium">상의</h3>
          </div>
          <UBadge v-if="topImage" color="green" variant="subtle" size="xs">
            업로드됨
          </UBadge>
        </div>

        <div
          class="relative group bg-gray-50 hover:bg-gray-100 transition-colors aspect-3/4 flex items-center justify-center"
          :class="{ 'cursor-pointer': !topPreview }"
          @click="!topPreview && triggerFileInput('top')"
          @drop.prevent="(e) => handleDrop(e, 'top')"
          @dragover.prevent="handleDragOver('top')"
          @dragleave.prevent="handleDragLeave('top')"
        >
          <div
            v-if="topPreview"
            class="absolute inset-0 flex items-center justify-center"
          >
            <img
              :src="topPreview"
              class="max-w-full max-h-full object-contain"
            />
            <div
              class="absolute inset-0 bg-black/40 opacity-0 group-hover:opacity-100 transition-opacity flex flex-col items-center justify-center gap-2"
            >
              <UButton
                color="white"
                icon="i-lucide-refresh-cw"
                @click.stop="triggerFileInput('top')"
              >
                변경
              </UButton>
              <UButton
                color="red"
                variant="solid"
                icon="i-lucide-trash-2"
                @click.stop="removeImage('top')"
              >
                제거
              </UButton>
            </div>
          </div>
          <div v-else class="text-center p-6">
            <div
              class="w-14 h-14 rounded-full bg-blue-50 flex items-center justify-center mx-auto mb-3 group-hover:scale-110 transition-transform"
            >
              <UIcon
                name="i-lucide-upload-cloud"
                class="w-7 h-7 text-blue-500"
              />
            </div>
            <p class="font-medium mb-1 text-sm">상의 업로드</p>
            <p class="text-xs text-gray-500">선택 사항</p>
          </div>

          <input
            ref="topInput"
            type="file"
            accept="image/*"
            class="hidden"
            @change="(e) => handleFileInputChange(e, 'top')"
          />
        </div>
      </div>

      <!-- Bottom (Lower Body) Image Upload -->
      <div
        v-if="garmentMode === 'separate'"
        class="bg-white rounded-lg border border-gray-200 overflow-hidden flex flex-col"
      >
        <div
          class="px-4 py-3 border-b border-gray-200 flex items-center justify-between bg-gray-50/50"
        >
          <div class="flex items-center gap-2">
            <UIcon name="i-lucide-footprints" class="w-5 h-5 text-amber-500" />
            <h3 class="font-medium">하의</h3>
          </div>
          <UBadge v-if="bottomImage" color="green" variant="subtle" size="xs">
            업로드됨
          </UBadge>
        </div>

        <div
          class="relative group bg-gray-50 hover:bg-gray-100 transition-colors aspect-3/4 flex items-center justify-center"
          :class="{ 'cursor-pointer': !bottomPreview }"
          @click="!bottomPreview && triggerFileInput('bottom')"
          @drop.prevent="(e) => handleDrop(e, 'bottom')"
          @dragover.prevent="handleDragOver('bottom')"
          @dragleave.prevent="handleDragLeave('bottom')"
        >
          <div
            v-if="bottomPreview"
            class="absolute inset-0 flex items-center justify-center"
          >
            <img
              :src="bottomPreview"
              class="max-w-full max-h-full object-contain"
            />
            <div
              class="absolute inset-0 bg-black/40 opacity-0 group-hover:opacity-100 transition-opacity flex flex-col items-center justify-center gap-2"
            >
              <UButton
                color="white"
                icon="i-lucide-refresh-cw"
                @click.stop="triggerFileInput('bottom')"
              >
                변경
              </UButton>
              <UButton
                color="red"
                variant="solid"
                icon="i-lucide-trash-2"
                @click.stop="removeImage('bottom')"
              >
                제거
              </UButton>
            </div>
          </div>
          <div v-else class="text-center p-6">
            <div
              class="w-14 h-14 rounded-full bg-amber-50 flex items-center justify-center mx-auto mb-3 group-hover:scale-110 transition-transform"
            >
              <UIcon
                name="i-lucide-upload-cloud"
                class="w-7 h-7 text-amber-500"
              />
            </div>
            <p class="font-medium mb-1 text-sm">하의 업로드</p>
            <p class="text-xs text-gray-500">선택 사항</p>
          </div>

          <input
            ref="bottomInput"
            type="file"
            accept="image/*"
            class="hidden"
            @change="(e) => handleFileInputChange(e, 'bottom')"
          />
        </div>
      </div>

      <!-- Dress (One-piece) Image Upload -->
      <div
        v-if="garmentMode === 'dress'"
        class="bg-white rounded-lg border border-gray-200 overflow-hidden flex flex-col"
      >
        <div
          class="px-4 py-3 border-b border-gray-200 flex items-center justify-between bg-gray-50/50"
        >
          <div class="flex items-center gap-2">
            <UIcon name="i-lucide-sparkles" class="w-5 h-5 text-pink-500" />
            <h3 class="font-medium">원피스</h3>
          </div>
          <UBadge v-if="dressImage" color="green" variant="subtle" size="xs">
            업로드됨
          </UBadge>
        </div>

        <div
          class="relative group bg-gray-50 hover:bg-gray-100 transition-colors aspect-3/4 flex items-center justify-center"
          :class="{ 'cursor-pointer': !dressPreview }"
          @click="!dressPreview && triggerFileInput('dress')"
          @drop.prevent="(e) => handleDrop(e, 'dress')"
          @dragover.prevent="handleDragOver('dress')"
          @dragleave.prevent="handleDragLeave('dress')"
        >
          <div
            v-if="dressPreview"
            class="absolute inset-0 flex items-center justify-center"
          >
            <img
              :src="dressPreview"
              class="max-w-full max-h-full object-contain"
            />
            <div
              class="absolute inset-0 bg-black/40 opacity-0 group-hover:opacity-100 transition-opacity flex flex-col items-center justify-center gap-2"
            >
              <UButton
                color="white"
                icon="i-lucide-refresh-cw"
                @click.stop="triggerFileInput('dress')"
              >
                변경
              </UButton>
              <UButton
                color="red"
                variant="solid"
                icon="i-lucide-trash-2"
                @click.stop="removeImage('dress')"
              >
                제거
              </UButton>
            </div>
          </div>
          <div v-else class="text-center p-6">
            <div
              class="w-14 h-14 rounded-full bg-pink-50 flex items-center justify-center mx-auto mb-3 group-hover:scale-110 transition-transform"
            >
              <UIcon
                name="i-lucide-upload-cloud"
                class="w-7 h-7 text-pink-500"
              />
            </div>
            <p class="font-medium mb-1 text-sm">원피스 업로드</p>
            <p class="text-xs text-gray-500">클릭하거나 드래그하세요</p>
          </div>

          <input
            ref="dressInput"
            type="file"
            accept="image/*"
            class="hidden"
            @change="(e) => handleFileInputChange(e, 'dress')"
          />
        </div>
      </div>

      <!-- Result Card -->
      <div
        class="bg-white rounded-lg border border-gray-200 overflow-hidden flex flex-col"
      >
        <div
          class="px-4 py-3 border-b border-gray-200 flex items-center justify-between bg-gray-50/50"
        >
          <div class="flex items-center gap-2">
            <UIcon
              :name="outputImage ? 'i-lucide-check-circle' : 'i-lucide-image'"
              :class="outputImage ? 'text-green-500' : 'text-gray-400'"
              class="w-5 h-5"
            />
            <h3 class="font-medium">결과</h3>
          </div>
          <UBadge v-if="outputImage" color="green" variant="subtle" size="xs">
            완료
          </UBadge>
        </div>

        <div
          class="relative bg-gray-50 aspect-3/4 flex items-center justify-center"
        >
          <!-- Result Image -->
          <template v-if="outputImage">
            <div class="absolute inset-0 flex items-center justify-center">
              <img
                :src="outputImage"
                class="max-w-full max-h-full object-contain"
              />
            </div>
            <div
              class="absolute inset-0 bg-black/40 opacity-0 hover:opacity-100 transition-opacity flex items-center justify-center gap-2"
            >
              <UButton
                color="white"
                icon="i-lucide-download"
                :to="outputImage"
                target="_blank"
              >
                다운로드
              </UButton>
            </div>
          </template>
          <!-- Placeholder when no result -->
          <div v-else class="text-center p-6 text-gray-400">
            <UIcon
              name="i-lucide-image"
              class="w-12 h-12 mx-auto mb-2 opacity-50"
            />
            <p class="text-sm">결과가 여기에 표시됩니다</p>
          </div>
        </div>
      </div>
    </div>

    <!-- Generate Section (always visible) -->
    <div
      class="mt-6 transition-all duration-300"
      :class="garmentMode === 'dress' ? 'md:w-3/4 md:mx-auto' : 'w-full'"
    >
      <div class="bg-white rounded-lg border border-gray-200 p-4">
        <div
          class="flex flex-col md:flex-row md:items-end gap-4"
          :class="{ 'md:justify-end': !outputImage && !hasGarments }"
        >
          <!-- Description Input (단일 입력) -->
          <div v-if="!outputImage && hasGarments" class="flex-1">
            <label class="text-xs text-gray-500 mb-1 block">
              의류 설명 (선택사항)
            </label>
            <UInput
              v-model="garmentDescription"
              placeholder="예: 캐주얼한 스타일의 옷"
              variant="outline"
              class="w-full"
            />
          </div>

          <!-- Generate Button -->
          <div
            :class="{
              'w-full': outputImage,
              'w-full md:w-auto': !outputImage,
            }"
          >
            <UButton
              :class="{
                'md:min-w-64':
                  !outputImage &&
                  ((garmentMode === 'separate' && topImage && bottomImage) ||
                    garmentMode === 'dress'),
                'md:min-w-48':
                  !outputImage &&
                  !(garmentMode === 'separate' && topImage && bottomImage) &&
                  garmentMode !== 'dress',
              }"
              block
              size="lg"
              :disabled="!canSubmit"
              :loading="isProcessing"
              icon="i-lucide-sparkles"
              @click="handleSubmit"
            >
              <template v-if="outputImage">다시 피팅하기</template>
              <template v-else-if="garmentMode === 'dress'"
                >원피스 피팅하기</template
              >
              <template v-else-if="topImage && bottomImage"
                >상의 + 하의 피팅하기</template
              >
              <template v-else>가상 피팅 시작하기</template>
            </UButton>
          </div>
        </div>

        <!-- Progress Section -->
        <div v-if="isProcessing" class="mt-4 space-y-3">
          <div class="flex items-center justify-between text-sm">
            <span class="font-medium text-gray-700">
              {{
                processingStatus === "pending"
                  ? "대기 중..."
                  : processingStatus === "generating"
                  ? "생성 중..."
                  : "처리 중..."
              }}
            </span>
            <span class="text-gray-700 font-mono text-sm font-medium">
              {{ Math.round(progress) }}%
            </span>
          </div>

          <!-- Custom progress bar with actual percentage fill -->
          <div class="w-full h-2 bg-gray-200 rounded-full overflow-hidden">
            <div
              class="h-full bg-primary-500 rounded-full transition-all duration-300 ease-out"
              :style="{ width: `${progress}%` }"
            />
          </div>

          <div
            v-if="stepProgress"
            class="flex items-center justify-center gap-2 text-xs text-gray-600"
          >
            <span>
              단계 {{ stepProgress.current }} / {{ stepProgress.total }}
            </span>
          </div>

          <div
            v-if="queuePosition !== undefined && processingStatus === 'pending'"
            class="text-xs text-amber-600 text-center"
          >
            대기 순서 {{ queuePosition + 1 }}
            <template v-if="queueSize"> / {{ queueSize }}</template>
          </div>

          <p class="text-xs text-center text-gray-500">
            {{ progressMessage }}
          </p>

          <div
            class="flex items-center justify-center gap-3 text-xs text-gray-400"
          >
            <span>{{ elapsedTime }}초 경과</span>
            <span v-if="eta !== undefined && eta > 0">
              ~{{ Math.max(0, Math.ceil(eta)) }}초 남음
            </span>
          </div>
        </div>

        <!-- Helper text when not processing -->
        <p
          v-if="!isProcessing && !outputImage"
          class="text-xs text-gray-500 text-center mt-2"
        >
          <template v-if="garmentMode === 'dress'">
            원피스 모드입니다. 처리는 약 60-90초 정도 소요됩니다
          </template>
          <template v-else-if="topImage && bottomImage">
            상의와 하의를 모두 선택하셨습니다. 하의 적용 후 상의가 적용됩니다.
            (약 2분 소요)
          </template>
          <template v-else> 처리는 약 60-90초 정도 소요됩니다 </template>
        </p>
      </div>
    </div>

    <!-- Error Alert -->
    <UAlert
      v-if="error"
      color="red"
      variant="subtle"
      icon="i-lucide-alert-circle"
      :title="error"
      class="mt-6"
    />
  </div>
</template>
