import { format, formatDistanceToNow } from 'date-fns';

import type { IListingItem } from '@/components/ListingItem/ListingItem';
import type { AccordionItemBuilds } from '@/types/tree/TreeDetails';
import type {
  Architecture,
  BuildsTabBuild,
  BuildsTableBuild,
  RequiredStatusCount,
} from '@/types/general';
import type { ISummaryItem } from '@/components/Tabs/Summary';
import type { Status } from '@/types/database';

import { valueOrEmpty } from '@/lib/string';

import { UNKNOWN_STRING } from './constants/backend';
import { groupStatus } from './status';
import { buildTreeBranch } from './table';

export function formatDate(
  date: Date | string,
  short?: boolean,
  addRelative?: boolean,
): string {
  const options: Intl.DateTimeFormatOptions = {
    year: short ? '2-digit' : 'numeric',
    month: short ? 'numeric' : 'long',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit',
    timeZoneName: short ? undefined : 'short',
  };

  if (typeof date === 'string') {
    date = new Date(date);
  }
  if (isNaN(date.getTime())) {
    return '-';
  }

  const formattedDate = new Intl.DateTimeFormat('en-US', options).format(date);

  // TODO: use intl for the "ago" part
  if (addRelative) {
    return `${formattedDate} (${formatDistanceToNow(date)} ago)`;
  }

  return formattedDate;
}

export const getDateOffset = (date: Date): string => {
  return format(date, 'z');
};

export const sanitizeArchs = (
  archs: Architecture | undefined,
): ISummaryItem[] => {
  if (!archs) {
    return [];
  }
  return Object.entries(archs).map(([key, value]) => {
    const { successCount, failedCount, inconclusiveCount } = groupStatus({
      doneCount: value.DONE,
      errorCount: value.ERROR,
      failCount: value.FAIL,
      missCount: value.MISS,
      passCount: value.PASS,
      skipCount: value.SKIP,
      nullCount: value.NULL,
    });

    return {
      arch: {
        text: key,
        errors: failedCount,
        success: successCount,
        unknown: inconclusiveCount,
      },
      compilers: value.compilers,
    };
  });
};

export const sanitizeConfigs = (
  configs: Record<string, RequiredStatusCount> | undefined,
): IListingItem[] => {
  if (!configs) {
    return [];
  }

  return Object.entries(configs).map(([key, value]) => {
    const { successCount, failedCount, inconclusiveCount } = groupStatus({
      doneCount: value.DONE,
      errorCount: value.ERROR,
      failCount: value.FAIL,
      missCount: value.MISS,
      passCount: value.PASS,
      skipCount: value.SKIP,
      nullCount: value.NULL,
    });

    return {
      text: key,
      errors: failedCount,
      success: successCount,
      unknown: inconclusiveCount,
    };
  });
};

// TODO: Check if it's still necessary and remove it if not
const isBuildError = (build_status: Status): number => {
  return build_status === 'FAIL' ? 1 : 0;
};

export const sanitizeBuilds = (
  builds: BuildsTabBuild[] | undefined,
): AccordionItemBuilds[] => {
  if (!builds) {
    return [];
  }

  return builds.map(build => ({
    id: build.id,
    config:
      build.config_name === UNKNOWN_STRING ? undefined : build.config_name,
    architecture:
      build.architecture === UNKNOWN_STRING ? undefined : build.architecture,
    date: build.start_time,
    buildTime: build.duration,
    compiler: build.compiler === UNKNOWN_STRING ? undefined : build.compiler,
    buildErrors: isBuildError(build.status),
    status: build.status,
    buildLogs: build.log_url,
    kernelConfig: build.config_url,
    treeBranch: buildTreeBranch(build.tree_name, build.git_repository_branch),
    lab: typeof build.misc?.lab === 'string' ? build.misc.lab : undefined,
  }));
};

export const sanitizeBuildTable = (
  builds: BuildsTableBuild[],
): AccordionItemBuilds[] => {
  return builds.map(build => ({
    id: build.id,
    config: build.config_name,
    architecture: build.architecture,
    date: build.start_time,
    buildTime: build.duration,
    compiler: build.compiler,
    buildErrors: isBuildError(build.status),
    status: build.status,
    buildLogs: build.log_url,
    treeBranch: buildTreeBranch(build.tree_name, build.git_repository_branch),
    lab: typeof build.misc?.lab === 'string' ? build.misc.lab : undefined,
  }));
};

export const sanitizeBuildsSummary = (
  buildsSummary: RequiredStatusCount | undefined,
): RequiredStatusCount =>
  buildsSummary
    ? buildsSummary
    : { FAIL: 0, NULL: 0, PASS: 0, ERROR: 0, MISS: 0, DONE: 0, SKIP: 0 };

/**
 * Maps an object (Record or another class) from {"key": "value"} or {"key": ["value"]} to {"filter_key": ["value"]}
 *
 * @param instance - the object to make compatible with backend filters
 *
 * @returns a formatted Record<string, string[]> where the keys start with "filter_" and the values are an array of strings
 */
export const mapFiltersKeysToBackendCompatible = <T extends object>(
  instance: T,
): Record<string, string[]> => {
  const filterParam: Record<string, string[]> = {};

  for (const [key, value] of Object.entries(instance)) {
    const filterKey = `filter_${key}`;
    if (!filterParam[filterKey]) {
      filterParam[filterKey] = [];
    }

    if (!Array.isArray(value)) {
      filterParam[filterKey] = [String(value)];
    } else {
      value.forEach(entry => {
        filterParam[filterKey].push(String(entry));
      });
    }
  }

  return filterParam;
};

export const isStringRecord = (
  obj: unknown,
): obj is Record<string, unknown> => {
  return (
    typeof obj === 'object' &&
    obj !== null &&
    !(obj instanceof Set) &&
    !Array.isArray(obj)
  );
};

export const isEmptyObject = (obj: Record<string, unknown>): boolean => {
  for (const prop in obj) {
    if (Object.prototype.hasOwnProperty.call(obj, prop)) {
      return false;
    }
  }
  return true;
};

type TIssueFilter = {
  id: string;
  version?: number;
};

export const version_prefix = 'v.';

export const getIssueFilterLabel = (issueFilter: TIssueFilter): string => {
  const issueId = issueFilter.id;
  const issueVersion = issueFilter.version;

  if (issueVersion === undefined || issueVersion === null) {
    return issueId;
  }

  const versionFormatted = `${version_prefix}${issueVersion}`;

  return `${issueId} ${versionFormatted}`;
};

export const getTitle = (title?: string, loading?: boolean): string => {
  if (loading) {
    return 'Loading...';
  }

  return valueOrEmpty(title);
};

export const getStringParam = (
  params: Record<string, string>,
  key: string,
  defaultValue?: string,
): string => {
  return key in params ? params[key] : defaultValue ?? '';
};

type SortByErrorsAndTextParam = { errors: number; text: string };

/**
 * Sorted with UNKNOWN_STRING text last, then by descending error count, then by
 * text alphabetically.
 */
export const sortByErrorsAndText = (
  a: SortByErrorsAndTextParam,
  b: SortByErrorsAndTextParam,
): number => {
  const { errors: errorsA, text: textA } = a;
  const { errors: errorsB, text: textB } = b;

  if (textA === UNKNOWN_STRING && textA !== textB) {
    return 1;
  }
  if (textB === UNKNOWN_STRING && textB !== textA) {
    return -1;
  }

  if (errorsB !== errorsA) {
    return errorsB - errorsA;
  }

  return textA.localeCompare(textB);
};
