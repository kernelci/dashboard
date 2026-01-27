import { createFileRoute } from '@tanstack/react-router';

import { z } from 'zod';

import type { JSX } from 'react';

import TreeListingV2 from '@/pages/TreeListing/TreesV2';
import TreeListingV1 from '@/pages/TreeListing/Trees';
import { useFeatureFlag } from '@/hooks/useFeatureFlag';

export const TreeSearchSchema = z.object({
  treeSearch: z.string().catch(''),
});

const TreeListingComponent = (): JSX.Element => {
  const { treeListingVersion } = useFeatureFlag();
  return treeListingVersion === 'v2' ? (
    <TreeListingV2 urlFromMap={{ search: '/_main/tree', navigate: '/tree' }} />
  ) : (
    <TreeListingV1 urlFromMap={{ search: '/_main/tree', navigate: '/tree' }} />
  );
};

export const Route = createFileRoute('/_main/tree/')({
  component: TreeListingComponent,
});
