import { describe, it, expect, assert } from 'vitest';

import { stringifySearchWith } from '@tanstack/react-router';

import {
  flattenObject,
  unflattenObject,
  parseSearch,
  stringifySearch,
  isEncodedJSONArrayParam,
} from './search';

const KEY_FLAT_CHAR = '|';

const simpleObject = {
  origin: 'maestro',
  intervalInDays: 7,
  // eslint-disable-next-line no-magic-numbers
  treeIndexes: [1, 2, 3],
};

const simpleObjectStringify =
  '?origin=maestro&intervalInDays=7&treeIndexes[]=1,2,3';

const nestedObject = {
  origin: 'maestro',
  intervalInDays: 7,
  tableFilter: {
    bootsTable: 'all',
    buildsTable: 'failed',
    testsTable: 'all',
  },
  treeInfo: {
    treeName: 'android',
    gitCommitHash: 'hash',
  },
  diffFilter: {
    configs: { defconfig: true },
    archs: { arm: true },
    testPath: 'amlogic',
  },
  treeIndexes: [0, 1, 2],
};

const flatObject = {
  origin: 'maestro',
  intervalInDays: 7,
  'tableFilter|bootsTable': 'all',
  'tableFilter|buildsTable': 'failed',
  'tableFilter|testsTable': 'all',
  'treeInfo|treeName': 'android',
  'treeInfo|gitCommitHash': 'hash',
  'diffFilter|configs|defconfig': true,
  'diffFilter|archs|arm': true,
  'diffFilter|testPath': 'amlogic',
  treeIndexes: [0, 1, 2],
};

const nestedObjectStringify =
  '?origin=maestro&intervalInDays=7' +
  '&tableFilter|bootsTable=all&tableFilter|buildsTable=failed&tableFilter|testsTable=all' +
  '&treeInfo|treeName=android&treeInfo|gitCommitHash=hash' +
  '&diffFilter|configs|defconfig=true&diffFilter|archs|arm=true&diffFilter|testPath=amlogic' +
  '&treeIndexes[]=0,1,2';

describe('isEncodedArrayParam', () => {
  const emptyJSONArrayStr = 'treeIndexes=[]';
  const emptyQSArrayStr = 'treeIndexes[]';
  const filledJSONArrayStr = 'treeIndexes=[1,2,3]';
  const filledQSArrayStr = 'treeIndexes[]=1,2,3';

  it('JSON empty array', () => {
    expect(isEncodedJSONArrayParam(emptyJSONArrayStr)).toBe(true);
  });

  it('JSON empty array - URI encoded', () => {
    expect(isEncodedJSONArrayParam(encodeURI(emptyJSONArrayStr))).toBe(true);
  });

  it('query-string empty array', () => {
    expect(isEncodedJSONArrayParam(emptyQSArrayStr)).toBe(false);
  });

  it('query-string empty array - URI encoded', () => {
    expect(isEncodedJSONArrayParam(encodeURI(emptyQSArrayStr))).toBe(false);
  });

  it('JSON filled array', () => {
    expect(isEncodedJSONArrayParam(filledJSONArrayStr)).toBe(true);
  });

  it('JSON filled array - URI encoded', () => {
    expect(isEncodedJSONArrayParam(encodeURI(filledJSONArrayStr))).toBe(true);
  });

  it('JSON filled array - partially URI encoded', () => {
    const customEncodedStr = filledJSONArrayStr.replace(/,/g, '%2C');
    expect(isEncodedJSONArrayParam(customEncodedStr)).toBe(true);
  });

  it('query-string filled array', () => {
    expect(isEncodedJSONArrayParam(filledQSArrayStr)).toBe(false);
  });

  it('query-string filled array - URI encoded', () => {
    expect(isEncodedJSONArrayParam(encodeURI(filledQSArrayStr))).toBe(false);
  });
});

describe('flattenObject', () => {
  it('Simple object with filled array', () => {
    expect(flattenObject(simpleObject, KEY_FLAT_CHAR)).toStrictEqual(
      simpleObject,
    );
  });

  it('Simple object with empty array', () => {
    const simpleObjectEmptyArray = { ...simpleObject, treeIndexes: [] };
    expect(flattenObject(simpleObjectEmptyArray, KEY_FLAT_CHAR)).toStrictEqual(
      simpleObjectEmptyArray,
    );
  });

  it('Nested object', () => {
    expect(flattenObject(nestedObject, KEY_FLAT_CHAR)).toStrictEqual(
      flatObject,
    );
  });
});

