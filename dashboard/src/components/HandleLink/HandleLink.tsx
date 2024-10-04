import { LinkComponentProps } from 'node_modules/@tanstack/react-router/dist/esm/link';
import React, { PropsWithChildren, useEffect, useRef, useState } from 'react';
import { Link } from '@tanstack/react-router';

const HandleLink: React.FC<PropsWithChildren<LinkComponentProps<'a'>>> = ({
  children,
  ...props
}) => {
  const [linkTarget, setLinkTarget] = useState<string | undefined>(undefined);
  const linkRef = useRef<HTMLAnchorElement>(null);

  useEffect(() => {
    if (linkTarget) {
      setLinkTarget(undefined);
      linkRef.current?.click();
    }
  }, [linkTarget]);

  return (
    <Link
      {...props}
      ref={linkRef}
      target={linkTarget}
      onContextMenu={e => {
        e.preventDefault();
        setLinkTarget('_blank');
      }}
    >
      {children}
    </Link>
  );
};

export default HandleLink;
