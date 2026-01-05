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
            <UIcon name="i-lucide-camera" class="w-8 h-8" />
          </div>
          <h1 class="text-3xl font-bold text-purple-900">진단환경 준비</h1>
        </div>

        <div class="prose prose-purple max-w-none text-gray-700 space-y-6">
          <!-- 1. 촬영 자세 -->
          <div class="space-y-4">
            <div class="flex gap-4 items-start">
              <div
                class="w-10 h-10 rounded-full bg-white border-2 border-purple-200 flex items-center justify-center shrink-0 font-bold text-purple-600"
              >
                1
              </div>
              <div class="flex-1">
                <h3 class="font-bold text-gray-900 mb-2">
                  정면에서 촬영을 하고 눈동자가 잘 보일 수 있게 해주세요.
                </h3>
                <ul class="text-sm text-gray-600 space-y-1 mb-4">
                  <li>• 눈과 렌즈가 같은 높이</li>
                  <li>• 정면 + 수평 촬영</li>
                  <li>• 촬영 각도가 위나 아래로 가지 않게 해주세요.</li>
                </ul>

                <!-- 촬영 가이드 이미지 -->
                <div
                  class="bg-white rounded-2xl p-4 border border-purple-100 shadow-sm"
                >
                  <img
                    src="/photo-guide.png"
                    alt="촬영 가이드 - 정면 수평 촬영 O, 아래에서 찍기 X"
                    class="w-full max-w-md mx-auto rounded-lg"
                  />
                  <p class="text-xs text-center text-gray-500 mt-2">
                    1)번 관련 사진
                  </p>
                </div>
              </div>
            </div>

            <!-- 2. 자연광 환경 -->
            <div class="flex gap-4 items-start">
              <div
                class="w-10 h-10 rounded-full bg-white border-2 border-purple-200 flex items-center justify-center shrink-0 font-bold text-purple-600"
              >
                2
              </div>
              <div>
                <h3 class="font-bold text-gray-900 mb-2">
                  얼굴이 그림자가 지지 않고 밝은 자연광 환경이 가장 좋아요.
                </h3>
                <ul class="text-sm text-gray-600 space-y-1">
                  <li class="flex items-start gap-2">
                    <span class="text-yellow-500">☀️</span>
                    <span
                      >야외 촬영 시 오전 9~11시, 오후 3~5시 사이가 가장
                      좋습니다.</span
                    >
                  </li>
                  <li class="flex items-start gap-2">
                    <span class="text-orange-500">🏠</span>
                    <span>실내 촬영 시 오전 11시~ 오후 3시 사이가 좋습니다.</span>
                  </li>
                  <li class="flex items-start gap-2">
                    <span class="text-blue-500">🪟</span>
                    <span
                      >창문 옆에서 찍을 때는 얼굴 정면이 창문을 향하도록 하고,
                      창문과 50cm정도 떨어진 거리에서 촬영을 합니다.</span
                    >
                  </li>
                  <li class="flex items-start gap-2">
                    <span class="text-gray-400">🌧️</span>
                    <span>흐린날은 피해주세요.</span>
                  </li>
                  <li class="flex items-start gap-2">
                    <span class="text-red-400">⚠️</span>
                    <span>얼굴에 그림자가 생기면 안됩니다.</span>
                  </li>
                </ul>
              </div>
            </div>

            <!-- 3. 민낯 -->
            <div class="flex gap-4 items-start">
              <div
                class="w-10 h-10 rounded-full bg-white border-2 border-purple-200 flex items-center justify-center shrink-0 font-bold text-purple-600"
              >
                3
              </div>
              <div>
                <h3 class="font-bold text-gray-900 mb-2">
                  선크림이나 화장을 하지 않은 상태가 가장 좋습니다.
                </h3>
                <p class="text-sm text-gray-600">
                  메이크업을 하지 않은 본연의 피부톤이 필요합니다. 컬러 렌즈나
                  색이 있는 안경도 피해 주세요.
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
