/* prettier-ignore-start */

/* eslint-disable */

// @ts-nocheck

// noinspection JSUnusedGlobalSymbols

// This file is auto-generated by TanStack Router

// Import Routes

import { Route as rootRoute } from './routes/~__root'
import { Route as IndexImport } from './routes/~index'
import { Route as TreeIndexImport } from './routes/~tree/~index'
import { Route as TreeTreeIdIndexImport } from './routes/~tree/~$treeId/~index'
import { Route as TreeTreeIdBuildBuildIdIndexImport } from './routes/~tree/~$treeId/~build/~$buildId/~index'

// Create/Update Routes

const IndexRoute = IndexImport.update({
  path: '/',
  getParentRoute: () => rootRoute,
} as any)

const TreeIndexRoute = TreeIndexImport.update({
  path: '/tree/',
  getParentRoute: () => rootRoute,
} as any)

const TreeTreeIdIndexRoute = TreeTreeIdIndexImport.update({
  path: '/tree/$treeId/',
  getParentRoute: () => rootRoute,
} as any)

const TreeTreeIdBuildBuildIdIndexRoute =
  TreeTreeIdBuildBuildIdIndexImport.update({
    path: '/tree/$treeId/build/$buildId/',
    getParentRoute: () => rootRoute,
  } as any)

// Populate the FileRoutesByPath interface

declare module '@tanstack/react-router' {
  interface FileRoutesByPath {
    '/': {
      id: '/'
      path: '/'
      fullPath: '/'
      preLoaderRoute: typeof IndexImport
      parentRoute: typeof rootRoute
    }
    '/tree/': {
      id: '/tree/'
      path: '/tree'
      fullPath: '/tree'
      preLoaderRoute: typeof TreeIndexImport
      parentRoute: typeof rootRoute
    }
    '/tree/$treeId/': {
      id: '/tree/$treeId/'
      path: '/tree/$treeId'
      fullPath: '/tree/$treeId'
      preLoaderRoute: typeof TreeTreeIdIndexImport
      parentRoute: typeof rootRoute
    }
    '/tree/$treeId/build/$buildId/': {
      id: '/tree/$treeId/build/$buildId/'
      path: '/tree/$treeId/build/$buildId'
      fullPath: '/tree/$treeId/build/$buildId'
      preLoaderRoute: typeof TreeTreeIdBuildBuildIdIndexImport
      parentRoute: typeof rootRoute
    }
  }
}

// Create and export the route tree

export const routeTree = rootRoute.addChildren({
  IndexRoute,
  TreeIndexRoute,
  TreeTreeIdIndexRoute,
  TreeTreeIdBuildBuildIdIndexRoute,
})

/* prettier-ignore-end */

/* ROUTE_MANIFEST_START
{
  "routes": {
    "__root__": {
      "filePath": "~__root.tsx",
      "children": [
        "/",
        "/tree/",
        "/tree/$treeId/",
        "/tree/$treeId/build/$buildId/"
      ]
    },
    "/": {
      "filePath": "~index.tsx"
    },
    "/tree/": {
      "filePath": "~tree/~index.tsx"
    },
    "/tree/$treeId/": {
      "filePath": "~tree/~$treeId/~index.tsx"
    },
    "/tree/$treeId/build/$buildId/": {
      "filePath": "~tree/~$treeId/~build/~$buildId/~index.tsx"
    }
  }
}
ROUTE_MANIFEST_END */
