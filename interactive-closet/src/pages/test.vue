<template>
  <div class="space-y-6">
    <div class="flex items-center justify-between">
      <h2 class="text-2xl font-bold text-gray-900">Test Page</h2>
    </div>

    <UCard>
      <template #header>
        <div class="flex items-center gap-2">
          <UIcon
            name="i-lucide-flask-conical"
            class="w-5 h-5 text-primary-500"
          />
          <h3 class="font-medium text-gray-900">Component Test Area</h3>
        </div>
      </template>

      <div class="space-y-4">
        <p class="text-gray-600">
          This is a test page to verify navigation and component rendering.
        </p>

        <div class="flex gap-4">
          <UButton>Primary Button</UButton>
          <UButton color="white">Secondary Button</UButton>
          <UButton color="red" variant="soft">Danger Button</UButton>
        </div>

        <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
          <UCard>
            <div class="text-center p-4">
              <UIcon
                name="i-lucide-check-circle"
                class="w-8 h-8 text-green-500 mb-2"
              />
              <p class="font-medium">Success State</p>
            </div>
          </UCard>
          <UCard>
            <div class="text-center p-4">
              <UIcon
                name="i-lucide-alert-triangle"
                class="w-8 h-8 text-yellow-500 mb-2"
              />
              <p class="font-medium">Warning State</p>
            </div>
          </UCard>
          <UCard>
            <div class="text-center p-4">
              <UIcon
                name="i-lucide-x-circle"
                class="w-8 h-8 text-red-500 mb-2"
              />
              <p class="font-medium">Error State</p>
            </div>
          </UCard>
        </div>
      </div>
    </UCard>
  </div>
</template>
