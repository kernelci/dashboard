export const getStringParam = (
  params: Record<string, string>,
  key: string,
  defaultValue?: string,
): string => {
  return key in params ? params[key] : defaultValue ?? '';
};
