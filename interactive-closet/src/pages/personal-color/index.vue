<template>
  <div class="h-full flex flex-col justify-center items-center p-6 bg-white">
    <div class="max-w-4xl w-full">
      <div class="flex items-center justify-center gap-2 mb-8">
        <UIcon name="i-lucide-info" class="w-8 h-8 text-primary-500" />
        <h1 class="text-3xl font-bold text-gray-900">퍼스널 컬러 가이드</h1>
      </div>

      <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-12">
        <!-- Item 1: Definition -->
        <button
          class="group p-6 rounded-2xl bg-purple-50 border-2 border-purple-100 hover:border-purple-300 hover:shadow-lg hover:-translate-y-1 transition-all duration-300 text-left"
          @click="router.push('/personal-color/definition')"
        >
          <div class="flex flex-col h-full justify-between">
            <div>
              <div class="flex items-center gap-3 mb-4">
                <div
                  class="p-2 bg-purple-100 rounded-xl text-purple-600 group-hover:scale-110 transition-transform"
                >
                  <UIcon name="i-lucide-help-circle" class="w-6 h-6" />
                </div>
                <h3 class="font-bold text-xl text-purple-900">퍼스널컬러란?</h3>
              </div>
              <p class="text-sm text-purple-800 leading-relaxed font-medium">
                나에게 가장 잘 어울리는 색은 무엇일까요?
              </p>
            </div>
            <div
              class="flex items-center text-sm font-bold text-purple-600 group-hover:translate-x-2 transition-transform mt-4"
            >
              자세히 보기
              <UIcon name="i-lucide-arrow-right" class="w-4 h-4 ml-2" />
            </div>
          </div>
        </button>

        <!-- Item 2: Importance -->
        <button
          class="group p-6 rounded-2xl bg-purple-50 border-2 border-purple-100 hover:border-purple-300 hover:shadow-lg hover:-translate-y-1 transition-all duration-300 text-left"
          @click="router.push('/personal-color/importance')"
        >
          <div class="flex flex-col h-full justify-between">
            <div>
              <div class="flex items-center gap-3 mb-4">
                <div
                  class="p-2 bg-purple-100 rounded-xl text-purple-600 group-hover:scale-110 transition-transform"
                >
                  <UIcon name="i-lucide-sparkles" class="w-6 h-6" />
                </div>
                <h3 class="font-bold text-xl text-purple-900">중요성</h3>
              </div>
              <p class="text-sm text-purple-800 leading-relaxed font-medium">
                왜 퍼스널 컬러를 알아야 할까요?
              </p>
            </div>
            <div
              class="flex items-center text-sm font-bold text-purple-600 group-hover:translate-x-2 transition-transform mt-4"
            >
              자세히 보기
              <UIcon name="i-lucide-arrow-right" class="w-4 h-4 ml-2" />
            </div>
          </div>
        </button>

        <!-- Item 3: Preparation -->
        <button
          class="group p-6 rounded-2xl bg-purple-50 border-2 border-purple-100 hover:border-purple-300 hover:shadow-lg hover:-translate-y-1 transition-all duration-300 text-left"
          @click="router.push('/personal-color/preparation')"
        >
          <div class="flex flex-col h-full justify-between">
            <div>
              <div class="flex items-center gap-3 mb-4">
                <div
                  class="p-2 bg-purple-100 rounded-xl text-purple-600 group-hover:scale-110 transition-transform"
                >
                  <UIcon name="i-lucide-sun" class="w-6 h-6" />
                </div>
                <h3 class="font-bold text-xl text-purple-900">준비 사항</h3>
              </div>
              <p class="text-sm text-purple-800 leading-relaxed font-medium">
                진단 전 준비해야 할 체크리스트
              </p>
            </div>
            <div
              class="flex items-center text-sm font-bold text-purple-600 group-hover:translate-x-2 transition-transform mt-4"
            >
              자세히 보기
              <UIcon name="i-lucide-arrow-right" class="w-4 h-4 ml-2" />
            </div>
          </div>
        </button>

        <!-- Item 4: Start Analysis -->
        <button
          class="group p-6 rounded-2xl bg-purple-600 border-2 border-purple-600 hover:bg-purple-700 hover:border-purple-700 hover:shadow-lg hover:-translate-y-1 transition-all duration-300 text-left cursor-pointer"
          @click="startAnalysis"
        >
          <div class="flex flex-col h-full justify-between">
            <div>
              <div class="flex items-center gap-3 mb-4">
                <div
                  class="p-2 bg-purple-500 rounded-xl text-white group-hover:scale-110 transition-transform"
                >
                  <UIcon name="i-lucide-play-circle" class="w-6 h-6" />
                </div>
                <h3 class="font-bold text-xl text-white">진단 시작하기</h3>
              </div>
              <p class="text-sm text-purple-100 leading-relaxed font-medium">
                준비가 되셨다면 바로 시작해보세요.
              </p>
            </div>
            <div
              class="flex items-center text-sm font-bold text-white group-hover:translate-x-2 transition-transform mt-4"
            >
              START <UIcon name="i-lucide-arrow-right" class="w-4 h-4 ml-2" />
            </div>
          </div>
        </button>
      </div>

      <div class="text-center">
        <p class="text-gray-500 text-sm">
          각 항목을 눌러 상세 내용을 확인해보세요.
        </p>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { useRouter } from "vue-router";

const router = useRouter();

function startAnalysis() {
  router.push("/personal-color/analyze");
}
</script>
