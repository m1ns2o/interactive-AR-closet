<template>
  <Suspense>
    <UApp>
      <UHeader>
        <template #left>
          <RouterLink to="/" class="flex items-center gap-2">
            <UIcon name="i-lucide-shirt" class="w-6 h-6" />
            <span class="font-bold text-lg">InteractiveARcloset</span>
          </RouterLink>
        </template>
      </UHeader>

      <UMain>
        <RouterView />
      </UMain>

      <UFooter>
        <template #left>
          <p class="text-sm text-gray-600">
            Powered by IDM-VTON • © {{ new Date().getFullYear() }}
          </p>
        </template>

        <template #right>
          <UBadge color="primary" variant="subtle">
            AI Virtual Try-On
          </UBadge>
        </template>
      </UFooter>
    </UApp>
  </Suspense>
</template>
