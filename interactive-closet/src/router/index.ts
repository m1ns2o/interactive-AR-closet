import { createRouter, createWebHistory } from "vue-router";
import Index from "../pages/index.vue";
import Test from "../pages/test.vue";

const routes = [
  {
    path: "/",
    name: "Home",
    component: Index,
  },
  {
    path: "/test",
    name: "Test",
    component: Test,
  },
  {
    path: "/history",
    name: "History",
    component: Index, // Placeholder
  },
  {
    path: "/settings",
    name: "Settings",
    component: Index, // Placeholder
  },
];

const router = createRouter({
  history: createWebHistory(),
  routes,
});

export default router;
