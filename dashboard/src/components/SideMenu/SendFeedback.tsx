import { MdOutlineFeedback } from 'react-icons/md';
import { FormattedMessage } from 'react-intl';

import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
  AlertDialogTrigger,
} from '@/components/ui/alert-dialog';

import {
  FEEDBACK_ISSUE_URL,
  FEEDBACK_EMAIL_TO,
} from '@/utils/constants/general';

import { NavigationMenuItem } from '@/components/ui/navigation-menu';

import NavLink from './NavLink';

const get_github_body = (): string =>
  encodeURIComponent(`# Feedback Description:

## URL used to send feedback:
${window.location.href}
`);

const get_email_body = (): string =>
  encodeURIComponent(`Feedback Description:

URL used to send feedback:
${window.location.href}
`);

const onGitHubClick = (): void => {
  window.open(`${FEEDBACK_ISSUE_URL}&body=${get_github_body()}`, '_blank');
};

const onEmailClick = (): void => {
  const subject = 'Dashboard Feedback';
  window.open(
    `mailto:${FEEDBACK_EMAIL_TO}?body=${get_email_body()}&subject=${subject}`,
    '_blank',
  );
};

const SendFeedback = (
  props: React.ComponentProps<typeof NavigationMenuItem>,
): JSX.Element => {
  return (
    <NavigationMenuItem {...props}>
      <AlertDialog>
        <AlertDialogTrigger>
          <NavLink icon={<MdOutlineFeedback />} idIntl="routes.sendFeedback" />
        </AlertDialogTrigger>
        <AlertDialogContent>
          <AlertDialogHeader>
            <AlertDialogTitle>
              <FormattedMessage id="routes.sendFeedback" />
            </AlertDialogTitle>
            <AlertDialogDescription>
              <FormattedMessage id="routes.sendFeedbackMsg" />
            </AlertDialogDescription>
          </AlertDialogHeader>
          <AlertDialogFooter>
            <AlertDialogAction asChild>
              <a onClick={onGitHubClick}>
                <FormattedMessage id="global.github" />
              </a>
            </AlertDialogAction>
            <AlertDialogAction asChild>
              <a onClick={onEmailClick}>
                <FormattedMessage id="global.email" />
              </a>
            </AlertDialogAction>
            <AlertDialogCancel>
              <FormattedMessage id="global.cancel" />
            </AlertDialogCancel>
          </AlertDialogFooter>
        </AlertDialogContent>
      </AlertDialog>
    </NavigationMenuItem>
  );
};

export default SendFeedback;
