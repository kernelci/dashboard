import { format } from 'date-fns';

import type { IListingItem } from '@/components/ListingItem/ListingItem';
import type {
  AccordionItemBuilds,
  TTreeDetailsFilter,
} from '@/types/tree/TreeDetails';
import type {
  Architecture,
  BuildsTabBuild,
  BuildsTableBuild,
  BuildStatus,
  StatusCount,
} from '@/types/general';
import type { ISummaryItem } from '@/components/Tabs/Summary';
import type { Status } from '@/types/database';

import { valueOrEmpty } from '@/lib/string';

import { UNKNOWN_STRING } from './constants/backend';
import { groupStatus } from './status';
import { buildTreeBranch } from './table';

export function formatDate(date: Date | string, short?: boolean): string {
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

  return new Intl.DateTimeFormat('en-US', options).format(date);
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
  configs: Record<string, BuildStatus> | undefined,
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

export const sanitizePlatforms = (
  platforms:
    | Record<string, BuildStatus>
    | Record<string, StatusCount>
    | undefined,
): IListingItem[] => {
  if (!platforms) {
    return [];
  }

  return Object.entries(platforms).map(([key, value]) => {
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
    kernelImage: build.misc ? build.misc['kernel_type'] : undefined,
    dtb: build.misc ? build.misc['dtb'] : undefined,
    systemMap: build.misc ? build.misc['system_map'] : undefined,
    modules: build.misc ? build.misc['modules'] : undefined,
    treeBranch: buildTreeBranch(build.tree_name, build.git_repository_branch),
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
  }));
};

export const sanitizeBuildsSummary = (
  buildsSummary: BuildStatus | undefined,
): BuildStatus =>
  buildsSummary
    ? buildsSummary
    : { FAIL: 0, NULL: 0, PASS: 0, ERROR: 0, MISS: 0, DONE: 0, SKIP: 0 };

// TODO, remove this function, is just a step further towards the final implementation
export const mapFiltersKeysToBackendCompatible = (
  filter: TTreeDetailsFilter | Record<string, never>,
): Record<string, string[]> => {
  const filterParam: { [key: string]: string[] } = {};

  Object.keys(filter).forEach(key => {
    const filterList = filter[key as keyof TTreeDetailsFilter];
    filterList?.forEach(value => {
      if (!filterParam[`filter_${key}`]) {
        filterParam[`filter_${key}`] = [value.toString()];
      } else {
        filterParam[`filter_${key}`].push(value.toString());
      }
    });
  });

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
