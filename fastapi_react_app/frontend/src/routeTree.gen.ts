import { createRoute, createRootRoute, Outlet } from "@tanstack/react-router";
import { IndexPage } from "./pages/Evals";
import { EvaluatePage } from "./pages/EvalDetails";
// import App from "./App"; // Removed to break circular dependency
import React from "react"; // Import React for Outlet

const rootRoute = createRootRoute({
  component: () => React.createElement(Outlet), // Use React.createElement
});

const indexRoute = createRoute({
  getParentRoute: () => rootRoute,
  path: "/",
  component: IndexPage,
});

const evaluateRoute = createRoute({
  getParentRoute: () => rootRoute,
  path: "/evaluate/$inputId",
  component: EvaluatePage,
});

export const routeTree = rootRoute.addChildren([indexRoute, evaluateRoute]);
