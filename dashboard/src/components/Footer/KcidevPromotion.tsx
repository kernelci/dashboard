import type { JSX } from 'react';

import { TbTerminal2 } from 'react-icons/tb';

import NavLink from '@/components/SideMenu/NavLink';

/** A documentation-area link that introduces users to the kci-dev CLI. */
export const KcidevPromotion = ({
  onLinkClick,
}: {
  onLinkClick?: () => void;
}): JSX.Element => (
  <NavLink
    asTag="a"
    href="https://kci.dev"
    icon={<TbTerminal2 className="size-5" />}
    idIntl="footer.promotionLabel"
    onClickElement={onLinkClick}
    target="_blank"
  />
);
