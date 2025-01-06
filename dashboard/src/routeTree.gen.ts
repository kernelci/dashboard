/* prettier-ignore-start */

/* eslint-disable */

// @ts-nocheck

// noinspection JSUnusedGlobalSymbols

// This file is auto-generated by TanStack Router

// Import Routes

import { Route as rootRoute } from './routes/__root'
import { Route as TreeRouteImport } from './routes/tree/route'
import { Route as HardwareRouteImport } from './routes/hardware/route'
import { Route as IndexImport } from './routes/index'
import { Route as TreeIndexImport } from './routes/tree/index'
import { Route as HardwareIndexImport } from './routes/hardware/index'
import { Route as TreeTreeNameRouteImport } from './routes/tree/$treeName/route'
import { Route as TreeTreeIdRouteImport } from './routes/tree/$treeId/route'
import { Route as TestTestIdRouteImport } from './routes/test/$testId/route'
import { Route as HardwareHardwareIdRouteImport } from './routes/hardware/$hardwareId/route'
import { Route as BuildBuildIdRouteImport } from './routes/build/$buildId/route'
import { Route as TreeTreeIdIndexImport } from './routes/tree/$treeId/index'
import { Route as TestTestIdIndexImport } from './routes/test/$testId/index'
import { Route as HardwareHardwareIdIndexImport } from './routes/hardware/$hardwareId/index'
import { Route as BuildBuildIdIndexImport } from './routes/build/$buildId/index'
import { Route as HardwareHardwareIdTestRouteImport } from './routes/hardware/$hardwareId/test/route'
import { Route as HardwareHardwareIdBuildRouteImport } from './routes/hardware/$hardwareId/build/route'
import { Route as HardwareHardwareIdBootRouteImport } from './routes/hardware/$hardwareId/boot/route'
import { Route as TreeTreeNameBranchIndexImport } from './routes/tree/$treeName/$branch/index'
import { Route as HardwareHardwareIdTestIndexImport } from './routes/hardware/$hardwareId/test/index'
import { Route as HardwareHardwareIdBuildIndexImport } from './routes/hardware/$hardwareId/build/index'
import { Route as HardwareHardwareIdBootIndexImport } from './routes/hardware/$hardwareId/boot/index'
import { Route as TreeTreeIdTestTestIdRouteImport } from './routes/tree/$treeId/test/$testId/route'
import { Route as IssueIssueIdVersionVersionNumberRouteImport } from './routes/issue/$issueId/version/$versionNumber/route'
import { Route as TreeTreeIdTestTestIdIndexImport } from './routes/tree/$treeId/test/$testId/index'
import { Route as TreeTreeIdBuildBuildIdIndexImport } from './routes/tree/$treeId/build/$buildId/index'
import { Route as IssueIssueIdVersionVersionNumberIndexImport } from './routes/issue/$issueId/version/$versionNumber/index'
import { Route as HardwareHardwareIdTestTestIdIndexImport } from './routes/hardware/$hardwareId/test/$testId/index'
import { Route as HardwareHardwareIdBuildBuildIdIndexImport } from './routes/hardware/$hardwareId/build/$buildId/index'
import { Route as HardwareHardwareIdBootBootIdIndexImport } from './routes/hardware/$hardwareId/boot/$bootId/index'

// Create/Update Routes

const TreeRouteRoute = TreeRouteImport.update({
  path: '/tree',
  getParentRoute: () => rootRoute,
} as any)

const HardwareRouteRoute = HardwareRouteImport.update({
  path: '/hardware',
  getParentRoute: () => rootRoute,
} as any)

const IndexRoute = IndexImport.update({
  path: '/',
  getParentRoute: () => rootRoute,
} as any)

const TreeIndexRoute = TreeIndexImport.update({
  path: '/',
  getParentRoute: () => TreeRouteRoute,
} as any)

const HardwareIndexRoute = HardwareIndexImport.update({
  path: '/',
  getParentRoute: () => HardwareRouteRoute,
} as any)

const TreeTreeNameRouteRoute = TreeTreeNameRouteImport.update({
  path: '/$treeName',
  getParentRoute: () => TreeRouteRoute,
} as any)

const TreeTreeIdRouteRoute = TreeTreeIdRouteImport.update({
  path: '/$treeId',
  getParentRoute: () => TreeRouteRoute,
} as any)

