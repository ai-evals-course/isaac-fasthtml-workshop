import React from "react";
import { RouterProvider, createRouter } from "@tanstack/react-router";
import { routeTree } from "./routeTree.gen";
import { AppShell, Burger, Button, Container, Group, Skeleton } from "@mantine/core";

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
    <AppShell header={{ height: 60 }} padding="md">
      <AppShell.Header>
        <Group h="100%" px="md">
          <Button variant="subtle" onClick={() => router.navigate({ to: "/" })}>
            FastAPI+React Demo
          </Button>
        </Group>
      </AppShell.Header>
      <AppShell.Main>
        <Container fluid h={50}>
          <RouterProvider router={router} />
        </Container>
      </AppShell.Main>
    </AppShell>
  );
}

export default App;
