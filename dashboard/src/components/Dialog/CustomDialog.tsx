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
  titleIntlId?: MessagesKey;
  descriptionIntlId?: MessagesKey;
  content?: ReactNode;
  contentClassName?: string;
  showOverlay?: boolean;
  showCloseButton?: boolean;
  footerClassName?: string;
  actionLinks?: ActionLink[];
  showCancel?: boolean;
}

export const CustomDialog = ({
  trigger,
  titleIntlId,
  descriptionIntlId,
  content,
  contentClassName,
  showOverlay = true,
  showCloseButton = true,
  footerClassName,
  actionLinks = [],
  showCancel = true,
}: CustomDialogProps): JSX.Element => {
  const hasHeader = Boolean(titleIntlId || descriptionIntlId);
  const hasFooter = actionLinks.length > 0 || showCancel;

  return (
    <Dialog>
      <DialogTrigger asChild>{trigger}</DialogTrigger>
      <DialogContent
        className={contentClassName}
        showOverlay={showOverlay}
        showCloseButton={showCloseButton}
      >
        {hasHeader && (
          <DialogHeader>
            {titleIntlId && (
              <DialogTitle className="leading-normal tracking-normal">
                <FormattedMessage id={titleIntlId} />
              </DialogTitle>
            )}
            {descriptionIntlId && (
              <DialogDescription>
                <FormattedMessage id={descriptionIntlId} />
              </DialogDescription>
            )}
          </DialogHeader>
        )}
        {content}
        {hasFooter && (
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
        )}
      </DialogContent>
    </Dialog>
  );
};
