<script setup lang="ts">
import { ref, computed } from 'vue'

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:3000'

// Form data
const humanImage = ref<File | null>(null)
const garmentImage = ref<File | null>(null)
const description = ref('')

// Preview URLs
const humanPreview = ref<string | null>(null)
const garmentPreview = ref<string | null>(null)

// Drag states
const humanDragging = ref(false)
const garmentDragging = ref(false)

// Processing state
const isProcessing = ref(false)
const progress = ref(0)
const progressMessage = ref('')
const elapsedTime = ref(0)
let elapsedTimer: ReturnType<typeof setInterval> | null = null
let eventSource: EventSource | null = null

// Results
const outputImage = ref<string | null>(null)
const maskedImage = ref<string | null>(null)
const error = ref<string | null>(null)

const canSubmit = computed(() => humanImage.value && garmentImage.value && !isProcessing.value)

function handleImageUpload(file: File, type: 'human' | 'garment') {
  const reader = new FileReader()
  reader.onload = (e) => {
    if (type === 'human') {
      humanImage.value = file
      humanPreview.value = e.target?.result as string
    } else {
      garmentImage.value = file
      garmentPreview.value = e.target?.result as string
    }
  }
  reader.readAsDataURL(file)
}

function handleDrop(e: DragEvent, type: 'human' | 'garment') {
  e.preventDefault()
  if (type === 'human') {
    humanDragging.value = false
  } else {
    garmentDragging.value = false
  }

  const file = e.dataTransfer?.files?.[0]
  if (file && file.type.startsWith('image/')) {
    handleImageUpload(file, type)
  }
}

function handleDragOver(e: DragEvent, type: 'human' | 'garment') {
  e.preventDefault()
  if (type === 'human') {
    humanDragging.value = true
  } else {
    garmentDragging.value = true
  }
}

function handleDragLeave(type: 'human' | 'garment') {
  if (type === 'human') {
    humanDragging.value = false
  } else {
    garmentDragging.value = false
  }
}

function triggerFileInput(type: 'human' | 'garment') {
  const input = document.getElementById(`${type}-input`)
  if (input) {
    (input as HTMLInputElement).click()
  }
}

function handleFileInputChange(e: Event, type: 'human' | 'garment') {
  const target = e.target as HTMLInputElement
  const file = target.files?.[0]
  if (file) {
    handleImageUpload(file, type)
  }
}

function startElapsedTimer() {
  const startTime = Date.now()
  elapsedTimer = setInterval(() => {
    elapsedTime.value = Math.floor((Date.now() - startTime) / 1000)
  }, 1000)
}

function stopElapsedTimer() {
  if (elapsedTimer) {
    clearInterval(elapsedTimer)
    elapsedTimer = null
  }
}

async function handleSubmit() {
  if (!humanImage.value || !garmentImage.value) return

  error.value = null
  outputImage.value = null
  maskedImage.value = null
  isProcessing.value = true
  progress.value = 0
  progressMessage.value = 'Initializing...'
  elapsedTime.value = 0
  startElapsedTimer()

  const sessionId = `session_${Date.now()}_${Math.random().toString(36).substring(2, 11)}`

  // Setup SSE for progress
  eventSource = new EventSource(`${API_BASE_URL}/api/progress/${sessionId}`)
  eventSource.onmessage = (event) => {
    const data = JSON.parse(event.data)
    if (data.progress !== undefined) {
      progress.value = data.progress
      progressMessage.value = data.message || 'Processing...'
    }
  }

  const formData = new FormData()
  formData.append('humanImage', humanImage.value)
  formData.append('garmentImage', garmentImage.value)
  formData.append('description', description.value || 'A person wearing the garment')
  formData.append('sessionId', sessionId)

  try {
    const response = await fetch(`${API_BASE_URL}/api/tryon`, {
      method: 'POST',
      body: formData,
    })

    if (eventSource) {
      eventSource.close()
      eventSource = null
    }

    const result = await response.json()

    if (result.success) {
      outputImage.value = result.outputImage
      maskedImage.value = result.maskedImage
      progress.value = 100
      progressMessage.value = 'Complete!'
    } else {
      error.value = result.error || 'An error occurred'
    }
  } catch (err) {
    if (eventSource) {
      eventSource.close()
      eventSource = null
    }
    error.value = err instanceof Error ? err.message : 'Network error occurred'
  } finally {
    stopElapsedTimer()
    isProcessing.value = false
  }
}

function reset() {
  humanImage.value = null
  garmentImage.value = null
  humanPreview.value = null
  garmentPreview.value = null
  outputImage.value = null
  maskedImage.value = null
  error.value = null
  progress.value = 0
  description.value = ''
}
</script>