const TestTestIdRouteRoute = TestTestIdRouteImport.update({
  path: '/test/$testId',
  getParentRoute: () => rootRoute,
} as any)

const HardwareHardwareIdRouteRoute = HardwareHardwareIdRouteImport.update({
  path: '/$hardwareId',
  getParentRoute: () => HardwareRouteRoute,
} as any)

const BuildBuildIdRouteRoute = BuildBuildIdRouteImport.update({
  path: '/build/$buildId',
  getParentRoute: () => rootRoute,
} as any)

const TreeTreeIdIndexRoute = TreeTreeIdIndexImport.update({
  path: '/',
  getParentRoute: () => TreeTreeIdRouteRoute,
} as any)

const TestTestIdIndexRoute = TestTestIdIndexImport.update({
  path: '/',
  getParentRoute: () => TestTestIdRouteRoute,
} as any)

const HardwareHardwareIdIndexRoute = HardwareHardwareIdIndexImport.update({
  path: '/',
  getParentRoute: () => HardwareHardwareIdRouteRoute,
} as any)

const BuildBuildIdIndexRoute = BuildBuildIdIndexImport.update({
  path: '/',
  getParentRoute: () => BuildBuildIdRouteRoute,
} as any)

const HardwareHardwareIdTestRouteRoute =
  HardwareHardwareIdTestRouteImport.update({
    path: '/test',
    getParentRoute: () => HardwareHardwareIdRouteRoute,
  } as any)

const HardwareHardwareIdBuildRouteRoute =
  HardwareHardwareIdBuildRouteImport.update({
    path: '/build',
    getParentRoute: () => HardwareHardwareIdRouteRoute,
  } as any)

const HardwareHardwareIdBootRouteRoute =
  HardwareHardwareIdBootRouteImport.update({
    path: '/boot',
    getParentRoute: () => HardwareHardwareIdRouteRoute,
  } as any)

const TreeTreeNameBranchIndexRoute = TreeTreeNameBranchIndexImport.update({
  path: '/$branch/',
  getParentRoute: () => TreeTreeNameRouteRoute,
} as any)

const HardwareHardwareIdTestIndexRoute =
  HardwareHardwareIdTestIndexImport.update({
    path: '/',
    getParentRoute: () => HardwareHardwareIdTestRouteRoute,
  } as any)

const HardwareHardwareIdBuildIndexRoute =
  HardwareHardwareIdBuildIndexImport.update({
    path: '/',
    getParentRoute: () => HardwareHardwareIdBuildRouteRoute,
  } as any)

const HardwareHardwareIdBootIndexRoute =
  HardwareHardwareIdBootIndexImport.update({
    path: '/',
    getParentRoute: () => HardwareHardwareIdBootRouteRoute,
  } as any)

const TreeTreeIdTestTestIdRouteRoute = TreeTreeIdTestTestIdRouteImport.update({
  path: '/test/$testId',
  getParentRoute: () => TreeTreeIdRouteRoute,
} as any)

const IssueIssueIdVersionVersionNumberRouteRoute =
  IssueIssueIdVersionVersionNumberRouteImport.update({
    path: '/issue/$issueId/version/$versionNumber',
    getParentRoute: () => rootRoute,
  } as any)

const TreeTreeIdTestTestIdIndexRoute = TreeTreeIdTestTestIdIndexImport.update({
  path: '/',
  getParentRoute: () => TreeTreeIdTestTestIdRouteRoute,
} as any)

const TreeTreeIdBuildBuildIdIndexRoute =
  TreeTreeIdBuildBuildIdIndexImport.update({
    path: '/build/$buildId/',
    getParentRoute: () => TreeTreeIdRouteRoute,
  } as any)

const IssueIssueIdVersionVersionNumberIndexRoute =
  IssueIssueIdVersionVersionNumberIndexImport.update({
    path: '/',
    getParentRoute: () => IssueIssueIdVersionVersionNumberRouteRoute,
  } as any)

const HardwareHardwareIdTestTestIdIndexRoute =
  HardwareHardwareIdTestTestIdIndexImport.update({
    path: '/$testId/',
    getParentRoute: () => HardwareHardwareIdTestRouteRoute,
  } as any)

