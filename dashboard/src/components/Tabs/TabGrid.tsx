import { type ReactNode, type JSX, memo } from 'react';

type GridProps = {
  children: ReactNode;
};

const MobileGrid = ({ children }: GridProps): JSX.Element => (
  <div className="min-[1652px]:none">{children}</div>
);

const InnerMobileGrid = ({ children }: GridProps): JSX.Element => (
  <div className="grid grid-cols-1 lg:grid-cols-2 lg:gap-x-8">{children}</div>
);

const DesktopGrid = ({ children }: GridProps): JSX.Element => (
  <div className="none grid-cols-2 gap-4 min-[1652px]:grid">{children}</div>
);

const ResponsiveDetailsGrid = ({
  topCards,
  bodyCards,
  footerCards,
}: {
  topCards: JSX.Element[];
  bodyCards: JSX.Element[];
  footerCards: JSX.Element[];
}): JSX.Element => {
  /**
   * Top level grid for responsiveness in the tree/hardware details pages.
   * The topCards will be shown at the top of both columns in large format and have priority in the middle format.
   * The footerCards will be shown at the bottom and always spanning 2 columns.
   */

  const midIndex = Math.ceil(topCards.length / 2);
  const leftTopCards = topCards.slice(0, midIndex);
  const rightTopCards = topCards.slice(midIndex);

  const midBodyIndex = Math.ceil(bodyCards.length / 2);
  const leftBodyCards = bodyCards.slice(0, midBodyIndex);
  const rightBodyCards = bodyCards.slice(midBodyIndex);

  return (
    <>
      <DesktopGrid>
        <div>
          {leftTopCards}
          {leftBodyCards}
        </div>
        <div>
          {rightTopCards}
          {rightBodyCards}
        </div>
        <div className="col-span-2">{footerCards}</div>
      </DesktopGrid>
      <MobileGrid>
        {topCards}
        <InnerMobileGrid>
          <div>{leftBodyCards}</div>
          <div>{rightBodyCards}</div>
        </InnerMobileGrid>
        {footerCards}
      </MobileGrid>
    </>
  );
};

export const MemoizedResponsiveDetailsCards = memo(ResponsiveDetailsGrid);
