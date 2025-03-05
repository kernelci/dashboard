import type { JSX } from 'react';

export const OpenGraphTags = ({
  title,
  url,
  description,
  imageUrl = 'https://dashboard.kernelci.org/kernelCI_logo-card.png',
  type = 'website',
}: {
  title: string;
  url?: string;
  description: string;
  imageUrl?: string;
  type?: string;
}): JSX.Element => {
  return (
    <>
      <meta property="og:title" content={title} />
      <meta property="og:url" content={url ?? window.location.href} />
      <meta property="og:description" content={description} />
      <meta property="og:image" content={imageUrl} />
      <meta property="og:type" content={type} />
      <meta property="twitter:title" content={title} />
      <meta property="twitter:site" content={url ?? window.location.href} />
      <meta property="twitter:description" content={description} />
      <meta property="twitter:image" content={imageUrl} />
    </>
  );
};
