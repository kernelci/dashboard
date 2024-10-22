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
}

interface IBuildStatus {
  valid?: number;
  invalid?: number;
  unknown?: number;
}

export const TestStatus = ({
  pass,
  error,
  miss,
  fail,
  done,
  skip,
  forceNumber = true,
}: ITestStatus): JSX.Element => {
  return (
    <div className="flex flex-row gap-1">
      {(forceNumber || Boolean(pass)) && (
        <ColoredCircle
          quantity={pass ?? 0}
          tooltipText="global.pass"
          backgroundClassName="bg-lightGreen"
        />
      )}
      {(forceNumber || Boolean(error)) && (
        <ColoredCircle
          quantity={error ?? 0}
          tooltipText="global.error"
          backgroundClassName="bg-lightRed"
        />
      )}
      {(forceNumber || Boolean(miss)) && (
        <ColoredCircle
          quantity={miss ?? 0}
          tooltipText="global.missed"
          backgroundClassName="bg-lightGray"
        />
      )}
      {(forceNumber || Boolean(fail)) && (
        <ColoredCircle
          quantity={fail ?? 0}
          tooltipText="global.failed"
          backgroundClassName="bg-yellow"
        />
      )}
      {(forceNumber || Boolean(done)) && (
        <ColoredCircle
          quantity={done ?? 0}
          tooltipText="global.done"
          backgroundClassName="bg-lightBlue"
        />
      )}
      {(forceNumber || Boolean(skip)) && (
        <ColoredCircle
          quantity={skip ?? 0}
          tooltipText="global.skipped"
          backgroundClassName="bg-mediumGray"
        />
      )}
    </div>
  );
};

export const GroupedTestStatus = ({
  pass,
  error,
  miss,
  fail,
  done,
  skip,
  nullStatus,
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
      {
        <ColoredCircle
          quantity={inconclusiveCount ?? 0}
          tooltipText="global.inconclusive"
          backgroundClassName="bg-mediumGray"
        />
      }
    </div>
  );
};

export const BuildStatus = ({
  valid,
  invalid,
  unknown,
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
      <ColoredCircle
        quantity={unknown ?? 0}
        tooltipText="global.inconclusive"
        backgroundClassName="bg-lightGray"
      />
    </div>
  );
};
