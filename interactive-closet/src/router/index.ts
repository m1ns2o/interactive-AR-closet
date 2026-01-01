import { createRouter, createWebHistory } from "vue-router";
import Index from "../pages/index.vue";
import Test from "../pages/test.vue";
import PersonalColor from "../pages/personal-color.vue";
import FaceShape from "../pages/face-shape.vue";

const routes = [
  {
    path: "/",
    name: "Home",
    component: Index,
  },
  {
    path: "/personal-color",
    name: "PersonalColor",
    component: PersonalColor,
  },
  {
    path: "/face-shape",
    name: "FaceShape",
    component: FaceShape,
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
