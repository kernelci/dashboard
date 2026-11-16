import type { Dispatch, SetStateAction } from 'react';

import ReactJsonView from '@microlink/react-json-view';
import { match, P } from 'ts-pattern';

import { isUrl, shouldTruncate } from '@/lib/string';

import type {
  IJsonContent,
  SheetType,
} from '@/components/Sheet/LogOrJsonSheetContent';
import type { SubsectionLink } from '@/components/Section/Section';
import { SheetTrigger } from '@/components/Sheet';
import CopyButton from '@/components/Button/CopyButton';
import CodeBlock from '@/components/Filter/CodeBlock';
import { TruncatedValueTooltip } from '@/components/Tooltip/TruncatedValueTooltip';
import { JsonViewIcon } from '@/components/Icons/JsonView';

import { isStringRecord } from './utils';

// Show the root keys. Nested objects stay collapsed until opened in place.
const INLINE_JSON_COLLAPSE_DEPTH = 1;

export const miscContentHandler = ({
  fieldKey,
  fieldValue,
  setSheetType,
  setJsonContent,
  inlineJson = false,
}: {
  fieldKey: string;
  fieldValue: unknown;
  setSheetType?: Dispatch<SetStateAction<SheetType>>;
  setJsonContent?: Dispatch<SetStateAction<IJsonContent | undefined>>;
  inlineJson?: boolean;
}): SubsectionLink | undefined => {
  let stringField;

  if (typeof fieldValue?.toString === 'function') {
    stringField = fieldValue.toString();
  } else {
    return;
  }

  const isObjectField = Array.isArray(fieldValue) || isStringRecord(fieldValue);
  if (isObjectField) {
    stringField = JSON.stringify(fieldValue);
  }

  if (inlineJson && isObjectField) {
    return {
      children: (
        <div className="flex items-start gap-1">
          <ReactJsonView
            src={fieldValue}
            name={fieldKey}
            collapsed={INLINE_JSON_COLLAPSE_DEPTH}
            displayDataTypes={false}
            style={{ fontSize: 12 }}
          />
          <CopyButton value={stringField} />
        </div>
      ),
    };
  }

  const isUrlResult = isUrl(stringField);
  let children;
  let linkText;

  const showContent = match({ [fieldKey]: fieldValue })
    .with({ log_excerpt: '' }, _ => false)
    .with({ log_excerpt: P.string }, field => {
      children = (
        <CodeBlock code={field.log_excerpt} compact className="max-h-40" />
      );
      return true;
    })
    .otherwise(_ => {
      linkText = !shouldTruncate(stringField) ? (
        stringField
      ) : (
        <TruncatedValueTooltip
          value={stringField}
          isUrl={isUrlResult}
          isClickable={isObjectField}
        />
      );
      return true;
    });

  if (showContent) {
    return {
      unformattedTitle: fieldKey,
      link: isUrlResult ? stringField : undefined,
      icon: isObjectField ? <JsonViewIcon /> : undefined,
      wrapperComponent: isObjectField ? SheetTrigger : undefined,
      onClick: isObjectField
        ? (): void => {
            if (setSheetType !== undefined) {
              setSheetType('json');
            }
            if (setJsonContent !== undefined) {
              setJsonContent({ name: fieldKey, src: fieldValue });
            }
          }
        : undefined,
      copyValue: isObjectField ? stringField : undefined,
      linkText: linkText,
      children: children,
    };
  }
};
