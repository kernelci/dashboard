import type { ReactNode, JSX } from 'react';

type GridProps = {
  children: ReactNode;
};
export const MobileGrid = ({ children }: GridProps): JSX.Element => (
  <div className="min-[1652px]:hidden">{children}</div>
);

export const InnerMobileGrid = ({ children }: GridProps): JSX.Element => (
  <div className="grid grid-cols-1 lg:grid-cols-2 lg:gap-x-8">{children}</div>
);

export const DesktopGrid = ({ children }: GridProps): JSX.Element => (
  <div className="hidden grid-cols-2 gap-4 min-[1652px]:grid">{children}</div>
);
