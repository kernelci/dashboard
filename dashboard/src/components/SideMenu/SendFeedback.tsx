import { MdOutlineFeedback } from 'react-icons/md';
import { FormattedMessage } from 'react-intl';

import { useEffect, useMemo, useState, type JSX } from 'react';

import { useLocation } from '@tanstack/react-router';

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

const SendFeedback = (
  props: React.ComponentProps<typeof NavigationMenuItem>,
): JSX.Element => {
  const location = useLocation();

  const [fullLocation, setFullLocation] = useState(
    `${window.location.origin}${location.pathname}${location.search}${location.hash}`,
  );

  useEffect(() => {
    const newUrl = `${window.location.origin}${location.pathname}${location.search}${location.hash}`;
    setFullLocation(newUrl);
  }, [location]);

  const github_href = useMemo(() => {
    const github_body = encodeURIComponent(`# Feedback Description:
  
## URL used to send feedback:
${fullLocation}
    `);

    return `${FEEDBACK_ISSUE_URL}&body=${github_body}`;
  }, [fullLocation]);

  const email_href = useMemo(() => {
    const subject = 'Dashboard Feedback';
    const email_body = encodeURIComponent(`Feedback Description:
  
URL used to send feedback:
${fullLocation}
      `);

    return `mailto:${FEEDBACK_EMAIL_TO}?body=${email_body}&subject=${subject}`;
  }, [fullLocation]);

  return (
    <NavigationMenuItem {...props}>
      <AlertDialog>
        <AlertDialogTrigger>
          <NavLink
            asTag="a"
            icon={<MdOutlineFeedback />}
            idIntl="routes.sendFeedback"
          />
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
              <a href={github_href} target="_blank" rel="noreferrer">
                <FormattedMessage id="global.github" />
              </a>
            </AlertDialogAction>
            <AlertDialogAction asChild>
              <a href={email_href} target="_blank" rel="noreferrer">
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
