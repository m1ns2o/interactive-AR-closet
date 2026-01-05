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
            <UIcon name="i-lucide-help-circle" class="w-8 h-8" />
          </div>
          <h1 class="text-3xl font-bold text-purple-900">퍼스널컬러란?</h1>
        </div>

        <div class="prose prose-purple max-w-none text-gray-700 space-y-6">
          <p class="text-lg leading-relaxed font-medium">
            개인이 가진 신체의 색과 어울리는 색을 의미해요. 퍼스널 컬러를 잘 알고
            활용하면 생기 있고 활기찬 이미지를 낼 수 있어요.
          </p>
          <p class="text-lg leading-relaxed">
            퍼스널 컬러의 유형은 크게 노란 기가 도는 <strong>웜톤</strong>과 푸른
            기가 도는 <strong>쿨톤</strong>으로 나뉩니다. 웜톤에는 봄 웜과 가을
            웜이 있고, 쿨톤에는 여름 쿨과 겨울 쿨이 있어요.
          </p>

          <div class="grid grid-cols-1 md:grid-cols-2 gap-4 mt-6">
            <!-- Spring -->
            <div class="bg-white p-5 rounded-2xl border border-yellow-200">
              <span class="block text-xs font-bold text-yellow-600 mb-1"
                >Warm Tone</span
              >
              <h3 class="text-lg font-bold text-gray-900 mb-2">
                봄 웜톤 (Spring)
              </h3>
              <p class="text-sm text-gray-600">
                따뜻하고 화사한 느낌. 생기발랄하고 귀여운 이미지가 특징입니다.
                피치, 코랄, 노란빛이 도는 밝은 색이 잘 어울립니다.
              </p>
            </div>

            <!-- Summer -->
            <div class="bg-white p-5 rounded-2xl border border-blue-200">
              <span class="block text-xs font-bold text-blue-500 mb-1"
                >Cool Tone</span
              >
              <h3 class="text-lg font-bold text-gray-900 mb-2">
                여름 쿨톤 (Summer)
              </h3>
              <p class="text-sm text-gray-600">
                시원하고 청량한 느낌. 우아하고 세련된 이미지가 특징입니다.
                파스텔 톤, 회색이 섞인 차분한 색이 잘 어울립니다.
              </p>
            </div>

            <!-- Autumn -->
            <div class="bg-white p-5 rounded-2xl border border-orange-200">
              <span class="block text-xs font-bold text-orange-600 mb-1"
                >Warm Tone</span
              >
              <h3 class="text-lg font-bold text-gray-900 mb-2">
                가을 웜톤 (Autumn)
              </h3>
              <p class="text-sm text-gray-600">
                깊이 있고 그윽한 느낌. 지적이고 성숙한 이미지가 특징입니다.
                브라운, 카키, 골드 등 차분하고 짙은 색이 잘 어울립니다.
              </p>
            </div>

            <!-- Winter -->
            <div class="bg-white p-5 rounded-2xl border border-indigo-200">
              <span class="block text-xs font-bold text-indigo-600 mb-1"
                >Cool Tone</span
              >
              <h3 class="text-lg font-bold text-gray-900 mb-2">
                겨울 쿨톤 (Winter)
              </h3>
              <p class="text-sm text-gray-600">
                강렬하고 선명한 느낌. 도시적이고 카리스마 있는 이미지가
                특징입니다. 블랙, 화이트, 쨍한 원색이 잘 어울립니다.
              </p>
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
