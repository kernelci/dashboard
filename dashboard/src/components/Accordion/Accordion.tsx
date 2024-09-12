import { ReactElement, useCallback, useMemo } from 'react';

import { MdCheck, MdClose, MdChevronRight } from 'react-icons/md';

import { FormattedMessage } from 'react-intl';

import { useNavigate } from '@tanstack/react-router';

import { AccordionItemBuilds } from '@/types/tree/TreeDetails';

import { TIndividualTest, TPathTests } from '@/types/general';

import ColoredCircle from '@/components/ColoredCircle/ColoredCircle';

import { ItemType } from '@/components/ListingItem/ListingItem';

import { GroupedTestStatus } from '@/components/Status/Status';

import HeaderWithInfo from '@/pages/TreeDetails/Tabs/HeaderWithInfo';

import { TableBody, TableCell, TableRow } from '@/components/ui/table';

import BaseTable from '@/components/Table/BaseTable';

import {
  Collapsible,
  CollapsibleContent,
  CollapsibleTrigger,
} from '@/components/ui/collapsible';

import AccordionBuildContent from './BuildAccordionContent';

export interface IAccordion {
  headers?: ReactElement[];
  items: AccordionItemBuilds[] | TPathTests[];
  type: 'build' | 'test';
}

export interface IAccordionItems {
  accordionData: AccordionItemBuilds | TPathTests;
}

interface ICustomAccordionTableBody {
  items: AccordionItemBuilds[] | TPathTests[];
  type: 'build' | 'test';
}

interface IAccordionTestContent {
  data: TIndividualTest[];
}

const headersBuilds = [
  <FormattedMessage key="treeDetails.config" id="treeDetails.config" />,
  <FormattedMessage key="treeDetails.compiler" id="treeDetails.compiler" />,
  <FormattedMessage key="treeDetails.date" id="treeDetails.date" />,
  <FormattedMessage
    key="treeDetails.buildErrors"
    id="treeDetails.buildErrors"
  />,
  <FormattedMessage key="treeDetails.buildTime" id="treeDetails.buildTime" />,
  <HeaderWithInfo
    key="treeDetails.status"
    labelId="treeDetails.status"
    tooltipId="buildTab.statusTooltip"
  />,
];

const headersTests = [
  <FormattedMessage key="testDetails.path" id="testDetails.path" />,
  <HeaderWithInfo
    key="treeDetails.status"
    labelId="testDetails.status"
    tooltipId="testsTab.statusTooltip"
  />,
  <span key="chevron"></span>, //empty cell to add the chevron
];

const headerTestsDetails = [
  <FormattedMessage key="testDetails.path" id="testDetails.path" />,
  <FormattedMessage key="testDetails.status" id="testDetails.status" />,
  <FormattedMessage key="global.date" id="global.date" />,
  <FormattedMessage key="treeDetails.duration" id="testDetails.duration" />,
  <span key="chevron2"></span>, //extra one to add the chevron icon
];

const Accordion = ({ items, type }: IAccordion): JSX.Element => {
  const accordionTableHeader = type === 'build' ? headersBuilds : headersTests;

  return (
    <BaseTable
      headers={accordionTableHeader}
      body={<AccordionTableBody items={items} type={type} />}
    />
  );
};

const ChevronRightAnimate = (): JSX.Element => {
  return (
    <MdChevronRight className="transition group-data-[state='open']:rotate-90" />
  );
};

