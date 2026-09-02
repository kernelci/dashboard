import { Link } from '@tanstack/react-router';

import { FormattedMessage } from 'react-intl';

import type { JSX } from 'react';

import {
  LF_PRIVACY_POLICY_URL,
  LF_PROJECTS_POLICIES_URL,
} from '@/utils/constants/general';

const externalLinkClassName = 'text-dark-blue underline';

export const SiteFooter = (): JSX.Element => {
  return (
    <footer className="mt-8 border-t border-gray-300 pt-4 pb-2 text-center text-sm text-gray-600">
      <p>
        <FormattedMessage
          id="footer.privacyNotice"
          values={{
            dashboardPrivacyLink: (
              <Link to="/privacy" className={externalLinkClassName}>
                <FormattedMessage id="global.privacy" />
              </Link>
            ),
            lfPrivacyLink: (
              <a
                href={LF_PRIVACY_POLICY_URL}
                className={externalLinkClassName}
                target="_blank"
                rel="noreferrer"
              >
                <FormattedMessage id="global.lfPrivacyPolicy" />
              </a>
            ),
          }}
        />
      </p>
      <p className="mt-2 text-xs text-gray-500">
        <FormattedMessage
          id="footer.lfPolicies"
          values={{
            lfPoliciesLink: (
              <a
                href={LF_PROJECTS_POLICIES_URL}
                className={externalLinkClassName}
                target="_blank"
                rel="noreferrer"
              >
                lfprojects.org/policies
              </a>
            ),
          }}
        />
      </p>
    </footer>
  );
};
