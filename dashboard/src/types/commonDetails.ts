import { z } from 'zod';

import type {
  ArchCompilerStatus,
  Architecture,
  PropertyStatusCounts,
  RequiredStatusCount,
  StatusCounts,
} from './general';
import type { TIssue } from './issues';

type TestSummary = {
  status: StatusCounts;
  architectures: ArchCompilerStatus[];
  configs: PropertyStatusCounts;
  issues: TIssue[];
  unknown_issues: number;
  fail_reasons: Record<string, number>;
  failed_platforms: string[];
  environment_compatible?: PropertyStatusCounts;
  environment_misc?: PropertyStatusCounts;
  platforms?: PropertyStatusCounts;
};

type BuildSummary = {
  status: RequiredStatusCount;
  architectures: Architecture;
  configs: Record<string, RequiredStatusCount>;
  issues: TIssue[];
  unknown_issues: number;
};

export type Summary = {
  builds: BuildSummary;
  boots: TestSummary;
  tests: TestSummary;
};

export type GlobalFilters = {
  configs: string[];
  architectures: string[];
  compilers: string[];
};

export type IssueFilterItem = [string, number?];

export type LocalFilters = {
  issues: IssueFilterItem[];
  has_unknown_issue: boolean;
};

export type DetailsFilters = {
  all: GlobalFilters;
  builds: LocalFilters;
  boots: LocalFilters;
  tests: LocalFilters;
};

export const DEFAULT_LOG_OPEN = false;
export const zLogOpen = z
  .boolean()
  .catch(DEFAULT_LOG_OPEN)
  .default(DEFAULT_LOG_OPEN);
