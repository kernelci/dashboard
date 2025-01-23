import qs from 'query-string';

import { type AnySchema, parseSearchWith } from '@tanstack/react-router';

import { type SearchParamsKeys, type TFilterKeys } from '@/types/general';
import type {
  possibleBuildsTableFilter,
  possibleTabs,
  possibleTestsTableFilter,
  TableFilter,
  TTreeInformation,
} from '@/types/tree/TreeDetails';

import { isStringRecord } from './utils';

// Must be a character not used in any other query parameters (e.g. '.' or '_' wouldn't work)
const KEY_FLAT_CHAR = '|';
const ARRAY_SEPARATOR = ',';

export const isEncodedJSONArrayParam = (str: string): boolean => {
  // Regex responsible to match URI encoded (or not) array of numbers
  // in the query parameters when they where JSON stringified and not
  // query-string stringified.
  const encodedArrayRegex =
    /=(%5B|\[)\d+(?:(%2C|,)\d+)*(%5D|\])|=(%5B|\[)(%5D|\])/;
  return encodedArrayRegex.test(str);
};

export const parseSearch = (searchStr: string): AnySchema => {
  const JSONChar = '{';
  const encodeJSONChar = encodeURI(JSONChar);
  const encodeKeyFlatChar = encodeURI(KEY_FLAT_CHAR);

  if (
    ((!searchStr.includes(KEY_FLAT_CHAR) ||
      !searchStr.includes(encodeKeyFlatChar)) &&
      (searchStr.includes(JSONChar) || searchStr.includes(encodeJSONChar))) ||
    isEncodedJSONArrayParam(searchStr)
  ) {
    return parseSearchWith(JSON.parse)(searchStr);
  }

  const flattenedParsedSearch = qs.parse(searchStr, {
    arrayFormat: 'bracket-separator',
    arrayFormatSeparator: ARRAY_SEPARATOR,
    parseBooleans: true,
    types: {
      i: 'number',
      df_bdx: 'number',
      df_bdm: 'number',
      df_btdx: 'number',
      df_btdm: 'number',
      df_tdx: 'number',
      df_tdm: 'number',
      x: 'number[]',
      st: 'number',
      et: 'number',
    },
  });

  Object.setPrototypeOf(flattenedParsedSearch, Object.prototype);
  const minifiedParsedSearch = unflattenObject(
    flattenedParsedSearch,
    KEY_FLAT_CHAR,
  );
  const parsedSearch = unminifyParams(minifiedParsedSearch);
  return parsedSearch;
};

export const stringifySearch = (
  searchParams: Record<string, unknown>,
): string => {
  const minifiedSearchParams = minifyParams(searchParams);
  const flattenedSearchParams = flattenObject(
    minifiedSearchParams,
    KEY_FLAT_CHAR,
  );
  const stringifiedSearch = qs.stringify(flattenedSearchParams, {
    arrayFormat: 'bracket-separator',
    arrayFormatSeparator: ARRAY_SEPARATOR,
  });
  return stringifiedSearch && `?${stringifiedSearch}`;
};

export const flattenObject = (
  obj: Record<string, unknown>,
  keySplitChar: string,
  parent = '',
  result: Record<string, boolean | number | string | number[]> = {},
): Record<string, boolean | string | number | number[]> => {
  for (const strKey in obj) {
    const key = strKey as keyof typeof obj;
    if (Object.prototype.hasOwnProperty.call(obj, key)) {
      const newKey = parent ? `${parent}${keySplitChar}${key}` : key;
      if (isStringRecord(obj[key])) {
        flattenObject(obj[key], keySplitChar, newKey, result);
      } else if (
        typeof obj[key] === 'number' ||
        typeof obj[key] === 'string' ||
        typeof obj[key] === 'boolean' ||
        Array.isArray(obj[key])
      ) {
        result[newKey] = obj[key];
      }
    }
  }
  return result;
};

export const unflattenObject = (
  obj: qs.ParsedQuery<string | number | boolean>,
  keySplitChar: string,
): Record<string, unknown> => {
  const result: Record<string, unknown> = {};
  for (const key in obj) {
    if (Object.prototype.hasOwnProperty.call(obj, key)) {
      const keys = key.split(keySplitChar);
      keys.reduce<Record<string, unknown> | number[]>((acc, part, index) => {
        if (isStringRecord(acc)) {
          if (index === keys.length - 1) {
            acc[part] = obj[key];
          } else {
            acc[part] = acc[part] || {};
          }
          if (isStringRecord(acc[part]) || Array.isArray(acc[part])) {
            return acc[part];
          }
        }
        return acc;
      }, result);
    }
  }
  return result;
};

const generalMinifiedParams: Record<SearchParamsKeys, string> = {
  origin: 'o',
  intervalInDays: 'i',
  currentPageTab: 'p',
  tableFilter: 'tf',
  diffFilter: 'df',
  treeSearch: 'ts',
  hardwareSearch: 'hs',
  treeInfo: 'ti',
  treeIndexes: 'x',
  treeCommits: 'c',
  startTimestampInSeconds: 'st',
  endTimestampInSeconds: 'et',
} as const;