const HardwareHardwareIdBuildBuildIdIndexRoute =
  HardwareHardwareIdBuildBuildIdIndexImport.update({
    path: '/$buildId/',
    getParentRoute: () => HardwareHardwareIdBuildRouteRoute,
  } as any)

const HardwareHardwareIdBootBootIdIndexRoute =
  HardwareHardwareIdBootBootIdIndexImport.update({
    path: '/$bootId/',
    getParentRoute: () => HardwareHardwareIdBootRouteRoute,
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
    '/hardware': {
      id: '/hardware'
      path: '/hardware'
      fullPath: '/hardware'
      preLoaderRoute: typeof HardwareRouteImport
      parentRoute: typeof rootRoute
    }
    '/tree': {
      id: '/tree'
      path: '/tree'
      fullPath: '/tree'
      preLoaderRoute: typeof TreeRouteImport
      parentRoute: typeof rootRoute
    }
    '/build/$buildId': {
      id: '/build/$buildId'
      path: '/build/$buildId'
      fullPath: '/build/$buildId'
      preLoaderRoute: typeof BuildBuildIdRouteImport
      parentRoute: typeof rootRoute
    }
    '/hardware/$hardwareId': {
      id: '/hardware/$hardwareId'
      path: '/$hardwareId'
      fullPath: '/hardware/$hardwareId'
      preLoaderRoute: typeof HardwareHardwareIdRouteImport
      parentRoute: typeof HardwareRouteImport
    }
    '/test/$testId': {
      id: '/test/$testId'
      path: '/test/$testId'
      fullPath: '/test/$testId'
      preLoaderRoute: typeof TestTestIdRouteImport
      parentRoute: typeof rootRoute
    }
    '/tree/$treeId': {
      id: '/tree/$treeId'
      path: '/$treeId'
      fullPath: '/tree/$treeId'
      preLoaderRoute: typeof TreeTreeIdRouteImport
      parentRoute: typeof TreeRouteImport
    }
    '/tree/$treeName': {
      id: '/tree/$treeName'
      path: '/$treeName'
      fullPath: '/tree/$treeName'
      preLoaderRoute: typeof TreeTreeNameRouteImport
      parentRoute: typeof TreeRouteImport
    }
    '/hardware/': {
      id: '/hardware/'
      path: '/'
      fullPath: '/hardware/'
      preLoaderRoute: typeof HardwareIndexImport
      parentRoute: typeof HardwareRouteImport
    }
    '/tree/': {
      id: '/tree/'
      path: '/'
      fullPath: '/tree/'
      preLoaderRoute: typeof TreeIndexImport
      parentRoute: typeof TreeRouteImport
    }
    '/hardware/$hardwareId/boot': {
      id: '/hardware/$hardwareId/boot'
      path: '/boot'
      fullPath: '/hardware/$hardwareId/boot'
      preLoaderRoute: typeof HardwareHardwareIdBootRouteImport
      parentRoute: typeof HardwareHardwareIdRouteImport
    }
    '/hardware/$hardwareId/build': {
      id: '/hardware/$hardwareId/build'
      path: '/build'
      fullPath: '/hardware/$hardwareId/build'
      preLoaderRoute: typeof HardwareHardwareIdBuildRouteImport
      parentRoute: typeof HardwareHardwareIdRouteImport
    }
    '/hardware/$hardwareId/test': {
      id: '/hardware/$hardwareId/test'
      path: '/test'
      fullPath: '/hardware/$hardwareId/test'
      preLoaderRoute: typeof HardwareHardwareIdTestRouteImport
      parentRoute: typeof HardwareHardwareIdRouteImport
    }
    '/build/$buildId/': {
      id: '/build/$buildId/'
      path: '/'
      fullPath: '/build/$buildId/'
      preLoaderRoute: typeof BuildBuildIdIndexImport
      parentRoute: typeof BuildBuildIdRouteImport
    }
    '/hardware/$hardwareId/': {
      id: '/hardware/$hardwareId/'
      path: '/'
      fullPath: '/hardware/$hardwareId/'
      preLoaderRoute: typeof HardwareHardwareIdIndexImport
      parentRoute: typeof HardwareHardwareIdRouteImport
    }
    '/test/$testId/': {
      id: '/test/$testId/'
      path: '/'
      fullPath: '/test/$testId/'
      preLoaderRoute: typeof TestTestIdIndexImport
      parentRoute: typeof TestTestIdRouteImport
    }
    '/tree/$treeId/': {
      id: '/tree/$treeId/'
      path: '/'
      fullPath: '/tree/$treeId/'
      preLoaderRoute: typeof TreeTreeIdIndexImport
      parentRoute: typeof TreeTreeIdRouteImport
    }
    '/issue/$issueId/version/$versionNumber': {
      id: '/issue/$issueId/version/$versionNumber'
      path: '/issue/$issueId/version/$versionNumber'
      fullPath: '/issue/$issueId/version/$versionNumber'
      preLoaderRoute: typeof IssueIssueIdVersionVersionNumberRouteImport
      parentRoute: typeof rootRoute
    }
    '/tree/$treeId/test/$testId': {
      id: '/tree/$treeId/test/$testId'
      path: '/test/$testId'
      fullPath: '/tree/$treeId/test/$testId'
      preLoaderRoute: typeof TreeTreeIdTestTestIdRouteImport
      parentRoute: typeof TreeTreeIdRouteImport
    }
    '/hardware/$hardwareId/boot/': {
      id: '/hardware/$hardwareId/boot/'
      path: '/'
      fullPath: '/hardware/$hardwareId/boot/'
      preLoaderRoute: typeof HardwareHardwareIdBootIndexImport
      parentRoute: typeof HardwareHardwareIdBootRouteImport
    }
    '/hardware/$hardwareId/build/': {
      id: '/hardware/$hardwareId/build/'
      path: '/'
      fullPath: '/hardware/$hardwareId/build/'
      preLoaderRoute: typeof HardwareHardwareIdBuildIndexImport
      parentRoute: typeof HardwareHardwareIdBuildRouteImport
    }
    '/hardware/$hardwareId/test/': {
      id: '/hardware/$hardwareId/test/'
      path: '/'
      fullPath: '/hardware/$hardwareId/test/'
      preLoaderRoute: typeof HardwareHardwareIdTestIndexImport
      parentRoute: typeof HardwareHardwareIdTestRouteImport
    }
    '/tree/$treeName/$branch/': {
      id: '/tree/$treeName/$branch/'
      path: '/$branch'
      fullPath: '/tree/$treeName/$branch'
      preLoaderRoute: typeof TreeTreeNameBranchIndexImport
      parentRoute: typeof TreeTreeNameRouteImport
    }
    '/hardware/$hardwareId/boot/$bootId/': {
      id: '/hardware/$hardwareId/boot/$bootId/'
      path: '/$bootId'
      fullPath: '/hardware/$hardwareId/boot/$bootId'
      preLoaderRoute: typeof HardwareHardwareIdBootBootIdIndexImport
      parentRoute: typeof HardwareHardwareIdBootRouteImport
    }
    '/hardware/$hardwareId/build/$buildId/': {
      id: '/hardware/$hardwareId/build/$buildId/'
      path: '/$buildId'
      fullPath: '/hardware/$hardwareId/build/$buildId'
      preLoaderRoute: typeof HardwareHardwareIdBuildBuildIdIndexImport
      parentRoute: typeof HardwareHardwareIdBuildRouteImport
    }
    '/hardware/$hardwareId/test/$testId/': {
      id: '/hardware/$hardwareId/test/$testId/'
      path: '/$testId'
      fullPath: '/hardware/$hardwareId/test/$testId'
      preLoaderRoute: typeof HardwareHardwareIdTestTestIdIndexImport
      parentRoute: typeof HardwareHardwareIdTestRouteImport
    }
    '/issue/$issueId/version/$versionNumber/': {
      id: '/issue/$issueId/version/$versionNumber/'
      path: '/'
      fullPath: '/issue/$issueId/version/$versionNumber/'
      preLoaderRoute: typeof IssueIssueIdVersionVersionNumberIndexImport
      parentRoute: typeof IssueIssueIdVersionVersionNumberRouteImport
    }
    '/tree/$treeId/build/$buildId/': {
      id: '/tree/$treeId/build/$buildId/'
      path: '/build/$buildId'
      fullPath: '/tree/$treeId/build/$buildId'
      preLoaderRoute: typeof TreeTreeIdBuildBuildIdIndexImport
      parentRoute: typeof TreeTreeIdRouteImport
    }
    '/tree/$treeId/test/$testId/': {
      id: '/tree/$treeId/test/$testId/'
      path: '/'
      fullPath: '/tree/$treeId/test/$testId/'
      preLoaderRoute: typeof TreeTreeIdTestTestIdIndexImport
      parentRoute: typeof TreeTreeIdTestTestIdRouteImport
    }
  }
}

