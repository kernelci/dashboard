import { Link } from '@tanstack/react-router';
import { FormattedMessage } from 'react-intl';
import type { JSX } from 'react';

import { Button } from '@/components/ui/button';
import { MemoizedSectionError } from '@/components/DetailsPages/SectionError';
import { getMissingTreeResource } from '@/utils/treeDetails';

export const TreeQueryError = ({
  error,
  treeName,
  branch,
  hash,
  origin,
}: {
  error: Error | null;
  treeName?: string;
  branch?: string;
  hash?: string;
  origin: string;
}): JSX.Element => {
  const resource = getMissingTreeResource(error);

  return (
    <div
      className="flex min-h-[400px] flex-col items-center justify-center gap-5 px-6 py-12 text-center"
      data-test-id="tree-query-error"
      role="status"
    >
      {resource ? (
        <>
          <p className="text-weak-gray text-lg">404</p>
          <h1 className="text-3xl font-bold">
            <FormattedMessage id={`treeDetails.missing.${resource}`} />
          </h1>
          <p className="max-w-2xl break-all">
            <FormattedMessage
              id={`treeDetails.missing.${resource}.description`}
              values={{
                tree: treeName ?? '',
                branch: branch ?? '',
                hash: hash ?? '',
                origin,
              }}
            />
          </p>
        </>
      ) : (
        <MemoizedSectionError
          isLoading={false}
          errorMessage={error?.message}
          emptyLabel="treeDetails.notFound"
        />
      )}
      <Button asChild>
        <Link to="/tree" search={{ origin }}>
          <FormattedMessage id="treeDetails.backToTrees" />
        </Link>
      </Button>
    </div>
  );
};
