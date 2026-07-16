import { Link } from '@tanstack/react-router';
import type { JSX } from 'react';

import { GitCompareArrows } from 'lucide-react';
import { FormattedMessage } from 'react-intl';

import { Button } from '@/components/ui/button';

interface TreeCompareLinkProps {
  treeName: string;
  branch: string;
  hash: string;
  origin: string;
}

export function TreeCompareLink({
  treeName,
  branch,
  hash,
  origin,
}: TreeCompareLinkProps): JSX.Element {
  return (
    <Button variant="outline" size="sm" asChild>
      <Link
        to="/tree/$treeName/$branch/compare"
        params={{ treeName, branch }}
        search={{ hashA: hash, hashB: '', origin }}
        state={s => s}
      >
        <GitCompareArrows className="mr-2 h-4 w-4" />
        <FormattedMessage id="treeCompare.openCompare" />
      </Link>
    </Button>
  );
}
