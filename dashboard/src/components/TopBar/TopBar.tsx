import { FormattedMessage } from 'react-intl';

import { useSearch, useNavigate, useMatches } from '@tanstack/react-router';

import { useCallback, useEffect, useMemo, useState, type JSX } from 'react';

import { HiMenu } from 'react-icons/hi';

import Select, { SelectItem } from '@/components/Select/Select';
import { DEFAULT_ORIGIN } from '@/types/general';
import { useLabOrigins, useOrigins } from '@/api/origin';
import { Button } from '@/components/ui/button';
import MobileSideMenu from '@/components/SideMenu/MobileSideMenu';

import { SearchBoxNavigate } from '@/components/SearchBoxNavigate';
import { treeListingCleanFullPaths } from '@/utils/constants/treeListing';
import { hwListingCleanFullPaths } from '@/utils/constants/hardwareListing';
import { labsListingCleanFullPaths } from '@/utils/constants/labsListing';

type OriginSource = 'checkout' | 'test' | 'lab';

const OriginSelect = ({
  originSource,
}: {
  originSource: OriginSource;
}): JSX.Element => {
  const { origin } = useSearch({ strict: false });
  const isLabSource = originSource === 'lab';
  const { data: originData, status: originStatus } = useOrigins({
    enabled: !isLabSource,
  });
  const { data: labOriginData, status: labOriginStatus } = useLabOrigins({
    enabled: isLabSource,
  });

  const navigate = useNavigate();

  const onValueChange = useCallback(
    (value: string) => {
      navigate({
        to: '.',
        search: previousSearch => ({ ...previousSearch, origin: value }),
      });
    },
    [navigate],
  );

  const pageOrigins = useMemo(() => {
    if (isLabSource) {
      return labOriginData?.origins ?? [];
    }
    if (!originData) {
      return [];
    }
    return (
      (originSource === 'test'
        ? originData.test_origins
        : originData.checkout_origins) ?? []
    );
  }, [isLabSource, labOriginData, originData, originSource]);

  const selectItems = useMemo(() => {
    return pageOrigins.map(option => (
      <SelectItem
        key={option}
        value={option}
        data-test-id={`origin-option-${option}`}
      >
        {option}
      </SelectItem>
    ));
  }, [pageOrigins]);

  useEffect(() => {
    if (pageOrigins.length === 0) {
      return;
    }

    if (origin === undefined || !pageOrigins.includes(origin)) {
      navigate({
        to: '.',
        search: previousSearch => ({
          ...previousSearch,
          origin: DEFAULT_ORIGIN,
        }),
      });
    }
  }, [navigate, origin, pageOrigins]);

  if ((isLabSource ? labOriginStatus : originStatus) === 'pending') {
    return <FormattedMessage id="global.loading" />;
  }

  return (
    <div className="flex items-center">
      <span className="text-dim-gray mr-4 hidden text-base font-medium sm:block">
        <FormattedMessage id="global.origin" />
      </span>
      <Select
        onValueChange={onValueChange}
        value={origin}
        data-test-id="origin-dropdown"
      >
        {selectItems}
      </Select>
    </div>
  );
};

const TitleName = ({ basePath }: { basePath: string }): JSX.Element => {
  switch (basePath) {
    case 'tree':
      return <FormattedMessage id="routes.treeMonitor" />;
    case 'hardware':
      return <FormattedMessage id="routes.hardwareMonitor" />;
    case 'issues':
      return <FormattedMessage id="routes.issueMonitor" />;
    case 'build':
      return <FormattedMessage id="routes.buildDetails" />;
    case 'test':
      return <FormattedMessage id="routes.testDetails" />;
    case 'issue':
      return <FormattedMessage id="routes.issueDetails" />;
    case 'metrics':
      return <FormattedMessage id="routes.metricsMonitor" />;
    case 'labs':
      return <FormattedMessage id="routes.labsMonitor" />;
    default:
      return <FormattedMessage id="routes.unknown" />;
  }
};

const TopBar = (): JSX.Element => {
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);
  const matches = useMatches();

  const routeInfo = useMemo(() => {
    const lastMatch = matches[matches.length - 1];
    const firstUrlLocation = lastMatch?.pathname.split('/')[1] ?? '';
    const cleanFullPath = lastMatch?.fullPath.replace(/\//g, '') ?? '';
    const isTreeListing = treeListingCleanFullPaths.includes(cleanFullPath);
    const isHardwareListing = hwListingCleanFullPaths.includes(cleanFullPath);
    const isLabsListing = labsListingCleanFullPaths.includes(cleanFullPath);
    const isListingPage =
      isTreeListing ||
      isHardwareListing ||
      isLabsListing ||
      cleanFullPath.includes('issues');

    return {
      firstUrlLocation,
      isTreeListing: isTreeListing,
      isHardwarePage: cleanFullPath.includes('hardware'),
      isLabsPage: isLabsListing,
      isListingPage: isListingPage,
    };
  }, [matches]);

  return (
    <>
      <div className="fixed top-0 z-10 flex h-20 w-full max-w-full bg-white px-6 md:max-w-[calc(100%-14rem)] md:px-16">
        <div className="flex w-full flex-row items-center justify-between">
          <div className="flex w-full flex-row items-center gap-4">
            <Button
              variant="ghost"
              size="icon"
              className="md:hidden"
              onClick={() => setIsMobileMenuOpen(true)}
              aria-label="Open menu"
            >
              <HiMenu className="size-6" />
            </Button>
            <span className="mr-2 text-2xl sm:mr-10">
              <TitleName basePath={routeInfo.firstUrlLocation} />
            </span>
            {(routeInfo.isTreeListing ||
              routeInfo.isHardwarePage ||
              routeInfo.isLabsPage) && (
              <OriginSelect
                originSource={
                  routeInfo.isLabsPage
                    ? 'lab'
                    : routeInfo.isHardwarePage
                      ? 'test'
                      : 'checkout'
                }
              />
            )}
            <span className="ml-0 flex w-full px-6 lg:ml-14">
              {routeInfo.isListingPage && <SearchBoxNavigate />}
            </span>
          </div>
        </div>
      </div>
      <MobileSideMenu
        isOpen={isMobileMenuOpen}
        onClose={() => setIsMobileMenuOpen(false)}
      />
    </>
  );
};

export default TopBar;
