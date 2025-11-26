<script setup lang="ts">
import { ref } from "vue";

const links = [
  {
    label: "Virtual Try-On",
    icon: "i-lucide-shirt",
    to: "/",
  },
  {
    label: "History",
    icon: "i-lucide-history",
    to: "/history",
  },
  {
    label: "Settings",
    icon: "i-lucide-settings",
    to: "/settings",
  },
  {
    label: "Test Page",
    icon: "i-lucide-flask-conical",
    to: "/test",
  },
];

const isOpen = ref(false);
</script>

<template>
  <UApp>
    <div class="flex h-screen bg-gray-50">
      <!-- Mobile Header -->
      <div
        class="lg:hidden fixed top-0 left-0 right-0 h-16 bg-white border-b border-gray-200 flex items-center justify-between px-4 z-50"
      >
        <div class="flex items-center gap-2">
          <UIcon name="i-lucide-shirt" class="w-6 h-6 text-primary-500" />
          <span class="font-bold text-lg text-gray-900">Closet AI</span>
        </div>
        <UButton
          color="gray"
          variant="ghost"
          icon="i-lucide-menu"
          @click="isOpen = true"
        />
      </div>

      <!-- Mobile Sidebar (Slideover) -->
      <USlideover v-model="isOpen" side="left" class="lg:hidden">
        <div class="flex flex-col h-full bg-white border-r border-gray-200">
          <div
            class="p-6 border-b border-gray-200 flex items-center justify-between"
          >
            <div class="flex items-center gap-2">
              <UIcon name="i-lucide-shirt" class="w-8 h-8 text-primary-500" />
              <span class="font-bold text-xl text-gray-900">Closet AI</span>
            </div>
            <UButton
              color="gray"
              variant="ghost"
              icon="i-lucide-x"
              @click="isOpen = false"
            />
          </div>

          <div class="flex-1 overflow-y-auto py-6 px-4">
            <UVerticalNavigation :links="links" @click="isOpen = false" />
          </div>

          <div class="p-4 border-t border-gray-200">
            <div
              class="flex items-center gap-3 p-2 rounded-lg hover:bg-gray-50 cursor-pointer"
            >
              <UAvatar
                src="https://avatars.githubusercontent.com/u/739984?v=4"
                alt="User Avatar"
              />
              <div class="text-sm">
                <p class="font-medium text-gray-900">Demo User</p>
                <p class="text-gray-500">Free Plan</p>
              </div>
            </div>
          </div>
        </div>
      </USlideover>

      <!-- Desktop Sidebar -->
      <div
        class="hidden lg:flex flex-col w-64 bg-white border-r border-gray-200 h-full fixed left-0 top-0 bottom-0 z-40"
      >
        <div class="p-6 border-b border-gray-200">
          <div class="flex items-center gap-2">
            <UIcon name="i-lucide-shirt" class="w-8 h-8 text-primary-500" />
            <span class="font-bold text-xl text-gray-900">Closet AI</span>
          </div>
        </div>

        <div class="flex-1 overflow-y-auto py-6 px-4">
          <UVerticalNavigation :links="links" />
        </div>

        <div class="p-4 border-t border-gray-200">
          <div
            class="flex items-center gap-3 p-2 rounded-lg hover:bg-gray-50 cursor-pointer"
          >
            <UAvatar
              src="https://avatars.githubusercontent.com/u/739984?v=4"
              alt="User Avatar"
            />
            <div class="text-sm">
              <p class="font-medium text-gray-900">Demo User</p>
              <p class="text-gray-500">Free Plan</p>
            </div>
          </div>
        </div>
      </div>

      <!-- Main Content -->
      <div
        class="flex-1 flex flex-col min-w-0 overflow-hidden lg:pl-64 pt-16 lg:pt-0"
      >
        <header
          class="bg-white border-b border-gray-200 h-16 flex items-center justify-between px-8 sticky top-0 z-30 hidden lg:flex"
        >
          <h1 class="text-xl font-semibold text-gray-900">Virtual Try-On</h1>
          <div class="flex items-center gap-4">
            <UButton color="gray" variant="ghost" icon="i-lucide-bell" />
            <UButton color="gray" variant="ghost" icon="i-lucide-help-circle" />
          </div>
        </header>

        <main class="flex-1 overflow-y-auto p-4 sm:p-6 lg:p-8">
          <RouterView />
        </main>
      </div>
    </div>
  </UApp>
</template>
