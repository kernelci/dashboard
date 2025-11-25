import { type JSX, memo } from 'react';

/**
 * Top level grid for responsiveness in the tree/hardware details pages.
 * The topCards will be shown at the top of both columns in large format and have priority in the middle format.
 * The footerCards will be shown at the bottom and always spanning 2 columns.
 */
const ResponsiveDetailsGrid = ({
  topCards,
  bodyCards,
  footerCards,
}: {
  topCards: JSX.Element[];
  bodyCards: JSX.Element[];
  footerCards: JSX.Element[];
}): JSX.Element => {
  const midIndex = Math.ceil(topCards.length / 2);
  const leftTopCards = topCards.slice(0, midIndex);
  const rightTopCards = topCards.slice(midIndex);

  const midBodyIndex = Math.floor(bodyCards.length / 2);
  const leftBodyCards = bodyCards.slice(0, midBodyIndex);
  const rightBodyCards = bodyCards.slice(midBodyIndex);

  return (
    <>
      <div className="hidden grid-cols-2 gap-4 2xl:grid">
        <div>
          {leftTopCards}
          {leftBodyCards}
        </div>
        <div>
          {rightTopCards}
          {rightBodyCards}
        </div>
        <div className="col-span-2">{footerCards}</div>
      </div>
      <div className="2xl:hidden">
        {topCards}
        <div className="grid grid-cols-1 lg:grid-cols-2 lg:gap-x-8">
          <div>{leftBodyCards}</div>
          <div>{rightBodyCards}</div>
        </div>
        {footerCards}
      </div>
    </>
  );
};

export const MemoizedResponsiveDetailsCards = memo(ResponsiveDetailsGrid);
