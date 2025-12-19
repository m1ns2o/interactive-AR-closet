<script setup lang="ts">
import { ref } from "vue";
import type { NavigationMenuItem } from "@nuxt/ui";
import { useColorMode } from "@vueuse/core";

const isOpen = ref(false);

const colorMode = useColorMode();
colorMode.value = "light";

const items: NavigationMenuItem[] = [
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
</script>

<template>
  <UApp>
    <UDashboardGroup class="h-screen w-full">
      <UDashboardSidebar
        v-model="isOpen"
        mode="drawer"
        class="border-r border-gray-200"
      >
        <template #header="{ collapsed }">
          <div v-if="!collapsed" class="flex items-center gap-2">
            <UIcon name="i-lucide-shirt" class="w-6 h-6 text-primary-500" />
            <span class="font-bold text-lg">Closet AI</span>
          </div>
          <UIcon
            v-else
            name="i-lucide-shirt"
            class="w-6 h-6 text-primary-500 mx-auto"
          />
        </template>

        <UNavigationMenu :items="items" orientation="vertical" />
      </UDashboardSidebar>

      <UDashboardPanel grow class="flex flex-col h-full min-h-0">
        <UDashboardNavbar class="lg:hidden">
          <!-- <template #left>
            <UButton
              icon="i-lucide-menu"
              color="gray"
              variant="ghost"
              @click="isOpen = true"
            />
          </template> -->
        </UDashboardNavbar>

        <div class="flex-1 overflow-y-auto p-4 sm:p-6 lg:p-8">
          <RouterView />
        </div>
      </UDashboardPanel>
    </UDashboardGroup>
  </UApp>
</template>
