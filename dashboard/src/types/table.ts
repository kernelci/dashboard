import type { MessagesKey } from '@/locales/messages';

export type ListingTableColumnMeta = {
  tabTarget?: string;
  /** Intl id for column label in the columns menu. */
  headerIntlKey?: MessagesKey;
  /** Columns that identify a row; always visible and leftmost. */
  isRowHeader?: boolean;
  minWidth?: number;
  maxWidth?: number;
  widthWeight?: number;
};
