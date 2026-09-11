import { FormattedMessage, useIntl } from 'react-intl';

import type { ErrorComponentProps } from '@tanstack/react-router';

import type { JSX } from 'react';

import { Button } from '@/components/ui/button';
import {
  FEEDBACK_EMAIL_TO,
  GITHUB_ISSUES_URL,
} from '@/utils/constants/general';

const REACT_QUERY_CACHE_KEY = 'REACT_QUERY_OFFLINE_CACHE';

const clearPersistedQueryCache = (): void => {
  window.sessionStorage.removeItem(REACT_QUERY_CACHE_KEY);
  window.localStorage.removeItem(REACT_QUERY_CACHE_KEY);
  window.location.reload();
};

const RouteError = ({ error }: ErrorComponentProps): JSX.Element => {
  const { formatMessage } = useIntl();

  const errorMessage = error instanceof Error ? error.message : String(error);

  const reportLinks = {
    emailLink: (
      <a href={`mailto:${FEEDBACK_EMAIL_TO}`} className="underline">
        {FEEDBACK_EMAIL_TO}
      </a>
    ),
    gitHubLink: (
      <a
        href={GITHUB_ISSUES_URL}
        target="_blank"
        rel="noreferrer"
        className="underline"
      >
        {formatMessage({ id: 'global.gitHubIssue' })}
      </a>
    ),
  };

  return (
    <div className="flex h-screen flex-col items-center justify-center px-4 py-8">
      <div className="flex max-w-2xl flex-col items-center space-y-8 text-center">
        <h1 className="text-4xl font-bold">
          <FormattedMessage id="global.somethingWrong" />
        </h1>
        <div className="space-y-3 text-xl leading-relaxed">
          <p>
            <FormattedMessage id="global.unexpectedErrorReportIntro" />
          </p>
          <p>
            <FormattedMessage
              id="global.unexpectedErrorReportAction"
              values={reportLinks}
            />
          </p>
        </div>
        {errorMessage && (
          <pre className="max-w-2xl overflow-auto rounded border border-red-300 p-3 text-left text-xs text-red-600">
            <code>{errorMessage}</code>
          </pre>
        )}
        <Button onClick={clearPersistedQueryCache}>
          <FormattedMessage id="global.reloadAndClearCache" />
        </Button>
      </div>
    </div>
  );
};

export default RouteError;
