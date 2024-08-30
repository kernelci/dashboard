import ColoredCircle from '@/components/ColoredCircle/ColoredCircle';

interface ITestStatus {
  pass?: number;
  error?: number;
  miss?: number;
  fail?: number;
  done?: number;
  skip?: number;
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
      {(forceNumber || pass) && (
        <ColoredCircle
          quantity={pass ?? 0}
          tooltipText="global.pass"
          backgroundClassName="bg-lightGreen"
        />
      )}
      {(forceNumber || error) && (
        <ColoredCircle
          quantity={error ?? 0}
          tooltipText="global.error"
          backgroundClassName="bg-lightRed"
        />
      )}
      {(forceNumber || miss) && (
        <ColoredCircle
          quantity={miss ?? 0}
          tooltipText="global.missed"
          backgroundClassName="bg-lightGray"
        />
      )}
      {(forceNumber || fail) && (
        <ColoredCircle
          quantity={fail ?? 0}
          tooltipText="global.failed"
          backgroundClassName="bg-yellow"
        />
      )}
      {(forceNumber || done) && (
        <ColoredCircle
          quantity={done ?? 0}
          tooltipText="global.done"
          backgroundClassName="bg-lightBlue"
        />
      )}
      {(forceNumber || done) && (
        <ColoredCircle
          quantity={skip ?? 0}
          tooltipText="global.skipped"
          backgroundClassName="bg-mediumGray"
        />
      )}
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
        tooltipText="global.valid"
      />
      <ColoredCircle
        quantity={invalid ?? 0}
        backgroundClassName="bg-lightRed"
        tooltipText="global.invalid"
      />
      <ColoredCircle
        quantity={unknown ?? 0}
        tooltipText="global.unknown"
        backgroundClassName="bg-lightGray"
      />
    </div>
  );
};
