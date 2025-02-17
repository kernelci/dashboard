import type { JSX, PropsWithChildren } from 'react';

interface IPageWithTitle extends PropsWithChildren {
  title?: string;
}

const PageWithTitle = ({ title, children }: IPageWithTitle): JSX.Element => (
  <>
    {title && <title>{title}</title>}
    {children}
  </>
);

export default PageWithTitle;
