import { ReactNode, useMemo } from 'react';

import { MdCheck, MdClose } from 'react-icons/md';

import { TableBody, TableCell, TableRow } from '../ui/table';
import BaseTable from '../Table/BaseTable';
import {
  Collapsible,
  CollapsibleContent,
  CollapsibleTrigger,
} from '../ui/collapsible';
import ColoredCircle from '../ColoredCircle/ColoredCircle';
import { ItemType } from '../ListingItem/ListingItem';

export interface IAccordion {
  headers: string[];
  items: IAccordionItems[];
  type: 'build' | 'test';
}

export interface IAccordionItems {
  trigger: AccordionItemBuildsTrigger | AccordionItemTestsTrigger;
  content?: ReactNode;
}

interface ICustomAccordionTableBody {
  items: IAccordionItems[];
  type: 'build' | 'test';
}

export type AccordionItemBuildsTrigger = {
  config?: string;
  compiler?: string;
  date?: string;
  buildErrors?: number;
  buildTime?: string;
  status?: 'valid' | 'invalid';
};

export type AccordionItemTestsTrigger = {
  testPlans?: string;
  testSuccessfull?: number;
  testErrors?: number;
  status?: 'valid' | 'invalid';
};

const Accordion = ({ headers, items, type }: IAccordion): JSX.Element => {
  const accordionTableHeader = useMemo(
    () => headers.map(header => <span key={header}>{header}</span>),
    [headers],
  );

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
                  <AccordionBuildsTrigger trigger={item.trigger} />
                ) : (
                  <AccordionTestsTrigger trigger={item.trigger} />
                )}
              </TableRow>
            </CollapsibleTrigger>
            <CollapsibleContent>{item.content}</CollapsibleContent>
          </>
        </Collapsible>
      )),
    [items, type],
  );

  return <TableBody>{accordionItems}</TableBody>;
};

const AccordionBuildsTrigger = ({ trigger }: IAccordionItems): JSX.Element => {
  const triggerInfo = trigger as AccordionItemBuildsTrigger;
  return (
    <>
      <TableCell>{triggerInfo.config}</TableCell>
      <TableCell>{triggerInfo.compiler}</TableCell>
      <TableCell>{triggerInfo.date}</TableCell>
      <TableCell>
        <ColoredCircle
          className="max-w-6"
          quantity={triggerInfo.buildErrors ?? 0}
          backgroundClassName={ItemType.Error}
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

const AccordionTestsTrigger = ({ trigger }: IAccordionItems): JSX.Element => {
  const triggerInfo = trigger as AccordionItemTestsTrigger;
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
