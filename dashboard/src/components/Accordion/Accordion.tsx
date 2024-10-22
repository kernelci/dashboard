import { ReactElement, useCallback, useMemo } from 'react';

import { FormattedMessage } from 'react-intl';

import { LinkProps } from '@tanstack/react-router';

import { useNavigate } from '@tanstack/react-router';

import {
  AccordionItemBuilds,
  AccordionItemBuildsKeys,
} from '@/types/tree/TreeDetails';

import { TPathTests } from '@/types/general';

import ColoredCircle from '@/components/ColoredCircle/ColoredCircle';

import { ItemType } from '@/components/ListingItem/ListingItem';

import { GroupedTestStatus } from '@/components/Status/Status';

import HeaderWithInfo from '@/pages/TreeDetails/Tabs/HeaderWithInfo';

import {
  TableBody,
  TableCell,
  TableCellWithLink,
  TableRow,
} from '@/components/ui/table';

import BaseTable from '@/components/Table/BaseTable';

import {
  Collapsible,
  CollapsibleContent,
  CollapsibleTrigger,
} from '@/components/ui/collapsible';

import { TooltipDateTime } from '@/components/TooltipDateTime';

import { ChevronRightAnimate } from '@/components/ui/chevron';

import { IndividualTestsTable } from '../NewTables/IndividualTestsTable';

import AccordionBuildContent from './BuildAccordionContent';

export interface IAccordion {
  headers?: ReactElement[];
  items: AccordionItemBuilds[] | TPathTests[];
  type: 'build' | 'test';
  headerOnClick?: (what: AccordionItemBuildsKeys) => void;
}

export interface IAccordionItems {
  accordionData: AccordionItemBuilds | TPathTests;
}

interface ICustomAccordionTableBody {
  items: AccordionItemBuilds[] | TPathTests[];
  type: 'build' | 'test';
}

// const headersBuilds = [
//   <FormattedMessage key="treeDetails.config" id="treeDetails.config" />,
//   <FormattedMessage key="treeDetails.compiler" id="treeDetails.compiler" />,
//   <FormattedMessage key="treeDetails.date" id="treeDetails.date" />,
//   <FormattedMessage
//     key="treeDetails.buildErrors"
//     id="treeDetails.buildErrors"
//   />,
//   <FormattedMessage key="treeDetails.buildTime" id="treeDetails.buildTime" />,
//   <HeaderWithInfo
//     key="treeDetails.status"
//     labelId="treeDetails.status"
//     tooltipId="buildTab.statusTooltip"
//   />,
// ];

const headersBuilds = {
  config: <FormattedMessage key="treeDetails.config" id="treeDetails.config" />,
  compiler: (
    <FormattedMessage key="treeDetails.compiler" id="treeDetails.compiler" />
  ),
  date: <FormattedMessage key="treeDetails.date" id="treeDetails.date" />,
  buildErrors: (
    <FormattedMessage
      key="treeDetails.buildErrors"
      id="treeDetails.buildErrors"
    />
  ),
  buildTime: (
    <FormattedMessage key="treeDetails.buildTime" id="treeDetails.buildTime" />
  ),
  status: (
    <HeaderWithInfo
      key="treeDetails.status"
      labelId="treeDetails.status"
      tooltipId="buildTab.statusTooltip"
    />
  ),
};

const headersTests = {
  path: <FormattedMessage key="testDetails.path" id="testDetails.path" />,
  status: (
    <HeaderWithInfo
      key="treeDetails.status"
      labelId="testDetails.status"
      tooltipId="testsTab.statusTooltip"
    />
  ),
  chevron: <span key="chevron"></span>, //empty cell to add the chevron}
};

const Accordion = ({ items, type, headerOnClick }: IAccordion): JSX.Element => {
  const accordionTableHeader = type === 'build' ? headersBuilds : headersTests;

  const onClickSort = useCallback(
    (sortProperty: AccordionItemBuildsKeys) => {
      headerOnClick?.(sortProperty);
    },
    [headerOnClick],
  );

  return (
    <BaseTable
      headers={Object.values(accordionTableHeader)}
      headerComponents={Object.entries(accordionTableHeader).map(column => (
        <TableHead
          className="border-b text-black"
          key={column[1].key}
          onClick={() => onClickSort(column[0] as AccordionItemBuildsKeys)}
        >
          {column[1]}
        </TableHead>
      ))}
    >
      <AccordionTableBody items={items} type={type} />
    </BaseTable>
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
                      <IndividualTestsTable
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
      <TableCell>
        {triggerInfo.date ? (
          <TooltipDateTime
            dateTime={triggerInfo.date}
            lineBreak={true}
            showLabelTime={true}
            showLabelTZ={true}
          />
        ) : (
          '-'
        )}
      </TableCell>
      <TableCell>
        <ColoredCircle
          className="max-w-6"
          quantity={buildErrors}
          backgroundClassName={buildErrors > 0 ? ItemType.Error : ItemType.None}
        />
      </TableCell>
      <TableCell>{triggerInfo.buildTime}</TableCell>
      <TableCell>
        {isBuildValid && (
          <FormattedMessage
            id="global.pass"
            defaultMessage={'Pass'}
          ></FormattedMessage>
        )}
        {isBuildInvalid && (
          <FormattedMessage
            id="global.invalid"
            defaultMessage={'Invalid'}
          ></FormattedMessage>
        )}
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
  const rows = useMemo(() => {
    return data.map(test => <TestTableRow key={test.id} test={test} />);
  }, [data]);

  return (
    <div className="h-max-12 overflow-scroll">
      <BaseTable headers={headerTestsDetails}>
        <TableBody>{rows}</TableBody>
      </BaseTable>
    </div>
  );
};

interface ITestTableRow {
  test: TIndividualTest;
}

const TestTableRow = ({ test }: ITestTableRow): JSX.Element => {
  const linkProps: LinkProps = useMemo(
    () => ({
      to: '/tree/$treeId/test/$testId',
      params: {
        testId: test.id,
      },
      search: s => s,
    }),
    [test],
  );

  return (
    <TableRow className="cursor-pointer hover:bg-lightBlue" key={test.id}>
      <TableCellWithLink linkProps={linkProps}>{test.path}</TableCellWithLink>
      <TableCellWithLink linkProps={linkProps}>{test.status}</TableCellWithLink>
      <TableCellWithLink linkProps={linkProps}>
        <TooltipDateTime
          dateTime={test.start_time}
          lineBreak={true}
          showLabelTime={true}
          showLabelTZ={true}
        />
      </TableCellWithLink>
      <TableCellWithLink linkProps={linkProps}>
        {test.duration ?? '-'}
      </TableCellWithLink>
      <TableCellWithLink
        linkProps={linkProps}
        className="flex items-center justify-end"
      >
        <ChevronRightAnimate />
      </TableCellWithLink>
    </TableRow>
  );
};

export default Accordion;
