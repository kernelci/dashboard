import { FormattedMessage } from 'react-intl';

import {
  useSearch,
  useNavigate,
  useRouterState,
  useMatches,
} from '@tanstack/react-router';

import { useCallback, useEffect, useMemo, useState, type JSX } from 'react';

import { HiMenu } from 'react-icons/hi';

import Select, { SelectItem } from '@/components/Select/Select';
import { DEFAULT_ORIGIN, type PossibleMonitorPath } from '@/types/general';
import { useOrigins } from '@/api/origin';
import { Button } from '@/components/ui/button';
import MobileSideMenu from '@/components/SideMenu/MobileSideMenu';

const getTargetPath = (basePath: string): PossibleMonitorPath => {
  switch (basePath) {
    case 'hardware':
      return '/hardware';
    case 'hardware-new':
      return '/hardware-new';
    case 'issues':
      return '/issues';
    default:
      return '/tree';
  }
};

const OriginSelect = ({ basePath }: { basePath: string }): JSX.Element => {
  const { origin } = useSearch({ strict: false });
  const { data: originData, status: originStatus } = useOrigins();

  const targetPath = getTargetPath(basePath);
  const navigate = useNavigate({ from: targetPath });

  const onValueChange = useCallback(
    (value: string) => {
      navigate({
        to: targetPath,
        search: previousSearch => ({ ...previousSearch, origin: value }),
      });
    },
    [navigate, targetPath],
  );

  const selectItems = useMemo(() => {
    if (originData === undefined) {
      return <></>;
    }

    let pageOrigins: string[];
    if (targetPath === '/hardware' || targetPath === '/hardware-new') {
      pageOrigins = originData.test_origins;
    } else {
      pageOrigins = originData.checkout_origins;
    }

    return pageOrigins.map(option => (
      <SelectItem
        key={option}
        value={option}
        data-test-id={`origin-option-${option}`}
      >
        {option}
      </SelectItem>
    ));
  }, [originData, targetPath]);

  useEffect(() => {
    if (origin === undefined) {
      navigate({
        search: previousSearch => ({
          ...previousSearch,
          origin: DEFAULT_ORIGIN,
        }),
      });
    }
  });

  if (originStatus === 'pending') {
    return <FormattedMessage id="global.loading" />;
  }

  return (
    <div className="flex items-center">
      <span className="text-dim-gray mr-4 text-base font-medium">
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
    case 'hardware-new':
      return <FormattedMessage id="routes.hardwareNewMonitor" />;
    case 'issues':
      return <FormattedMessage id="routes.issueMonitor" />;
    case 'build':
      return <FormattedMessage id="routes.buildDetails" />;
    case 'test':
      return <FormattedMessage id="routes.testDetails" />;
    case 'issue':
      return <FormattedMessage id="routes.issueDetails" />;
    default:
      return <FormattedMessage id="routes.unknown" />;
  }
};

const TopBar = (): JSX.Element => {
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);
  const matches = useMatches();
  const redirectStateFrom = useRouterState({
    select: s => s.location.state.from,
  });

  const routeInfo = useMemo(() => {
    const lastMatch = matches[matches.length - 1];
    const firstUrlLocation = lastMatch?.pathname.split('/')[1] ?? '';
    const cleanFullPath = lastMatch?.fullPath.replace(/\//g, '') ?? '';

    return {
      firstUrlLocation,
      isTreeListing: cleanFullPath === 'tree',
      isHardwarePage: cleanFullPath.includes('hardware'),
    };
  }, [matches]);

  const basePath = redirectStateFrom ?? routeInfo.firstUrlLocation;

  return (
    <>
      <div className="fixed top-0 z-10 flex h-20 w-full bg-white px-6 md:px-16">
        <div className="flex w-full flex-row items-center justify-between">
          <div className="flex flex-row items-center gap-4">
            <Button
              variant="ghost"
              size="icon"
              className="md:hidden"
              onClick={() => setIsMobileMenuOpen(true)}
              aria-label="Open menu"
            >
              <HiMenu className="size-6" />
            </Button>
            <span className="mr-10 text-2xl">
              <TitleName basePath={basePath} />
            </span>
            {(routeInfo.isTreeListing || routeInfo.isHardwarePage) && (
              <OriginSelect basePath={basePath} />
            )}
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
