import type { JSX } from 'react';
import { FormattedMessage, useIntl } from 'react-intl';

import { ChevronRightAnimate } from '@/components/AnimatedIcons/Chevron';
import { Badge } from '@/components/ui/badge';
import LinkWithIcon from '@/components/LinkWithIcon/LinkWithIcon';
import Section from '@/components/Section/Section';
import { TooltipDateTime } from '@/components/TooltipDateTime';
import { TreeDetailsLink } from '@/components/TreeDetailsLink/TreeDetailsLink';
import {
  Collapsible,
  CollapsibleContent,
  CollapsibleTrigger,
} from '@/components/ui/collapsible';

import { valueOrEmpty } from '@/lib/string';

import type { MessagesKey } from '@/locales/messages';
import type {
  Checkout,
  Incident,
  NextCheckout,
  TreeSeenData,
} from '@/types/issueExtras';

type SeenData = Incident | Checkout | NextCheckout;

const sameTree = (a: SeenData, b: SeenData): boolean =>
  a.tree_name === b.tree_name &&
  a.git_repository_branch === b.git_repository_branch;

const SeenColumn = ({
  label,
  data,
  time,
  version,
  emptyLabel,
  showTree = false,
}: {
  label: MessagesKey;
  data?: SeenData;
  time?: Date;
  version?: string;
  emptyLabel?: MessagesKey;
  showTree?: boolean;
}): JSX.Element => (
  <div className="flex min-w-0 flex-col items-start gap-1">
    <div className="flex flex-wrap items-center gap-x-2 gap-y-1">
      <span className="font-bold">
        <FormattedMessage id={label} />
      </span>
      {version && (
        <Badge variant="secondary" className="px-1.5 py-0 font-normal">
          <FormattedMessage
            id="issueDetails.versionNumber"
            values={{ versionNumber: version }}
          />
        </Badge>
      )}
      {time && (
        <span className="text-dark-gray2 text-sm whitespace-nowrap">
          <TooltipDateTime dateTime={time} lineBreak={false} showRelative />
        </span>
      )}
    </div>
    {data ? (
      <>
        <div className="flex w-full min-w-0 flex-wrap items-center gap-x-2 gap-y-1">
          <TreeDetailsLink
            className="inline-flex max-w-full min-w-0 items-center gap-1 text-sm [&_svg]:shrink-0"
            treeName={data.tree_name}
            gitBranch={data.git_repository_branch}
            commitHash={data.git_commit_hash}
            gitUrl={data.git_repository_url}
            commitName={data.git_commit_name}
            showFullLabel={showTree}
          />
          {data.git_commit_name && (
            <Badge
              variant="blueTag"
              className="max-w-full font-normal whitespace-normal normal-case"
            >
              {data.git_commit_name}
            </Badge>
          )}
        </div>
      </>
    ) : (
      emptyLabel && (
        <span className="text-dark-gray2 text-sm">
          <FormattedMessage id={emptyLabel} />
        </span>
      )
    )}
  </div>
);

