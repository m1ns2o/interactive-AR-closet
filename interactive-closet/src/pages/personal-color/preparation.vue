<template>
  <div
    class="h-full flex flex-col justify-center items-center p-6 bg-white overflow-y-auto"
  >
    <div class="max-w-3xl w-full flex flex-col items-center">
      <!-- Card Content -->
      <div
        class="bg-purple-50 rounded-3xl p-8 border-2 border-purple-100 w-full mb-8"
      >
        <div class="flex items-center gap-4 mb-6">
          <div class="p-3 bg-purple-100 rounded-2xl text-purple-600">
            <UIcon name="i-lucide-sun" class="w-8 h-8" />
          </div>
          <h1 class="text-3xl font-bold text-purple-900">진단 준비 사항</h1>
        </div>

        <div class="prose prose-purple max-w-none text-gray-700 space-y-6">
          <p class="text-lg leading-relaxed font-medium">
            정확한 퍼스널 컬러 진단을 위해 아래 환경을 준비해주시면 분석
            정확도가 크게 향상됩니다.
          </p>

          <div class="space-y-4">
            <div class="flex gap-4 items-start">
              <div
                class="w-10 h-10 rounded-full bg-white border-2 border-purple-200 flex items-center justify-center shrink-0 font-bold text-purple-600"
              >
                1
              </div>
              <div>
                <h3 class="font-bold text-gray-900 mb-1">자연광 조명</h3>
                <p class="text-sm text-gray-600">
                  직사광선을 피한 밝은 자연광 아래가 가장 좋습니다. 실내라면
                  백색 조명 아래에서 촬영해주세요. (노란 조명 X)
                </p>
              </div>
            </div>

            <div class="flex gap-4 items-start">
              <div
                class="w-10 h-10 rounded-full bg-white border-2 border-purple-200 flex items-center justify-center shrink-0 font-bold text-purple-600"
              >
                2
              </div>
              <div>
                <h3 class="font-bold text-gray-900 mb-1">민낯 (쌩얼)</h3>
                <p class="text-sm text-gray-600">
                  메이크업을 하지 않은 본연의 피부톤이 필요합니다. 컬러 렌즈나
                  색이 있는 안경도 피해 주세요.
                </p>
              </div>
            </div>

            <div class="flex gap-4 items-start">
              <div
                class="w-10 h-10 rounded-full bg-white border-2 border-purple-200 flex items-center justify-center shrink-0 font-bold text-purple-600"
              >
                3
              </div>
              <div>
                <h3 class="font-bold text-gray-900 mb-1">심플한 배경</h3>
                <p class="text-sm text-gray-600">
                  흰색이나 회색 등 무채색 배경이 좋습니다. 배경색이 피부톤에
                  영향을 주지 않도록 해주세요.
                </p>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Button Below Card -->
      <UButton
        to="/personal-color"
        icon="i-lucide-arrow-left"
        size="xl"
        color="purple"
        class="shadow-lg rounded-full px-8 py-3 font-bold"
      >
        뒤로가기
      </UButton>
    </div>
  </div>
</template>
