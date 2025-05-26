import React from "react";
import { RouterProvider, createRouter } from "@tanstack/react-router";
import { routeTree } from "./routeTree.gen";
import { Container } from "@mantine/core";

// Set up a Router instance
const router = createRouter({
  routeTree,
  defaultPreload: "intent",
  context: undefined, // Overwrite in each route if needed
});

// Register things for typesafety
declare module "@tanstack/react-router" {
  interface Register {
    router: typeof router;
  }
}

function App() {
  return (
    <Container>
      <RouterProvider router={router} />
    </Container>
  );
}

export default App;