const treeInfoMinifiedParams: Record<keyof TTreeInformation, string> = {
  gitBranch: 'gb',
  gitUrl: 'gu',
  treeName: 't',
  commitName: 'c',
  headCommitHash: 'ch',
} as const;

const tableFilterMinifiedParams: Record<keyof TableFilter, string> = {
  buildsTable: 'b',
  bootsTable: 'bt',
  testsTable: 't',
} as const;

const diffFilterMinifiedParams: Record<TFilterKeys, string> = {
  configs: 'c',
  archs: 'a',
  buildStatus: 'bs',
  compilers: 'cp',
  bootStatus: 'bts',
  testStatus: 'ts',
  testPath: 'tp',
  bootPath: 'bp',
  buildDurationMax: 'bdc',
  buildDurationMin: 'bdf',
  bootDurationMax: 'btdc',
  bootDurationMin: 'btdf',
  testDurationMax: 'tdc',
  testDurationMin: 'tdf',
  hardware: 'h',
  trees: 't',
  bootPlatform: 'btpf',
  testPlatform: 'tpf',
  buildIssue: 'bi',
  bootIssue: 'bti',
  testIssue: 'ti',
};

type MinifiedParams = Record<
  SearchParamsKeys | TFilterKeys | keyof TableFilter | keyof TTreeInformation,
  string
>;
type MinifiedParamsKeys = keyof MinifiedParams;
const minifiedParams: MinifiedParams = {
  ...generalMinifiedParams,
  ...treeInfoMinifiedParams,
  ...tableFilterMinifiedParams,
  ...diffFilterMinifiedParams,
} as const;

type MinifiedValues = Record<
  | (typeof possibleTabs)[number]
  | (typeof possibleBuildsTableFilter)[number]
  | (typeof possibleTestsTableFilter)[number],
  string
>;
type MinifiedValuesKeys = keyof MinifiedValues;
const minifiedValues: MinifiedValues = {
  // TableFilter values
  all: 'a',
  success: 's',
  failed: 'f',
  inconclusive: 'i',
  valid: 'v',
  invalid: 'iv',
  null: 'n',

  // CurrentPageTab values
  'global.builds': 'b',
  'global.boots': 'bt',
  'global.tests': 't',
} as const;

export const minifyParams = (
  searchParams: Record<string, unknown>,
): Record<string, unknown> => {
  const result: Record<string, unknown> = {};
  for (const key in searchParams) {
    if (Object.prototype.hasOwnProperty.call(searchParams, key)) {
      const newKey =
        key in minifiedParams ? minifiedParams[key as MinifiedParamsKeys] : key;
      if (isStringRecord(searchParams[key])) {
        result[newKey] = minifyParams(searchParams[key]);
      } else {
        const value =
          typeof searchParams[key] === 'string' &&
          searchParams[key] in minifiedValues
            ? minifiedValues[searchParams[key] as MinifiedValuesKeys]
            : searchParams[key];
        result[newKey] = value;
      }
    }
  }
  return result;
};

const generalMinifiedParamsArray = Object.entries(generalMinifiedParams).map(
  ([key, value]) => [value, key],
);
const treeInfoMinifiedParamsArray = Object.entries(treeInfoMinifiedParams).map(
  ([key, value]) => [value, key],
);
const tableFilterMinifiedParamsArray = Object.entries(
  tableFilterMinifiedParams,
).map(([key, value]) => [value, key]);
const diffFilterMinifiedParamsArray = Object.entries(
  diffFilterMinifiedParams,
).map(([key, value]) => [value, key]);
const minifiedValuesArray = Object.entries(minifiedValues).map(
  ([key, value]) => [value, key],
);

const groupedMinifiedParams = {
  general: Object.fromEntries(generalMinifiedParamsArray),
  ti: Object.fromEntries(treeInfoMinifiedParamsArray),
  tf: Object.fromEntries(tableFilterMinifiedParamsArray),
  df: Object.fromEntries(diffFilterMinifiedParamsArray),
  value: Object.fromEntries(minifiedValuesArray),
} as const;
type GroupedMinifiedKeys = keyof typeof groupedMinifiedParams;

export const unminifyParams = (
  searchParams: Record<string, unknown>,
  group: GroupedMinifiedKeys = 'general',
): Record<string, unknown> => {
  const result: Record<string, unknown> = {};
  for (const key in searchParams) {
    if (Object.prototype.hasOwnProperty.call(searchParams, key)) {
      const newKey =
        key in groupedMinifiedParams[group]
          ? groupedMinifiedParams[group][key as GroupedMinifiedKeys]
          : key;
      if (isStringRecord(searchParams[key])) {
        result[newKey] = unminifyParams(
          searchParams[key],
          key in groupedMinifiedParams
            ? (key as GroupedMinifiedKeys)
            : 'general',
        );
      } else {
        const value =
          typeof searchParams[key] === 'string' &&
          searchParams[key] in groupedMinifiedParams['value']
            ? groupedMinifiedParams['value'][
                searchParams[key] as GroupedMinifiedKeys
              ]
            : searchParams[key];
        result[newKey] = value;
      }
    }
  }
  return result;
};
