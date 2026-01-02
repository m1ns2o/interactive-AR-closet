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
            <UIcon name="i-lucide-sparkles" class="w-8 h-8" />
          </div>
          <h1 class="text-3xl font-bold text-purple-900">
            퍼스널컬러의 중요성
          </h1>
        </div>

        <div class="prose prose-purple max-w-none text-gray-700 space-y-6">
          <p class="text-lg leading-relaxed font-medium">
            자신에게 어울리는 색을 찾으면 피부 톤이 정돈되어 보이고, 인상이 더욱
            또렷해보이는 긍정적인 효과를 얻을 수 있습니다.
          </p>

          <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <div
              class="bg-white p-5 rounded-2xl border border-purple-100 shadow-sm"
            >
              <div
                class="flex items-center gap-2 mb-2 text-green-600 font-bold"
              >
                <UIcon name="i-lucide-check-circle" class="w-5 h-5" />
                <span>Best Color 효과</span>
              </div>
              <ul class="text-sm space-y-2 text-gray-600">
                <li>• 피부가 화사하고 투명해 보임</li>
                <li>• 다크서클이나 잡티가 옅어 보임</li>
                <li>• 이목구비가 또렷하고 생기 있어 보임</li>
              </ul>
            </div>

            <div
              class="bg-white p-5 rounded-2xl border border-purple-100 shadow-sm"
            >
              <div class="flex items-center gap-2 mb-2 text-red-500 font-bold">
                <UIcon name="i-lucide-x-circle" class="w-5 h-5" />
                <span>Worst Color 효과</span>
              </div>
              <ul class="text-sm space-y-2 text-gray-600">
                <li>• 피부가 칙칙하거나 노랗게 뜸</li>
                <li>• 결점이 부각되고 피곤해 보임</li>
                <li>• 얼굴 선이 무너져 보이거나 팽창되어 보임</li>
              </ul>
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