const AccordionTableBody = ({
  items,
  type,
}: ICustomAccordionTableBody): JSX.Element => {
  const accordionItems = useMemo(() => {
    if (items.length === 0) {
      return (
        <div className="flex h-8 items-center px-4">
          <FormattedMessage id="global.noResults" />
        </div>
      );
    }
    return items.map(item => {
      const itemKey =
        type === 'build'
          ? (item as AccordionItemBuilds).id
          : (item as TPathTests).path_group;
      return (
        <Collapsible key={itemKey} asChild>
          <>
            <CollapsibleTrigger asChild>
              <TableRow className="group cursor-pointer hover:bg-lightBlue">
                {type === 'build' ? (
                  <AccordionBuildsTrigger accordionData={item} />
                ) : (
                  <AccordionTestsTrigger accordionData={item} />
                )}
              </TableRow>
            </CollapsibleTrigger>
            <TableRow>
              <TableCell colSpan={6} className="p-0">
                <CollapsibleContent>
                  <div className="group max-h-[400px] w-full overflow-scroll border-b border-darkGray bg-lightGray p-8">
                    {type === 'build' ? (
                      <AccordionBuildContent accordionData={item} />
                    ) : (
                      <AccordionTestsContent
                        data={(item as TPathTests).individual_tests}
                      />
                    )}
                  </div>
                </CollapsibleContent>
              </TableCell>
            </TableRow>
          </>
        </Collapsible>
      );
    });
  }, [items, type]);

  return <TableBody>{accordionItems}</TableBody>;
};

const AccordionBuildsTrigger = ({
  accordionData,
}: IAccordionItems): JSX.Element => {
  const triggerInfo = accordionData as AccordionItemBuilds;
  const buildErrors = triggerInfo.buildErrors ?? 0;
  const isBuildValid = triggerInfo.status === 'valid';
  const isBuildInvalid = triggerInfo.status === 'invalid';
  const isBuildUnknown = triggerInfo.status === 'null';
  return (
    <>
      <TableCell>{triggerInfo.config}</TableCell>
      <TableCell>{triggerInfo.compiler}</TableCell>
      <TableCell>{triggerInfo.date}</TableCell>
      <TableCell>
        <ColoredCircle
          className="max-w-6"
          quantity={buildErrors}
          backgroundClassName={buildErrors > 0 ? ItemType.Error : ItemType.None}
        />
      </TableCell>
      <TableCell>{triggerInfo.buildTime}</TableCell>
      <TableCell>
        {isBuildValid && <MdCheck className="text-green" />}
        {isBuildInvalid && <MdClose className="text-red" />}
        {isBuildUnknown && <span>-</span>}
      </TableCell>
    </>
  );
};

const AccordionTestsTrigger = ({
  accordionData,
}: IAccordionItems): JSX.Element => {
  const triggerInfo = accordionData as TPathTests;
  return (
    <>
      <TableCell>{triggerInfo.path_group}</TableCell>
      <TableCell className="flex flex-row gap-1">
        <GroupedTestStatus
          pass={triggerInfo.pass_tests}
          done={triggerInfo.done_tests}
          miss={triggerInfo.miss_tests}
          fail={triggerInfo.fail_tests}
          skip={triggerInfo.skip_tests}
          error={triggerInfo.error_tests}
        />
      </TableCell>
      <TableCell>
        <ChevronRightAnimate />
      </TableCell>
    </>
  );
};

const AccordionTestsContent = ({
  data,
}: IAccordionTestContent): JSX.Element => {
  const navigate = useNavigate({ from: '/tree/$treeId' });

  const onClickName = useCallback(
    (e: React.MouseEvent<HTMLTableRowElement>) => {
      const newTestPath = e.currentTarget.querySelector(
        'td:first-child',
      ) as HTMLTableCellElement;
      if (newTestPath) {
        navigate({
          to: '/tree/$treeId/test/$testId',
          params: {
            testId: newTestPath.innerText,
          },
          search: s => s,
        });
      }
    },
    [navigate],
  );

  const rows = useMemo(() => {
    return data.map(test => (
      <TableRow
        className="cursor-pointer hover:bg-lightBlue"
        onClick={onClickName}
        key={test.id}
      >
        <TableCell>{test.path}</TableCell>
        <TableCell>{test.status}</TableCell>
        <TableCell>{test.start_time ?? '-'}</TableCell>
        <TableCell>{test.duration ?? '-'}</TableCell>
        <TableCell>
          <ChevronRightAnimate />
        </TableCell>
      </TableRow>
    ));
  }, [data, onClickName]);

  return (
    <div className="h-max-12 overflow-scroll">
      <BaseTable headers={headerTestsDetails}>
        <TableBody>{rows}</TableBody>
      </BaseTable>
    </div>
  );
};

export default Accordion;
