import { FormattedMessage } from 'react-intl';

import {
  useSearch,
  useNavigate,
  useLocation,
  useRouterState,
} from '@tanstack/react-router';

import { useCallback, useEffect, useMemo, type JSX } from 'react';

import Select, { SelectItem } from '@/components/Select/Select';
import type { PossibleMonitorPath, TOrigins } from '@/types/general';
import { zOrigin, zOriginEnum } from '@/types/general';

const getTargetPath = (basePath: string): PossibleMonitorPath => {
  switch (basePath) {
    case 'tree':
      return '/tree';
    case 'hardware':
      return '/hardware';
    case 'issue':
      return '/issue';
    default:
      return '/tree';
  }
};

const OriginSelect = ({ basePath }: { basePath: string }): JSX.Element => {
  const { origin: unsafeOrigin } = useSearch({ strict: false });
  const origin = zOrigin.parse(unsafeOrigin);

  const targetPath = getTargetPath(basePath);
  const navigate = useNavigate({ from: targetPath });

  const onValueChange = useCallback(
    (value: TOrigins) => {
      navigate({
        to: targetPath,
        search: previousSearch => ({ ...previousSearch, origin: value }),
      });
    },
    [navigate, targetPath],
  );

  const selectItems = useMemo(
    () =>
      zOriginEnum.options.map(option => (
        <SelectItem key={option} value={option}>
          {option}
        </SelectItem>
      )),
    [],
  );

  useEffect(() => {
    if (unsafeOrigin === undefined) {
      navigate({
        search: previousSearch => ({ ...previousSearch, origin: origin }),
      });
    }
  });

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
  const { pathname } = useLocation();
  const redirectFrom = useRouterState({ select: s => s.location.state.from });
  const splitPath = pathname.split('/')[1] ?? '';
  const basePath = redirectFrom ?? splitPath;

  return (
    <div className="fixed top-0 z-10 mx-52 flex h-20 w-full bg-white px-16">
      <div className="flex flex-row items-center justify-between">
        <span className="mr-14 text-2xl">
          <TitleName basePath={basePath} />
        </span>
        {(basePath === 'tree' ||
          basePath === 'hardware' ||
          basePath === 'issue') && <OriginSelect basePath={basePath} />}
      </div>
    </div>
  );
};

export default TopBar;
