import { createRouter, createWebHistory } from "vue-router";
import Index from "../pages/index.vue";
import PersonalColorGuide from "../pages/personal-color/index.vue";
import PersonalColorAnalyze from "../pages/personal-color/Analyze.vue";
import PersonalColorDefinition from "../pages/personal-color/definition.vue";
import PersonalColorImportance from "../pages/personal-color/importance.vue";
import PersonalColorPreparation from "../pages/personal-color/preparation.vue";
import FaceShape from "../pages/face-shape.vue";

const routes = [
  {
    path: "/",
    name: "Home",
    component: Index,
  },
  {
    path: "/personal-color",
    name: "PersonalColorGuide",
    component: PersonalColorGuide,
  },
  {
    path: "/personal-color/analyze",
    name: "PersonalColorAnalyze",
    component: PersonalColorAnalyze,
  },
  {
    path: "/personal-color/definition",
    name: "PersonalColorDefinition",
    component: PersonalColorDefinition,
  },
  {
    path: "/personal-color/importance",
    name: "PersonalColorImportance",
    component: PersonalColorImportance,
  },
  {
    path: "/personal-color/preparation",
    name: "PersonalColorPreparation",
    component: PersonalColorPreparation,
  },
  {
    path: "/face-shape",
    name: "FaceShape",
    component: FaceShape,
  },
];

const router = createRouter({
  history: createWebHistory(),
  routes,
});

export default router;
