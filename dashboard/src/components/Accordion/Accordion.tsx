import { ReactElement, useMemo } from 'react';

import { MdCheck, MdClose } from 'react-icons/md';

import { FormattedMessage } from 'react-intl';

import { AccordionItemBuilds } from '@/types/tree/TreeDetails';

import { TableBody, TableCell, TableRow } from '../ui/table';
import BaseTable from '../Table/BaseTable';
import {
  Collapsible,
  CollapsibleContent,
  CollapsibleTrigger,
} from '../ui/collapsible';
import ColoredCircle from '../ColoredCircle/ColoredCircle';
import { ItemType } from '../ListingItem/ListingItem';

import AccordionBuildContent from './BuildAccordionContent';

export interface IAccordion {
  headers?: ReactElement[];
  items: IAccordionItems[];
  type: 'build' | 'test';
}

export interface IAccordionItems {
  accordionData: AccordionItemBuilds | AccordionItemTestsTrigger;
}

interface ICustomAccordionTableBody {
  items: IAccordionItems[];
  type: 'build' | 'test';
}

export type AccordionItemTestsTrigger = {
  testPlans?: string;
  testSuccessfull?: number;
  testErrors?: number;
  status?: 'valid' | 'invalid';
};

const headersBuilds = [
  <FormattedMessage key="treeDetails.config" id="treeDetails.config" />,
  <FormattedMessage key="treeDetails.compiler" id="treeDetails.compiler" />,
  <FormattedMessage key="treeDetails.date" id="treeDetails.date" />,
  <FormattedMessage
    key="treeDetails.buildErrors"
    id="treeDetails.buildErrors"
  />,
  <FormattedMessage key="treeDetails.buildTime" id="treeDetails.buildTime" />,
  <FormattedMessage key="treeDetails.status" id="treeDetails.status" />,
];

const Accordion = ({ items, type }: IAccordion): JSX.Element => {
  const accordionTableHeader = type === 'build' ? headersBuilds : [];

  return (
    <BaseTable
      headers={accordionTableHeader}
      body={<AccordionTableBody items={items} type={type} />}
    />
  );
};

const AccordionTableBody = ({
  items,
  type,
}: ICustomAccordionTableBody): JSX.Element => {
  const accordionItems = useMemo(
    () =>
      items.map((item, index) => (
        <Collapsible key={index} asChild>
          <>
            <CollapsibleTrigger asChild>
              <TableRow>
                {type === 'build' ? (
                  <AccordionBuildsTrigger accordionData={item.accordionData} />
                ) : (
                  <AccordionTestsTrigger accordionData={item.accordionData} />
                )}
              </TableRow>
            </CollapsibleTrigger>
            <CollapsibleContent>
              <div className="h-fit w-f p-8">
                {type === 'build' ? (
                  <AccordionBuildContent accordionData={item.accordionData} />
                ) : (
                  <></>
                )}
              </div>
            </CollapsibleContent>
          </>
        </Collapsible>
      )),
    [items, type],
  );

  return <TableBody>{accordionItems}</TableBody>;
};

const AccordionBuildsTrigger = ({
  accordionData,
}: IAccordionItems): JSX.Element => {
  const triggerInfo = accordionData as AccordionItemBuilds;
  const buildErrors = triggerInfo.buildErrors ?? 0;
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
        {triggerInfo.status === 'valid' ? (
          <MdCheck className="text-green" />
        ) : (
          <MdClose className="text-red" />
        )}
      </TableCell>
    </>
  );
};

const AccordionTestsTrigger = ({
  accordionData,
}: IAccordionItems): JSX.Element => {
  const triggerInfo = accordionData as AccordionItemTestsTrigger;
  return (
    <>
      <TableCell>{triggerInfo.testPlans}</TableCell>
      <TableCell className="flex flex-row gap-1">
        <ColoredCircle
          quantity={triggerInfo.testErrors ?? 0}
          backgroundClassName={ItemType.Error}
        />
        <ColoredCircle
          quantity={triggerInfo.testSuccessfull ?? 0}
          backgroundClassName={ItemType.Warning}
        />
      </TableCell>
      <TableCell>
        {triggerInfo.status === 'valid' ? (
          <MdCheck className="text-green" />
        ) : (
          <MdClose className="text-red" />
        )}
      </TableCell>
    </>
  );
};

export default Accordion;