<template>
  <div class="min-h-screen bg-white">
    <div class="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <!-- Header -->
      <div class="text-center mb-10">
        <h1 class="text-4xl sm:text-5xl font-bold mb-3 text-[#4a90e2]">
          InteractiveARcloset
        </h1>
        <p class="text-lg text-gray-600 mb-3">
          AI 기반 가상 피팅 시스템
        </p>
        <div class="inline-block px-4 py-1.5 rounded-full bg-[#4a90e2]/10 text-[#4a90e2] text-sm font-medium">
          ⏱️ AI 처리 시간: 약 60-90초
        </div>
      </div>

    <!-- Upload Section -->
    <div class="mb-8">
      <h2 class="text-2xl font-semibold mb-6 text-gray-800">
        1. 이미지 업로드
      </h2>

      <div class="grid grid-cols-1 md:grid-cols-2 gap-6 max-w-3xl mx-auto">
        <!-- Human Image Upload -->
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-3">
            인물 사진 <span class="text-red-500">*</span>
          </label>

          <!-- Desktop: Drag & Drop Area -->
          <div
            class="hidden sm:block"
            @drop="(e) => handleDrop(e, 'human')"
            @dragover="(e) => handleDragOver(e, 'human')"
            @dragleave="() => handleDragLeave('human')"
            @click="() => triggerFileInput('human')"
          >
            <div
              :class="[
                'relative aspect-square rounded-xl border-2 border-dashed transition-all cursor-pointer overflow-hidden group bg-white',
                humanDragging ? 'border-[#4a90e2] bg-[#4a90e2]/10 scale-[1.02]' : 'border-gray-300 hover:border-[#4a90e2] hover:bg-[#4a90e2]/5',
                humanPreview ? 'border-solid border-[#4a90e2]' : ''
              ]"
            >
              <div v-if="humanPreview" class="w-full h-full relative bg-white">
                <img :src="humanPreview" alt="Human preview" class="w-full h-full object-cover object-center" />
                <div class="absolute inset-0 bg-black/0 group-hover:bg-black/20 transition-all flex items-center justify-center">
                  <UIcon name="i-lucide-refresh-cw" class="w-8 h-8 text-white opacity-0 group-hover:opacity-100 transition-opacity" />
                </div>
              </div>
              <div v-else class="flex flex-col items-center justify-center h-full p-6 bg-white">
                <UIcon name="i-lucide-user" class="w-12 h-12 text-gray-400 mb-3" />
                <p class="text-sm font-medium text-gray-600 mb-1">클릭하거나 드래그하여 업로드</p>
                <p class="text-xs text-gray-500">PNG, JPG (최대 10MB)</p>
              </div>
            </div>
          </div>

          <!-- Mobile: Simple File Input -->
          <div class="block sm:hidden">
            <div
              @click="() => triggerFileInput('human')"
              :class="[
                'relative aspect-square rounded-xl border-2 transition-all cursor-pointer overflow-hidden bg-white',
                humanPreview ? 'border-[#4a90e2] border-solid' : 'border-gray-300 border-dashed active:bg-[#4a90e2]/10'
              ]"
            >
              <div v-if="humanPreview" class="w-full h-full bg-white">
                <img :src="humanPreview" alt="Human preview" class="w-full h-full object-cover object-center" />
              </div>
              <div v-else class="flex flex-col items-center justify-center h-full p-6 bg-white">
                <UIcon name="i-lucide-user" class="w-12 h-12 text-gray-400 mb-3" />
                <p class="text-sm font-medium text-gray-600 mb-1">탭하여 사진 선택</p>
                <p class="text-xs text-gray-500">PNG, JPG</p>
              </div>
            </div>
          </div>

          <input
            id="human-input"
            type="file"
            accept="image/*"
            class="hidden"
            @change="(e) => handleFileInputChange(e, 'human')"
          />
        </div>

        <!-- Garment Image Upload -->
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-3">
            의류 사진 <span class="text-red-500">*</span>
          </label>

          <!-- Desktop: Drag & Drop Area -->
          <div
            class="hidden sm:block"
            @drop="(e) => handleDrop(e, 'garment')"
            @dragover="(e) => handleDragOver(e, 'garment')"
            @dragleave="() => handleDragLeave('garment')"
            @click="() => triggerFileInput('garment')"
          >
            <div
              :class="[
                'relative aspect-square rounded-xl border-2 border-dashed transition-all cursor-pointer overflow-hidden group bg-white',
                garmentDragging ? 'border-[#4a90e2] bg-[#4a90e2]/10 scale-[1.02]' : 'border-gray-300 hover:border-[#4a90e2] hover:bg-[#4a90e2]/5',
                garmentPreview ? 'border-solid border-[#4a90e2]' : ''
              ]"
            >
              <div v-if="garmentPreview" class="w-full h-full relative bg-white">
                <img :src="garmentPreview" alt="Garment preview" class="w-full h-full object-cover object-center" />
                <div class="absolute inset-0 bg-black/0 group-hover:bg-black/20 transition-all flex items-center justify-center">
                  <UIcon name="i-lucide-refresh-cw" class="w-8 h-8 text-white opacity-0 group-hover:opacity-100 transition-opacity" />
                </div>
              </div>
              <div v-else class="flex flex-col items-center justify-center h-full p-6 bg-white">
                <UIcon name="i-lucide-shirt" class="w-12 h-12 text-gray-400 mb-3" />
                <p class="text-sm font-medium text-gray-600 mb-1">클릭하거나 드래그하여 업로드</p>
                <p class="text-xs text-gray-500">PNG, JPG (최대 10MB)</p>
              </div>
            </div>
          </div>

          <!-- Mobile: Simple File Input -->
          <div class="block sm:hidden">
            <div
              @click="() => triggerFileInput('garment')"
              :class="[
                'relative aspect-square rounded-xl border-2 transition-all cursor-pointer overflow-hidden bg-white',
                garmentPreview ? 'border-[#4a90e2] border-solid' : 'border-gray-300 border-dashed active:bg-[#4a90e2]/10'
              ]"
            >
              <div v-if="garmentPreview" class="w-full h-full bg-white">
                <img :src="garmentPreview" alt="Garment preview" class="w-full h-full object-cover object-center" />
              </div>
              <div v-else class="flex flex-col items-center justify-center h-full p-6 bg-white">
                <UIcon name="i-lucide-shirt" class="w-12 h-12 text-gray-400 mb-3" />
                <p class="text-sm font-medium text-gray-600 mb-1">탭하여 사진 선택</p>
                <p class="text-xs text-gray-500">PNG, JPG</p>
              </div>
            </div>
          </div>

          <input
            id="garment-input"
            type="file"
            accept="image/*"
            class="hidden"
            @change="(e) => handleFileInputChange(e, 'garment')"
          />
        </div>
      </div>
    </div>

    <!-- Description Section -->
    <div class="mb-8">
      <h2 class="text-2xl font-semibold mb-4 text-gray-800">
        2. 설명 입력 <span class="text-sm text-gray-500 font-normal">(선택사항)</span>
      </h2>

      <UTextarea
        v-model="description"
        placeholder='예: "화이트 셔츠를 입은 사람", "청바지를 입은 모델" 등'
        :rows="2"
        size="lg"
        class="w-full"
      />
      <p class="text-sm text-gray-500 mt-2">
        입력하지 않으면 기본값이 사용됩니다
      </p>
    </div>

    <!-- Submit Button -->
    <div class="mb-8 text-center">
      <UButton
        size="xl"
        :disabled="!canSubmit"
        :loading="isProcessing"
        @click="handleSubmit"
        icon="i-lucide-sparkles"
        class="px-12"
      >
        AI 피팅 시작
      </UButton>
      <UButton
        v-if="outputImage"
        size="xl"
        color="neutral"
        variant="ghost"
        class="ml-4"
        icon="i-lucide-refresh-cw"
        @click="reset"
      >
        새로 시작
      </UButton>
    </div>

    <!-- Progress Section -->
    <div v-if="isProcessing" class="mb-8">
      <div class="bg-white rounded-xl border border-gray-200 p-6 shadow-sm">
        <div class="text-center">
          <UProgress :value="progress" class="mb-4" />
          <p class="text-lg font-medium text-gray-800 mb-2">
            {{ Math.round(progress) }}% - {{ progressMessage }}
          </p>
          <p class="text-sm text-gray-600">
            경과 시간: {{ elapsedTime }}초
          </p>
        </div>
      </div>
    </div>

    <!-- Error -->
    <UAlert
      v-if="error"
      color="red"
      variant="subtle"
      icon="i-lucide-alert-circle"
      :title="error"
      class="mb-8"
    />

    <!-- Results Section -->
    <div v-if="outputImage && maskedImage" class="mb-8">
      <h2 class="text-2xl font-semibold mb-6 text-gray-800">
        결과
      </h2>

      <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div class="bg-white rounded-xl border border-gray-200 p-4 shadow-sm">
          <h3 class="text-lg font-medium mb-4 text-gray-700">
            최종 결과
          </h3>
          <div class="rounded-lg overflow-hidden border border-gray-200">
            <img :src="outputImage" alt="Output" class="w-full h-auto" />
          </div>
        </div>

        <div class="bg-white rounded-xl border border-gray-200 p-4 shadow-sm">
          <h3 class="text-lg font-medium mb-4 text-gray-700">
            마스크 이미지
          </h3>
          <div class="rounded-lg overflow-hidden border border-gray-200">
            <img :src="maskedImage" alt="Masked" class="w-full h-auto" />
          </div>
        </div>
      </div>
    </div>
    </div>
  </div>
</template>
