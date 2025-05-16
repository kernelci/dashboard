import type { ReactNode, JSX } from 'react';
import { FormattedMessage } from 'react-intl';

import type { MessagesKey } from '@/locales/messages';

import {
  Dialog,
  DialogClose,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from '@/components/ui/dialog';
import { Button } from '@/components/ui/button';

interface ActionLinkBase {
  href: string;
  target?: string;
  rel?: string;
  icon?: JSX.Element;
}

interface ActionLinkWithIntl extends ActionLinkBase {
  intlId: MessagesKey;
  label?: never;
}

interface ActionLinkWithLabel extends ActionLinkBase {
  intlId?: never;
  label: string;
}

export type ActionLink = ActionLinkWithIntl | ActionLinkWithLabel;

export interface CustomDialogProps {
  trigger: ReactNode;
  titleIntlId: MessagesKey;
  descriptionIntlId: MessagesKey;
  footerClassName?: string;
  actionLinks?: ActionLink[];
  showCancel?: boolean;
}

export const CustomDialog = ({
  trigger,
  titleIntlId,
  descriptionIntlId,
  footerClassName,
  actionLinks = [],
  showCancel = true,
}: CustomDialogProps): JSX.Element => {
  return (
    <Dialog>
      <DialogTrigger asChild>{trigger}</DialogTrigger>
      <DialogContent>
        <DialogHeader>
          <DialogTitle className="leading-normal tracking-normal">
            <FormattedMessage id={titleIntlId} />
          </DialogTitle>
          <DialogDescription>
            <FormattedMessage id={descriptionIntlId} />
          </DialogDescription>
        </DialogHeader>
        <DialogFooter className={footerClassName}>
          {actionLinks.map((actionLink, index) => (
            <Button key={index} asChild>
              <a
                href={actionLink.href}
                target={actionLink.target ?? '_blank'}
                rel={actionLink.rel ?? 'noreferrer'}
              >
                {actionLink.intlId ? (
                  <FormattedMessage id={actionLink.intlId} />
                ) : (
                  actionLink.label
                )}
                {actionLink.icon}
              </a>
            </Button>
          ))}
          {showCancel && (
            <DialogClose asChild>
              <Button variant={'outline'}>
                <FormattedMessage id="global.cancel" />
              </Button>
            </DialogClose>
          )}
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
};
