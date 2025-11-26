<script setup lang="ts">
import { ref, computed } from "vue";

const API_BASE_URL = import.meta.env.VITE_API_URL || "http://localhost:3000";

// Form data
const humanImage = ref<File | null>(null);
const garmentImage = ref<File | null>(null);
const description = ref("");

// Preview URLs
const humanPreview = ref<string | null>(null);
const garmentPreview = ref<string | null>(null);

// Drag states
const humanDragging = ref(false);
const garmentDragging = ref(false);

// Processing state
const isProcessing = ref(false);
const progress = ref(0);
const progressMessage = ref("");
const elapsedTime = ref(0);
let elapsedTimer: ReturnType<typeof setInterval> | null = null;
let eventSource: EventSource | null = null;

// Results
const outputImage = ref<string | null>(null);
const maskedImage = ref<string | null>(null);
const error = ref<string | null>(null);

const canSubmit = computed(
  () => humanImage.value && garmentImage.value && !isProcessing.value
);

function handleImageUpload(file: File, type: "human" | "garment") {
  const reader = new FileReader();
  reader.onload = (e) => {
    if (type === "human") {
      humanImage.value = file;
      humanPreview.value = e.target?.result as string;
    } else {
      garmentImage.value = file;
      garmentPreview.value = e.target?.result as string;
    }
  };
  reader.readAsDataURL(file);
}

function handleDrop(e: DragEvent, type: "human" | "garment") {
  e.preventDefault();
  if (type === "human") {
    humanDragging.value = false;
  } else {
    garmentDragging.value = false;
  }

  const file = e.dataTransfer?.files?.[0];
  if (file && file.type.startsWith("image/")) {
    handleImageUpload(file, type);
  }
}

function handleDragOver(e: DragEvent, type: "human" | "garment") {
  e.preventDefault();
  if (type === "human") {
    humanDragging.value = true;
  } else {
    garmentDragging.value = true;
  }
}

function handleDragLeave(type: "human" | "garment") {
  if (type === "human") {
    humanDragging.value = false;
  } else {
    garmentDragging.value = false;
  }
}

function triggerFileInput(type: "human" | "garment") {
  const input = document.getElementById(`${type}-input`);
  if (input) {
    (input as HTMLInputElement).click();
  }
}

function handleFileInputChange(e: Event, type: "human" | "garment") {
  const target = e.target as HTMLInputElement;
  const file = target.files?.[0];
  if (file) {
    handleImageUpload(file, type);
  }
}

function startElapsedTimer() {
  const startTime = Date.now();
  elapsedTimer = setInterval(() => {
    elapsedTime.value = Math.floor((Date.now() - startTime) / 1000);
  }, 1000);
}

function stopElapsedTimer() {
  if (elapsedTimer) {
    clearInterval(elapsedTimer);
    elapsedTimer = null;
  }
}

async function handleSubmit() {
  if (!humanImage.value || !garmentImage.value) return;

  error.value = null;
  outputImage.value = null;
  maskedImage.value = null;
  isProcessing.value = true;
  progress.value = 0;
  progressMessage.value = "Initializing...";
  elapsedTime.value = 0;
  startElapsedTimer();

  const sessionId = `session_${Date.now()}_${Math.random()
    .toString(36)
    .substring(2, 11)}`;

  // Setup SSE for progress
  eventSource = new EventSource(`${API_BASE_URL}/api/progress/${sessionId}`);
  eventSource.onmessage = (event) => {
    const data = JSON.parse(event.data);
    if (data.progress !== undefined) {
      progress.value = data.progress;
      progressMessage.value = data.message || "Processing...";
    }
  };

  const formData = new FormData();
  formData.append("humanImage", humanImage.value);
  formData.append("garmentImage", garmentImage.value);
  formData.append(
    "description",
    description.value || "A person wearing the garment"
  );
  formData.append("sessionId", sessionId);

  try {
    const response = await fetch(`${API_BASE_URL}/api/tryon`, {
      method: "POST",
      body: formData,
    });

    if (eventSource) {
      eventSource.close();
      eventSource = null;
    }

    const result = await response.json();

    if (result.success) {
      outputImage.value = result.outputImage;
      maskedImage.value = result.maskedImage;
      progress.value = 100;
      progressMessage.value = "Complete!";
    } else {
      error.value = result.error || "An error occurred";
    }
  } catch (err) {
    if (eventSource) {
      eventSource.close();
      eventSource = null;
    }
    error.value = err instanceof Error ? err.message : "Network error occurred";
  } finally {
    stopElapsedTimer();
    isProcessing.value = false;
  }
}