// Create and export the route tree

export const routeTree = rootRoute.addChildren({
  IndexRoute,
  HardwareRouteRoute: HardwareRouteRoute.addChildren({
    HardwareHardwareIdRouteRoute: HardwareHardwareIdRouteRoute.addChildren({
      HardwareHardwareIdBootRouteRoute:
        HardwareHardwareIdBootRouteRoute.addChildren({
          HardwareHardwareIdBootIndexRoute,
          HardwareHardwareIdBootBootIdIndexRoute,
        }),
      HardwareHardwareIdBuildRouteRoute:
        HardwareHardwareIdBuildRouteRoute.addChildren({
          HardwareHardwareIdBuildIndexRoute,
          HardwareHardwareIdBuildBuildIdIndexRoute,
        }),
      HardwareHardwareIdTestRouteRoute:
        HardwareHardwareIdTestRouteRoute.addChildren({
          HardwareHardwareIdTestIndexRoute,
          HardwareHardwareIdTestTestIdIndexRoute,
        }),
      HardwareHardwareIdIndexRoute,
    }),
    HardwareIndexRoute,
  }),
  TreeRouteRoute: TreeRouteRoute.addChildren({
    TreeTreeIdRouteRoute: TreeTreeIdRouteRoute.addChildren({
      TreeTreeIdIndexRoute,
      TreeTreeIdTestTestIdRouteRoute:
        TreeTreeIdTestTestIdRouteRoute.addChildren({
          TreeTreeIdTestTestIdIndexRoute,
        }),
      TreeTreeIdBuildBuildIdIndexRoute,
    }),
    TreeTreeNameRouteRoute: TreeTreeNameRouteRoute.addChildren({
      TreeTreeNameBranchIndexRoute,
    }),
    TreeIndexRoute,
  }),
  BuildBuildIdRouteRoute: BuildBuildIdRouteRoute.addChildren({
    BuildBuildIdIndexRoute,
  }),
  TestTestIdRouteRoute: TestTestIdRouteRoute.addChildren({
    TestTestIdIndexRoute,
  }),
  IssueIssueIdVersionVersionNumberRouteRoute:
    IssueIssueIdVersionVersionNumberRouteRoute.addChildren({
      IssueIssueIdVersionVersionNumberIndexRoute,
    }),
})

