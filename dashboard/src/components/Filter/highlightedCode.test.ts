/* eslint-disable no-magic-numbers */
import { describe, it, expect } from 'vitest';

import { generateHighlightedCode } from './CodeBlock';

describe('highlightCode', () => {
  it('Gets n errors', () => {
    const result = generateHighlightedCode(
      'There was 1 error\n' + 'Then there were 200 errors',
    );
    expect(result.errorCount).toBe(2);
  });

  it('Gets n fails', () => {
    const result = generateHighlightedCode(
      'There was 1 fail\n' + 'Then there were 200 fails',
    );
    expect(result.failCount).toBe(2);
  });

  it('Gets error:/errors: N', () => {
    const testString = 'E summary was error: 5\n' + 'and then errors: 2';
    const result = generateHighlightedCode(testString);
    expect(result.errorCount).toBe(2);
  });

  it('Does not get error:/errors: 0', () => {
    const testString = 'E summary was error: 0\n' + 'and then errors: 0';
    const result = generateHighlightedCode(testString);
    expect(result.errorCount).toBe(0);
    expect(result.highlightCount).toBe(2);
  });

  it('Gets fail:/fails:/failed: N', () => {
    const testString =
      'Summary was fail: 5\n' + 'and then fails: 2\n' + 'and finally failed: 8';
    const result = generateHighlightedCode(testString);
    expect(result.failCount).toBe(3);
  });

  it('Does not get fail:/fails:/failed: 0', () => {
    const testString =
      'Summary was fail: 0\n' + 'and then fails: 0\n' + 'and finally failed: 0';
    const result = generateHighlightedCode(testString);
    expect(result.failCount).toBe(0);
    expect(result.highlightCount).toBe(3);
  });

  it('Gets failed to/with', () => {
    const testString =
      'Failed to find module\n' + 'Firmware failed with a problem';
    const result = generateHighlightedCode(testString);
    expect(result.failCount).toBe(2);
  });

  it('Gets error/fail messages', () => {
    const testString =
      'There was this fail: example\n' + 'There was this error: example';
    const result = generateHighlightedCode(testString);
    expect(result.failCount).toBe(1);
    expect(result.errorCount).toBe(1);
  });

  it('Does not consider backward count on fail', () => {
    // https://dashboard.kernelci.org/test/maestro%3A680a998f43948caad953a670?l=true
    const testString = 'Summary was pass:5 fail:0';
    const result = generateHighlightedCode(testString);
    expect(result.failCount).toBe(0);
    expect(result.highlightCount).toBe(1);
  });

  it('Does not consider backward count on error', () => {
    const testString = 'E summary was pass:5 error:0';
    const result = generateHighlightedCode(testString);
    expect(result.errorCount).toBe(0);
    expect(result.highlightCount).toBe(1);
  });

  it('Ignores ignore errors', () => {
    const testString = 'Ignore error in the next command';
    const result = generateHighlightedCode(testString);
    expect(result.errorCount).toBe(0);
    expect(result.highlightCount).toBe(1);
  });

  it('Considers the result:fail', () => {
    const testString = 'The final result:fail.\n' + 'An equal result=fail.';
    const result = generateHighlightedCode(testString);
    expect(result.failCount).toBe(2);
  });

  it('Considers error/fail/failed at the end of line', () => {
    const testString =
      'Result... fail\n' + 'Result... failed\n' + 'Result... error\n';
    const result = generateHighlightedCode(testString);
    expect(result.failCount).toBe(2);
    expect(result.errorCount).toBe(1);
  });

  it('Matches exception errors', () => {
    const testString = 'There was an AssertionError: example';
    const result = generateHighlightedCode(testString);
    expect(result.errorCount).toBe(1);
  });

  it('Matches generic errors', () => {
    const testString = 'We had error somewhere';
    const result = generateHighlightedCode(testString);
    expect(result.errorCount).toBe(1);
  });

  it('Matches negative problems', () => {
    const testString = 'there was error -110\n' + 'and also fail -100';
    const result = generateHighlightedCode(testString);
    expect(result.errorCount).toBe(1);
    expect(result.failCount).toBe(1);
  });
});
