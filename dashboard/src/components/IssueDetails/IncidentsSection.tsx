import type { JSX } from 'react';
import { FormattedMessage } from 'react-intl';

import { ChevronRightAnimate } from '@/components/AnimatedIcons/Chevron';
import LinkWithIcon from '@/components/LinkWithIcon/LinkWithIcon';
import { TooltipDateTime } from '@/components/TooltipDateTime';
import { TreeDetailsLink } from '@/components/TreeDetailsLink/TreeDetailsLink';
import {
  Collapsible,
  CollapsibleContent,
  CollapsibleTrigger,
} from '@/components/ui/collapsible';

import { valueOrEmpty } from '@/lib/string';

import type { MessagesKey } from '@/locales/messages';
import type { Checkout, Incident, TreeSeenData } from '@/types/issueExtras';

const CheckoutCell = ({
  title,
  data,
  time,
  version,
}: {
  title: MessagesKey;
  data: Incident | Checkout;
  time: Date;
  version?: string;
}): JSX.Element => (
  <div className="flex min-w-0 flex-col gap-2 text-sm">
    <div className="flex flex-col gap-0.5">
      <span className="font-bold">
        <FormattedMessage id={title} />
      </span>
      <TreeDetailsLink
        treeName={data.tree_name}
        gitBranch={data.git_repository_branch}
        commitHash={data.git_commit_hash}
        gitUrl={data.git_repository_url}
        commitName={data.git_commit_name}
      />
      <span className="text-dark-gray2">
        <TooltipDateTime dateTime={time} showRelative={true} />
      </span>
    </div>
    <LinkWithIcon
      className="text-sm"
      title="commonDetails.gitCommitName"
      linkText={valueOrEmpty(data.git_commit_name)}
    />
    {version !== undefined && (
      <LinkWithIcon
        className="text-sm"
        title="issueDetails.firstIncidentVersion"
        linkText={valueOrEmpty(version)}
      />
    )}
  </div>
);

const treeTitle = (tree: TreeSeenData): string => {
  const name = valueOrEmpty(tree.last_incident.tree_name);
  const branch = valueOrEmpty(tree.last_incident.git_repository_branch);
  return `${name} / ${branch}`;
};

const TreeIncidentCollapsible = ({
  tree,
}: {
  tree: TreeSeenData;
}): JSX.Element => {
  const checkout = tree.first_good_checkout;

  return (
    <Collapsible className="group border-dark-gray border-t">
      <CollapsibleTrigger className="flex w-full items-center gap-2 py-2 text-left">
        <ChevronRightAnimate className="shrink-0" />
        <span className="max-w-full font-bold break-all">
          {treeTitle(tree)}
        </span>
      </CollapsibleTrigger>
      <CollapsibleContent>
        <div className="grid grid-cols-1 gap-x-6 gap-y-3 pb-3 md:grid-cols-3">
          <CheckoutCell
            title="issue.firstSeen"
            data={tree.first_incident}
            time={tree.first_incident.first_seen}
            version={tree.first_incident.issue_version}
          />
          <CheckoutCell
            title="issue.lastSeen"
            data={tree.last_incident}
            time={tree.last_incident.first_seen}
            version={tree.last_incident.issue_version}
          />
          {checkout ? (
            <CheckoutCell
              title="issueDetails.firstGoodCheckout"
              data={checkout}
              time={checkout.start_time}
            />
          ) : (
            <div className="flex min-w-0 flex-col gap-0.5 text-sm">
              <span className="font-bold">
                <FormattedMessage id="issueDetails.firstGoodCheckout" />
              </span>
              <FormattedMessage id="issueDetails.stillFailing" />
            </div>
          )}
        </div>
      </CollapsibleContent>
    </Collapsible>
  );
};

export const IncidentsSection = ({
  perTree,
}: {
  perTree?: TreeSeenData[];
}): JSX.Element | undefined => {
  if (!perTree || perTree.length === 0) {
    return;
  }

  return (
    <div className="text-dim-gray mb-4 flex flex-col">
      <span className="mb-1 text-xl font-bold">
        <FormattedMessage id="issueDetails.incidents" />
      </span>
      {perTree.map(tree => (
        <TreeIncidentCollapsible
          key={`${tree.last_incident.tree_name}-${tree.last_incident.git_repository_branch}-${tree.last_incident.git_repository_url}`}
          tree={tree}
        />
      ))}
    </div>
  );
};
