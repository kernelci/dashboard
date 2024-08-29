import ColoredCircle from '@/components/ColoredCircle/ColoredCircle';

interface ITestStatus {
  pass?: number;
  error?: number;
  miss?: number;
  fail?: number;
  done?: number;
  skip?: number;
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
}: ITestStatus): JSX.Element => {
  return (
    <div className="flex flex-row gap-1">
      <ColoredCircle quantity={pass ?? 0} backgroundClassName="bg-lightGreen" />
      <ColoredCircle quantity={error ?? 0} backgroundClassName="bg-lightRed" />
      <ColoredCircle quantity={miss ?? 0} backgroundClassName="bg-lightGray" />
      <ColoredCircle quantity={fail ?? 0} backgroundClassName="bg-yellow" />
      <ColoredCircle quantity={done ?? 0} backgroundClassName="bg-lightBlue" />
      <ColoredCircle quantity={skip ?? 0} backgroundClassName="bg-mediumGray" />
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
      />
      <ColoredCircle
        quantity={invalid ?? 0}
        backgroundClassName="bg-lightRed"
      />
      <ColoredCircle
        quantity={unknown ?? 0}
        backgroundClassName="bg-lightGray"
      />
    </div>
  );
};
