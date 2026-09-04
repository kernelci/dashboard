import { useMemo, type JSX } from 'react';

import type { LabListingItem } from '@/types/lab';

import { useLabsListing } from '@/api/labs';

import { Toaster } from '@/components/ui/toaster';

import { matchesRegexOrIncludes } from '@/lib/string';

import type { LabsListingRoutesMap } from '@/utils/constants/labsListing';

import { LabsTable } from './LabsTable';

export function LabsPage({
  inputFilter,
  urlFromMap,
}: {
  inputFilter: string;
  urlFromMap: LabsListingRoutesMap;
}): JSX.Element {
  const { data, error, status, isLoading } = useLabsListing(urlFromMap.search);

  const listItems: LabListingItem[] = useMemo(() => {
    if (!data) {
      return [];
    }

    return data.labs
      .filter(lab => matchesRegexOrIncludes(lab.lab_name, inputFilter))
      .sort((a, b) => a.lab_name.localeCompare(b.lab_name));
  }, [data, inputFilter]);

  return (
    <>
      <Toaster />
      <div className="flex flex-col gap-6">
        <LabsTable
          labTableRows={listItems}
          status={status}
          queryData={data}
          error={error}
          isLoading={isLoading}
          urlFromMap={urlFromMap}
        />
      </div>
    </>
  );
}
