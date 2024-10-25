import ColoredCircle from '@/components/ColoredCircle/ColoredCircle';
import { groupStatus } from '@/utils/status';

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
}: ITestStatus): JSX.Element => {
  const { successCount, inconclusiveCount, failedCount } = groupStatus({
    doneCount: done ?? 0,
    errorCount: error ?? 0,
    failCount: fail ?? 0,
    missCount: miss ?? 0,
    passCount: pass ?? 0,
    skipCount: skip ?? 0,
    nullCount: nullStatus ?? 0,
  });
  return (
    <div className="flex flex-row gap-1">
      {
        <ColoredCircle
          quantity={successCount ?? 0}
          tooltipText="global.success"
          backgroundClassName="bg-lightGreen"
        />
      }
      {
        <ColoredCircle
          quantity={failedCount}
          tooltipText="global.failed"
          backgroundClassName="bg-lightRed"
        />
      }
      {!hideInconclusive && (
        <ColoredCircle
          quantity={inconclusiveCount ?? 0}
          tooltipText="global.inconclusive"
          backgroundClassName="bg-mediumGray"
        />
      )}
    </div>
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
        backgroundClassName="bg-lightGreen"
        tooltipText="global.success"
      />
      <ColoredCircle
        quantity={invalid ?? 0}
        backgroundClassName="bg-lightRed"
        tooltipText="global.failed"
      />
      {!hideInconclusive && (
        <ColoredCircle
          quantity={unknown ?? 0}
          tooltipText="global.inconclusive"
          backgroundClassName="bg-lightGray"
        />
      )}
    </div>
  );
};
