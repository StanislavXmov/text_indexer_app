import type { QueryClient } from "@tanstack/react-query";
import { RootComponent } from "./root-component";
import {
  createRootRouteWithContext,
  createRoute,
  Link,
} from "@tanstack/react-router";
import { Home } from "./pages/home";

export const rootRoute = createRootRouteWithContext<{
  queryClient: QueryClient;
}>()({
  component: RootComponent,
  notFoundComponent: () => {
    return (
      <div>
        <p>This is the notFoundComponent configured on root route</p>
        <Link to="/">Start Over</Link>
      </div>
    );
  },
});

export const homeRoute = createRoute({
  getParentRoute: () => rootRoute,
  path: "/",
  component: Home,
});