function reset() {
  humanImage.value = null;
  garmentImage.value = null;
  humanPreview.value = null;
  garmentPreview.value = null;
  outputImage.value = null;
  maskedImage.value = null;
  error.value = null;
  progress.value = 0;
  description.value = "";
}
</script>

<template>
  <div class="max-w-5xl mx-auto">
    <!-- Header Section -->
    <div class="mb-8">
      <h2 class="text-2xl font-bold text-gray-900 mb-2">New Try-On Session</h2>
      <p class="text-gray-500">
        Upload your photo and a garment to see how it looks.
      </p>
    </div>

    <div class="grid grid-cols-1 lg:grid-cols-12 gap-8">
      <!-- Left Column: Inputs -->
      <div class="lg:col-span-7 space-y-6">
        <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
          <!-- Human Image Upload -->
          <div
            class="bg-white rounded-lg border border-gray-200 overflow-hidden flex flex-col h-full"
          >
            <div
              class="px-4 py-3 border-b border-gray-200 flex items-center justify-between bg-gray-50/50"
            >
              <div class="flex items-center gap-2">
                <UIcon name="i-lucide-user" class="w-5 h-5 text-primary-500" />
                <h3 class="font-medium text-gray-900">Your Photo</h3>
              </div>
              <UBadge v-if="humanImage" color="green" variant="subtle" size="xs"
                >Uploaded</UBadge
              >
            </div>

            <div
              class="relative group cursor-pointer bg-gray-50 hover:bg-gray-100 transition-colors flex-1 flex items-center justify-center aspect-[3/4]"
              @click="triggerFileInput('human')"
              @drop.prevent="(e) => handleDrop(e, 'human')"
              @dragover.prevent="(e) => handleDragOver(e, 'human')"
              @dragleave.prevent="() => handleDragLeave('human')"
            >
              <div v-if="humanPreview" class="relative w-full h-full">
                <img :src="humanPreview" class="w-full h-full object-cover" />
                <div
                  class="absolute inset-0 bg-black/40 opacity-0 group-hover:opacity-100 transition-opacity flex items-center justify-center"
                >
                  <UButton color="white" icon="i-lucide-refresh-cw"
                    >Change Photo</UButton
                  >
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
                <p class="font-medium text-gray-900 mb-1 text-sm">
                  Upload Photo
                </p>
                <p class="text-xs text-gray-500">Click or drop</p>
              </div>

              <input
                id="human-input"
                type="file"
                accept="image/*"
                class="hidden"
                @change="(e) => handleFileInputChange(e, 'human')"
              />
            </div>
          </div>

          <!-- Garment Image Upload -->
          <div
            class="bg-white rounded-lg border border-gray-200 overflow-hidden flex flex-col h-full"
          >
            <div
              class="px-4 py-3 border-b border-gray-200 flex items-center justify-between bg-gray-50/50"
            >
              <div class="flex items-center gap-2">
                <UIcon name="i-lucide-shirt" class="w-5 h-5 text-primary-500" />
                <h3 class="font-medium text-gray-900">Garment</h3>
              </div>
              <UBadge
                v-if="garmentImage"
                color="green"
                variant="subtle"
                size="xs"
                >Uploaded</UBadge
              >
            </div>

            <div
              class="relative group cursor-pointer bg-gray-50 hover:bg-gray-100 transition-colors flex-1 flex items-center justify-center aspect-[3/4]"
              @click="triggerFileInput('garment')"
              @drop.prevent="(e) => handleDrop(e, 'garment')"
              @dragover.prevent="(e) => handleDragOver(e, 'garment')"
              @dragleave.prevent="() => handleDragLeave('garment')"
            >
              <div v-if="garmentPreview" class="relative w-full h-full">
                <img :src="garmentPreview" class="w-full h-full object-cover" />
                <div
                  class="absolute inset-0 bg-black/40 opacity-0 group-hover:opacity-100 transition-opacity flex items-center justify-center"
                >
                  <UButton color="white" icon="i-lucide-refresh-cw"
                    >Change Photo</UButton
                  >
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
                <p class="font-medium text-gray-900 mb-1 text-sm">
                  Upload Garment
                </p>
                <p class="text-xs text-gray-500">Click or drop</p>
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

        <!-- Description -->
        <div class="bg-white rounded-lg border border-gray-200 overflow-hidden">
          <div
            class="px-4 py-3 border-b border-gray-200 flex items-center gap-2 bg-gray-50/50"
          >
            <UIcon name="i-lucide-text" class="w-5 h-5 text-primary-500" />
            <h3 class="font-medium text-gray-900">Description (Optional)</h3>
          </div>
          <div class="p-4">
            <UTextarea
              v-model="description"
              placeholder="e.g., A person wearing a white t-shirt"
              :rows="3"
              variant="none"
              :ui="{ wrapper: 'w-full', base: 'p-0 focus:ring-0 border-0' }"
            />
          </div>
        </div>
      </div>

      <!-- Right Column: Actions & Results -->
      <div class="lg:col-span-5 space-y-6">
        <!-- Action Card -->
        <UCard>
          <div class="text-center py-4">
            <UButton
              block
              size="xl"
              :disabled="!canSubmit"
              :loading="isProcessing"
              @click="handleSubmit"
              icon="i-lucide-sparkles"
              class="mb-4"
            >
              Generate Try-On
            </UButton>

            <p
              class="text-xs text-gray-500 flex items-center justify-center gap-1"
            >
              <UIcon name="i-lucide-clock" class="w-3 h-3" />
              Estimated processing time: 60-90 seconds
            </p>
          </div>
        </UCard>

        <!-- Progress -->
        <UCard v-if="isProcessing">
          <div class="space-y-4">
            <div class="flex items-center justify-between text-sm">
              <span class="font-medium text-gray-700">Processing...</span>
              <span class="text-gray-500">{{ Math.round(progress) }}%</span>
            </div>
            <UProgress :value="progress" color="primary" />
            <p class="text-xs text-center text-gray-500">
              {{ progressMessage }}
            </p>
            <p class="text-xs text-center text-gray-400">
              Elapsed: {{ elapsedTime }}s
            </p>
          </div>
        </UCard>

        <!-- Error -->
        <UAlert
          v-if="error"
          color="red"
          variant="subtle"
          icon="i-lucide-alert-circle"
          :title="error"
        />

        <!-- Results -->
        <div v-if="outputImage" class="space-y-6">
          <div
            class="bg-white rounded-lg border border-gray-200 overflow-hidden"
          >
            <div
              class="px-4 py-3 border-b border-gray-200 flex items-center gap-2"
            >
              <UIcon
                name="i-lucide-check-circle"
                class="w-5 h-5 text-green-500"
              />
              <h3 class="font-medium text-gray-900">Final Result</h3>
            </div>
            <div class="relative group">
              <img :src="outputImage" class="w-full h-auto" />
              <div
                class="absolute inset-0 bg-black/40 opacity-0 group-hover:opacity-100 transition-opacity flex items-center justify-center gap-2"
              >
                <UButton
                  color="white"
                  icon="i-lucide-download"
                  :to="outputImage"
                  target="_blank"
                  >Download</UButton
                >
                <UButton color="white" icon="i-lucide-maximize"
                  >View Full</UButton
                >
              </div>
            </div>
          </div>

          <div
            class="bg-white rounded-lg border border-gray-200 overflow-hidden"
          >
            <div
              class="px-4 py-3 border-b border-gray-200 flex items-center gap-2"
            >
              <UIcon name="i-lucide-layers" class="w-5 h-5 text-gray-500" />
              <h3 class="font-medium text-gray-900">Mask Preview</h3>
            </div>
            <img
              :src="maskedImage || undefined"
              class="w-full h-auto opacity-80"
            />
          </div>

          <UButton
            block
            color="gray"
            variant="ghost"
            icon="i-lucide-refresh-cw"
            @click="reset"
          >
            Start New Session
          </UButton>
        </div>
      </div>
    </div>
  </div>
</template>
