import { MdOutlineFeedback } from 'react-icons/md';

import { useEffect, useMemo, useState, type JSX } from 'react';

import { useLocation } from '@tanstack/react-router';

import { LiaGithub } from 'react-icons/lia';

import { HiOutlineMail } from 'react-icons/hi';

import {
  FEEDBACK_ISSUE_URL,
  FEEDBACK_EMAIL_TO,
} from '@/utils/constants/general';

import { NavigationMenuItem } from '@/components/ui/navigation-menu';

import type { ActionLink } from '@/components/Dialog/CustomDialog';
import { CustomDialog } from '@/components/Dialog/CustomDialog';

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

  const actionLinks: ActionLink[] = useMemo(() => {
    const github_body = encodeURIComponent(
      `# Feedback Description:
  
## URL used to send feedback:
${fullLocation}`,
    );

    const email_subject = 'Dashboard Feedback';
    const email_body = encodeURIComponent(
      `Feedback Description:
  
URL used to send feedback:
${fullLocation}`,
    );

    return [
      {
        href: `${FEEDBACK_ISSUE_URL}&body=${github_body}`,
        label: 'Github',
        icon: <LiaGithub className="ml-2 size-5" />,
      },
      {
        href: `mailto:${FEEDBACK_EMAIL_TO}?body=${email_body}&subject=${email_subject}`,
        intlId: 'global.email',
        icon: <HiOutlineMail className="ml-2 size-5" />,
      },
    ];
  }, [fullLocation]);

  return (
    <NavigationMenuItem {...props}>
      <CustomDialog
        trigger={
          <NavLink
            asTag="a"
            icon={<MdOutlineFeedback />}
            idIntl="sidemenu.sendFeedback"
          />
        }
        titleIntlId="sidemenu.sendFeedback"
        descriptionIntlId="sidemenu.sendFeedbackMsg"
        actionLinks={actionLinks}
      />
    </NavigationMenuItem>
  );
};

export default SendFeedback;
