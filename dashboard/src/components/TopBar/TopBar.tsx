import { FormattedMessage } from 'react-intl';

import {
  useSearch,
  useNavigate,
  useRouterState,
  useMatches,
} from '@tanstack/react-router';

import { useCallback, useEffect, useMemo, type JSX } from 'react';

import Select, { SelectItem } from '@/components/Select/Select';
import { DEFAULT_ORIGIN, type PossibleMonitorPath } from '@/types/general';
import { useOrigins } from '@/api/origin';

const getTargetPath = (basePath: string): PossibleMonitorPath => {
  switch (basePath) {
    case 'hardware':
      return '/hardware';
    case 'issues':
      return '/issues';
    default:
      return '/tree';
  }
};

const OriginSelect = ({ basePath }: { basePath: string }): JSX.Element => {
  const { origin } = useSearch({ strict: false });
  const validOrigins = useOrigins();

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

  const selectItems = useMemo(
    () =>
      validOrigins.data?.map(option => (
        <SelectItem key={option} value={option}>
          {option}
        </SelectItem>
      )),
    [validOrigins.data],
  );

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

  if (validOrigins.status === 'pending') {
    return <FormattedMessage id="global.loading" />;
  }

  return (
    <div className="flex items-center">
      <span className="text-dim-gray mr-4 text-base font-medium">
        <FormattedMessage id="global.origin" />
      </span>
      <Select onValueChange={onValueChange} value={origin}>
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
    default:
      return <FormattedMessage id="routes.unknown" />;
  }
};

const TopBar = (): JSX.Element => {
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
    <div className="fixed top-0 z-10 flex h-20 w-full bg-white px-16">
      <div className="flex flex-row items-center justify-between">
        <span className="mr-14 text-2xl">
          <TitleName basePath={basePath} />
        </span>
        {(routeInfo.isTreeListing || routeInfo.isHardwarePage) && (
          <OriginSelect basePath={basePath} />
        )}
      </div>
    </div>
  );
};

export default TopBar;