/* prettier-ignore-end */

/* ROUTE_MANIFEST_START
{
  "routes": {
    "__root__": {
      "filePath": "__root.tsx",
      "children": [
        "/",
        "/hardware",
        "/tree",
        "/build/$buildId",
        "/test/$testId",
        "/issue/$issueId/version/$versionNumber"
      ]
    },
    "/": {
      "filePath": "index.tsx"
    },
    "/hardware": {
      "filePath": "hardware/route.tsx",
      "children": [
        "/hardware/$hardwareId",
        "/hardware/"
      ]
    },
    "/tree": {
      "filePath": "tree/route.tsx",
      "children": [
        "/tree/$treeId",
        "/tree/$treeName",
        "/tree/"
      ]
    },
    "/build/$buildId": {
      "filePath": "build/$buildId/route.tsx",
      "children": [
        "/build/$buildId/"
      ]
    },
    "/hardware/$hardwareId": {
      "filePath": "hardware/$hardwareId/route.tsx",
      "parent": "/hardware",
      "children": [
        "/hardware/$hardwareId/boot",
        "/hardware/$hardwareId/build",
        "/hardware/$hardwareId/test",
        "/hardware/$hardwareId/"
      ]
    },
    "/test/$testId": {
      "filePath": "test/$testId/route.tsx",
      "children": [
        "/test/$testId/"
      ]
    },
    "/tree/$treeId": {
      "filePath": "tree/$treeId/route.tsx",
      "parent": "/tree",
      "children": [
        "/tree/$treeId/",
        "/tree/$treeId/test/$testId",
        "/tree/$treeId/build/$buildId/"
      ]
    },
    "/tree/$treeName": {
      "filePath": "tree/$treeName/route.tsx",
      "parent": "/tree",
      "children": [
        "/tree/$treeName/$branch/"
      ]
    },
    "/hardware/": {
      "filePath": "hardware/index.tsx",
      "parent": "/hardware"
    },
    "/tree/": {
      "filePath": "tree/index.tsx",
      "parent": "/tree"
    },
    "/hardware/$hardwareId/boot": {
      "filePath": "hardware/$hardwareId/boot/route.tsx",
      "parent": "/hardware/$hardwareId",
      "children": [
        "/hardware/$hardwareId/boot/",
        "/hardware/$hardwareId/boot/$bootId/"
      ]
    },
    "/hardware/$hardwareId/build": {
      "filePath": "hardware/$hardwareId/build/route.tsx",
      "parent": "/hardware/$hardwareId",
      "children": [
        "/hardware/$hardwareId/build/",
        "/hardware/$hardwareId/build/$buildId/"
      ]
    },
    "/hardware/$hardwareId/test": {
      "filePath": "hardware/$hardwareId/test/route.tsx",
      "parent": "/hardware/$hardwareId",
      "children": [
        "/hardware/$hardwareId/test/",
        "/hardware/$hardwareId/test/$testId/"
      ]
    },
    "/build/$buildId/": {
      "filePath": "build/$buildId/index.tsx",
      "parent": "/build/$buildId"
    },
    "/hardware/$hardwareId/": {
      "filePath": "hardware/$hardwareId/index.tsx",
      "parent": "/hardware/$hardwareId"
    },
    "/test/$testId/": {
      "filePath": "test/$testId/index.tsx",
      "parent": "/test/$testId"
    },
    "/tree/$treeId/": {
      "filePath": "tree/$treeId/index.tsx",
      "parent": "/tree/$treeId"
    },
    "/issue/$issueId/version/$versionNumber": {
      "filePath": "issue/$issueId/version/$versionNumber/route.tsx",
      "children": [
        "/issue/$issueId/version/$versionNumber/"
      ]
    },
    "/tree/$treeId/test/$testId": {
      "filePath": "tree/$treeId/test/$testId/route.tsx",
      "parent": "/tree/$treeId",
      "children": [
        "/tree/$treeId/test/$testId/"
      ]
    },
    "/hardware/$hardwareId/boot/": {
      "filePath": "hardware/$hardwareId/boot/index.tsx",
      "parent": "/hardware/$hardwareId/boot"
    },
    "/hardware/$hardwareId/build/": {
      "filePath": "hardware/$hardwareId/build/index.tsx",
      "parent": "/hardware/$hardwareId/build"
    },
    "/hardware/$hardwareId/test/": {
      "filePath": "hardware/$hardwareId/test/index.tsx",
      "parent": "/hardware/$hardwareId/test"
    },
    "/tree/$treeName/$branch/": {
      "filePath": "tree/$treeName/$branch/index.tsx",
      "parent": "/tree/$treeName"
    },
    "/hardware/$hardwareId/boot/$bootId/": {
      "filePath": "hardware/$hardwareId/boot/$bootId/index.tsx",
      "parent": "/hardware/$hardwareId/boot"
    },
    "/hardware/$hardwareId/build/$buildId/": {
      "filePath": "hardware/$hardwareId/build/$buildId/index.tsx",
      "parent": "/hardware/$hardwareId/build"
    },
    "/hardware/$hardwareId/test/$testId/": {
      "filePath": "hardware/$hardwareId/test/$testId/index.tsx",
      "parent": "/hardware/$hardwareId/test"
    },
    "/issue/$issueId/version/$versionNumber/": {
      "filePath": "issue/$issueId/version/$versionNumber/index.tsx",
      "parent": "/issue/$issueId/version/$versionNumber"
    },
    "/tree/$treeId/build/$buildId/": {
      "filePath": "tree/$treeId/build/$buildId/index.tsx",
      "parent": "/tree/$treeId"
    },
    "/tree/$treeId/test/$testId/": {
      "filePath": "tree/$treeId/test/$testId/index.tsx",
      "parent": "/tree/$treeId/test/$testId"
    }
  }
}
ROUTE_MANIFEST_END */
