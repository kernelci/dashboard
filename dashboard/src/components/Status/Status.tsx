import { Link, type LinkProps } from '@tanstack/react-router';

import type { JSX } from 'react';

import ColoredCircle from '@/components/ColoredCircle/ColoredCircle';
import type { GroupedStatus } from '@/utils/status';
import { groupStatus } from '@/utils/status';

// TODO: replace the preCalculatedGroupedStatus with a type-safe approach,
// currently everything is optional
interface ITestStatus {
  pass?: number;
  error?: number;
  miss?: number;
  fail?: number;
  done?: number;
  skip?: number;
  nullStatus?: number;
  forceNumber?: boolean;
  hideInconclusive?: boolean;
  preCalculatedGroupedStatus?: GroupedStatus;
}

export const GroupedTestStatus = ({
  pass,
  error,
  miss,
  fail,
  done,
  skip,
  nullStatus,
  hideInconclusive = false,
  preCalculatedGroupedStatus,
}: ITestStatus): JSX.Element => {
  const { successCount, inconclusiveCount, failedCount } =
    preCalculatedGroupedStatus ??
    groupStatus({
      doneCount: done,
      errorCount: error,
      failCount: fail,
      missCount: miss,
      passCount: pass,
      skipCount: skip,
      nullCount: nullStatus,
    });
  return (
    <div className="flex flex-row gap-1">
      <ColoredCircle
        quantity={successCount}
        tooltipText="global.success"
        backgroundClassName="bg-light-green"
      />
      <ColoredCircle
        quantity={failedCount}
        tooltipText="global.failed"
        backgroundClassName="bg-light-red"
      />
      {!hideInconclusive && (
        <ColoredCircle
          quantity={inconclusiveCount ?? 0}
          tooltipText="global.inconclusive"
          backgroundClassName="bg-medium-gray"
        />
      )}
    </div>
  );
};

interface IStatusLinkProps {
  passLinkProps?: LinkProps;
  failLinkProps?: LinkProps;
  inconclusiveLinkProps?: LinkProps;
}

interface IBaseGroupedStatusWithLink extends IStatusLinkProps {
  groupedStatus: GroupedStatus;
  hideInconclusive?: boolean;
}

export const BaseGroupedStatusWithLink = ({
  groupedStatus,
  passLinkProps,
  failLinkProps,
  inconclusiveLinkProps,
  hideInconclusive = false,
}: IBaseGroupedStatusWithLink): JSX.Element => {
  return (
    <div className="flex flex-row gap-1">
      {
        <Link {...passLinkProps}>
          <ColoredCircle
            quantity={groupedStatus.successCount}
            tooltipText="global.success"
            backgroundClassName="bg-light-green"
          />
        </Link>
      }
      {
        <Link {...failLinkProps}>
          <ColoredCircle
            quantity={groupedStatus.failedCount}
            tooltipText="global.failed"
            backgroundClassName="bg-light-red"
          />
        </Link>
      }
      {!hideInconclusive && (
        <Link {...inconclusiveLinkProps}>
          <ColoredCircle
            quantity={groupedStatus.inconclusiveCount}
            tooltipText="global.inconclusive"
            backgroundClassName="bg-medium-gray"
          />
        </Link>
      )}
    </div>
  );
};

interface ITestStatusWithLink extends ITestStatus, IStatusLinkProps {}

export const GroupedTestStatusWithLink = ({
  pass,
  error,
  miss,
  fail,
  done,
  skip,
  nullStatus,
  hideInconclusive = false,
  passLinkProps,
  failLinkProps,
  inconclusiveLinkProps,
}: ITestStatusWithLink): JSX.Element => {
  const groupedStatus = groupStatus({
    doneCount: done,
    errorCount: error,
    failCount: fail,
    missCount: miss,
    passCount: pass,
    skipCount: skip,
    nullCount: nullStatus,
  });

  return (
    <BaseGroupedStatusWithLink
      groupedStatus={groupedStatus}
      passLinkProps={passLinkProps}
      failLinkProps={failLinkProps}
      inconclusiveLinkProps={inconclusiveLinkProps}
      hideInconclusive={hideInconclusive}
    />
  );
};

interface IBuildStatus {
  valid?: number;
  invalid?: number;
  unknown?: number;
  hideInconclusive?: boolean;
}

export const BuildStatus = ({
  valid,
  invalid,
  unknown,
  hideInconclusive = false,
}: IBuildStatus): JSX.Element => {
  return (
    <div className="flex flex-row gap-1">
      <ColoredCircle
        quantity={valid ?? 0}
        backgroundClassName="bg-light-green"
        tooltipText="global.success"
      />
      <ColoredCircle
        quantity={invalid ?? 0}
        backgroundClassName="bg-light-red"
        tooltipText="global.failed"
      />
      {!hideInconclusive && (
        <ColoredCircle
          quantity={unknown ?? 0}
          tooltipText="global.inconclusive"
          backgroundClassName="bg-light-gray"
        />
      )}
    </div>
  );
};