const TreeIncidents = ({
  tree,
  nextCheckout,
}: {
  tree: TreeSeenData;
  nextCheckout?: NextCheckout | null;
}): JSX.Element => {
  const last = tree.last_incident;
  const checkout = tree.first_good_checkout;
  const next =
    nextCheckout && sameTree(nextCheckout, last) ? nextCheckout : undefined;
  const repositoryUrl = last.git_repository_url;

  return (
    <Collapsible className="group border-dark-gray border-t py-2">
      <CollapsibleTrigger className="flex w-full items-center gap-2 text-left">
        <ChevronRightAnimate className="shrink-0" />
        <span className="min-w-0 font-semibold break-words">
          {`${valueOrEmpty(last.tree_name)} / ${valueOrEmpty(last.git_repository_branch)}`}
        </span>
      </CollapsibleTrigger>
      <CollapsibleContent className="flex flex-col gap-3 pt-2">
        {repositoryUrl && (
          <LinkWithIcon
            title="commonDetails.gitRepositoryUrl"
            link={repositoryUrl}
            linkText={repositoryUrl}
            titleClassName="text-dark-gray2 text-xs font-normal"
          />
        )}
        <div className="grid grid-cols-1 gap-x-6 gap-y-3 sm:grid-cols-2 xl:grid-cols-4 [&_svg]:h-4 [&_svg]:w-4">
          <SeenColumn
            label="issue.firstSeen"
            data={tree.first_incident}
            time={tree.first_incident.first_seen}
            version={tree.first_incident.issue_version}
          />
          <SeenColumn
            label="issue.lastSeen"
            data={last}
            time={last.first_seen}
            version={last.issue_version}
          />
          <SeenColumn
            label="issueDetails.firstGoodCheckout"
            data={checkout}
            time={checkout?.start_time}
            emptyLabel="issueDetails.stillFailing"
          />
          {next && (
            <SeenColumn
              label="issueDetails.nextCheckout"
              data={next}
              time={next.start_time}
            />
          )}
        </div>
      </CollapsibleContent>
    </Collapsible>
  );
};

const SummaryIncidents = ({
  firstIncident,
  lastIncident,
  nextCheckout,
}: {
  firstIncident?: Incident;
  lastIncident?: Incident;
  nextCheckout?: NextCheckout | null;
}): JSX.Element => (
  <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 xl:grid-cols-3">
    {firstIncident && (
      <SeenColumn
        label="issueDetails.firstIncidentData"
        data={firstIncident}
        time={firstIncident.first_seen}
        version={firstIncident.issue_version}
        showTree
      />
    )}
    {lastIncident && (
      <SeenColumn
        label="issueDetails.lastIncident"
        data={lastIncident}
        time={lastIncident.first_seen}
        version={lastIncident.issue_version}
        showTree
      />
    )}
    {nextCheckout && (
      <SeenColumn
        label="issueDetails.nextCheckout"
        data={nextCheckout}
        time={nextCheckout.start_time}
      />
    )}
  </div>
);

export const IncidentsSection = ({
  firstIncident,
  lastIncident,
  nextCheckout,
  perTree,
  card = false,
}: {
  firstIncident?: Incident;
  lastIncident?: Incident;
  nextCheckout?: NextCheckout | null;
  perTree?: TreeSeenData[];
  card?: boolean;
}): JSX.Element | undefined => {
  const { formatMessage } = useIntl();
  const unmatchedNext =
    nextCheckout &&
    !perTree?.some(tree => sameTree(nextCheckout, tree.last_incident))
      ? nextCheckout
      : undefined;

  if (!perTree?.length && !firstIncident && !lastIncident && !nextCheckout) {
    return;
  }

  return (
    <Section
      card={card}
      title={formatMessage({ id: 'issueDetails.incidentsTitle' })}
      subsections={[
        {
          infos: [
            {
              children: perTree?.length ? (
                <div className="flex flex-col gap-3">
                  {(firstIncident || lastIncident) && (
                    <SummaryIncidents
                      firstIncident={firstIncident}
                      lastIncident={lastIncident}
                    />
                  )}
                  <div className="[&>:first-child]:border-t-0 [&>:first-child]:pt-0">
                    {perTree.map(tree => (
                      <TreeIncidents
                        key={`${tree.last_incident.tree_name}-${tree.last_incident.git_repository_branch}-${tree.last_incident.git_repository_url}`}
                        tree={tree}
                        nextCheckout={nextCheckout}
                      />
                    ))}
                  </div>
                  {unmatchedNext && (
                    <SummaryIncidents nextCheckout={unmatchedNext} />
                  )}
                </div>
              ) : (
                <SummaryIncidents
                  firstIncident={firstIncident}
                  lastIncident={lastIncident}
                  nextCheckout={nextCheckout}
                />
              ),
            },
          ],
        },
      ]}
    />
  );
};