describe('unflattenObject', () => {
  it('Simple object with filled array', () => {
    expect(unflattenObject(simpleObject, KEY_FLAT_CHAR)).toStrictEqual(
      simpleObject,
    );
  });

  it('Simple object with empty array', () => {
    const simpleObjectEmptyArray = { ...simpleObject, treeIndexes: [] };
    expect(
      unflattenObject(simpleObjectEmptyArray, KEY_FLAT_CHAR),
    ).toStrictEqual(simpleObjectEmptyArray);
  });

  it('Nested object', () => {
    expect(unflattenObject(flatObject, KEY_FLAT_CHAR)).toStrictEqual(
      nestedObject,
    );
  });
});

describe('parseSearch', () => {
  it('Simple object with filled array', () => {
    expect(parseSearch(simpleObjectStringify)).toStrictEqual(simpleObject);
  });

  it('Simple object with empty array', () => {
    const simpleObjectEmptyArray = { ...simpleObject, treeIndexes: [] };
    const simpleObjectEmptyArrayStringify =
      '?origin=maestro&intervalInDays=7&treeIndexes[]';
    expect(parseSearch(simpleObjectEmptyArrayStringify)).toStrictEqual(
      simpleObjectEmptyArray,
    );
  });

  it('Nested object', () => {
    expect(parseSearch(nestedObjectStringify)).toStrictEqual(nestedObject);
  });

  it('Simple object with filled array - URI encoded', () => {
    expect(parseSearch(encodeURI(simpleObjectStringify))).toStrictEqual(
      simpleObject,
    );
  });

  it('Nested object - URI encoded', () => {
    expect(parseSearch(encodeURI(nestedObjectStringify))).toStrictEqual(
      nestedObject,
    );
  });

  it('JSON stringified simple object with filled array', () => {
    const JSONSimpleObjectStringify = stringifySearchWith(JSON.stringify)(
      simpleObject,
    );
    expect(parseSearch(JSONSimpleObjectStringify)).toStrictEqual(simpleObject);
  });

  it('JSON stringified simple object with empty array', () => {
    const simpleObjectEmptyArray = { ...simpleObject, treeIndexes: [] };
    const JSONSimpleObjectStringify = stringifySearchWith(JSON.stringify)(
      simpleObjectEmptyArray,
    );
    expect(parseSearch(JSONSimpleObjectStringify)).toStrictEqual(
      simpleObjectEmptyArray,
    );
  });

  it('JSON stringified simple object - not URI encoded', () => {
    const JSONSimpleObjectStringify = stringifySearchWith(JSON.stringify)(
      simpleObject,
    );
    const decodeStr = JSONSimpleObjectStringify.replace(/%5B/g, '[').replace(
      /%5D/g,
      ']',
    );
    expect(parseSearch(decodeStr)).toStrictEqual(simpleObject);
  });

  it('JSON stringified nested object', () => {
    const JSONNestedObjectStringify = stringifySearchWith(JSON.stringify)(
      nestedObject,
    );
    expect(parseSearch(JSONNestedObjectStringify)).toStrictEqual(nestedObject);
  });
});

describe('stringifySearch', () => {
  const assertSearchParams = (
    result: string,
    expected: Record<string, unknown>,
  ): void => {
    assert(result.includes('?'));
    for (const [key, value] of Object.entries(expected)) {
      if (Array.isArray(value)) {
        const arrayKeyStr = `${encodeURIComponent(key)}[]`;
        const arrayValueStr = `${value.length !== 0 ? '=' + value.join(',') : ''}`;
        assert(result.includes(`${arrayKeyStr}${arrayValueStr}`));
      } else {
        const valueStr = `${encodeURIComponent(key)}=${value}`;
        assert(result.includes(valueStr));
      }
    }
  };

  it('Simple object with filled array', () => {
    const result = stringifySearch(simpleObject);
    assertSearchParams(result, simpleObject);
  });

  it('Simple object with empty array', () => {
    const simpleObjectEmptyArray = { ...simpleObject, treeIndexes: [] };
    const result = stringifySearch(simpleObjectEmptyArray);
    assertSearchParams(result, simpleObjectEmptyArray);
  });

  it('Nested object', () => {
    const result = stringifySearch(nestedObject);
    assertSearchParams(result, flatObject);
  });
});
