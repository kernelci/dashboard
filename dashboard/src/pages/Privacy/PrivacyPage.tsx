import { useIntl } from 'react-intl';
import ReactMarkdown from 'react-markdown';
import type { Components } from 'react-markdown';

import type { JSX } from 'react';

import privacyMarkdown from '@privacy-policy?raw';

import { resolvePolicyUrl } from '@/utils/privacyPolicy';

const externalLinkProps = (
  href: string | undefined,
): { target: '_blank'; rel: 'noreferrer' } | undefined => {
  if (!href?.startsWith('http') && !href?.startsWith('mailto')) {
    return undefined;
  }

  return { target: '_blank', rel: 'noreferrer' };
};

const markdownComponents: Components = {
  h1: ({ children }) => <h1 className="mb-6 text-3xl font-bold">{children}</h1>,
  h2: ({ children }) => (
    <h2 className="mt-8 mb-3 text-xl font-semibold">{children}</h2>
  ),
  p: ({ children }) => <p className="mb-4 leading-relaxed">{children}</p>,
  ul: ({ children }) => (
    <ul className="mb-4 list-disc space-y-1 pl-6">{children}</ul>
  ),
  ol: ({ children }) => (
    <ol className="mb-4 list-decimal space-y-1 pl-6">{children}</ol>
  ),
  li: ({ children }) => <li className="mb-1">{children}</li>,
  blockquote: ({ children }) => (
    <blockquote className="mb-4 border-l-4 border-gray-300 pl-4 text-gray-700">
      {children}
    </blockquote>
  ),
  a: ({ href, children }) => {
    const resolvedHref = href ? resolvePolicyUrl(href) : undefined;

    return (
      <a
        href={resolvedHref}
        className="text-dark-blue underline"
        {...externalLinkProps(resolvedHref)}
      >
        {children}
      </a>
    );
  },
};

export const PrivacyPage = (): JSX.Element => {
  const { formatMessage } = useIntl();

  return (
    <>
      <title>{formatMessage({ id: 'privacy.title' })}</title>
      <div className="mx-auto max-w-3xl rounded-lg bg-white p-8 text-gray-900 shadow-sm">
        <ReactMarkdown components={markdownComponents}>
          {privacyMarkdown}
        </ReactMarkdown>
      </div>
    </>
  );
};
