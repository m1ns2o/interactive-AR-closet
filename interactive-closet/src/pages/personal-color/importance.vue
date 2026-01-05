<template>
  <div
    class="relative min-h-full flex flex-col items-center pt-16 pb-8 px-6 bg-white overflow-y-auto"
  >
    <!-- 좌측 상단 뒤로가기 버튼 -->
    <UButton
      to="/personal-color"
      icon="i-lucide-arrow-left"
      variant="ghost"
      color="neutral"
      class="absolute top-3 left-3 text-gray-600 hover:text-purple-600 hover:bg-purple-50"
    >
      뒤로가기
    </UButton>

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
            퍼스널 컬러는 피부색, 모발색, 눈동자색 등 개인의 고유한 신체 색과
            조화를 이루는 색을 말해요. 자신이 가진 신체 색과 의복, 화장, 장신구의
            색이 조화를 이루어 생기가 돌고 활기차 보이도록 연출할 수 있어요.
          </p>

          <div
            class="bg-white p-5 rounded-2xl border border-purple-100 shadow-sm"
          >
            <p class="text-base leading-relaxed text-gray-700">
              또한, 퍼스널 컬러는 <strong>'나다움, 특별한, 개성 있음'</strong>을
              표현하는 것으로, 태어날 때부터 가지고 있는 자연 그대로의 색과 서로
              어울리는 색을 파악하고, 어색하지 않고 자연스럽게 연결하는 기능을
              해요.
            </p>
          </div>

          <div
            class="bg-purple-100 p-5 rounded-2xl border border-purple-200 text-center"
          >
            <p class="text-base leading-relaxed text-purple-800 font-medium">
              우리는 사람마다 서로 다른 특징이 있음을 이해하고 이러한 아름다움을
              존중하는 자세를 갖고 이미지 메이킹을 시작해봅시다.
            </p>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>
