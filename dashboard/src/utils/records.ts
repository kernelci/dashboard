const isRecord = (obj: unknown): obj is Record<string, unknown> => {
  return typeof obj === 'object' && !Array.isArray(obj);
};

export const deepCompare = (
  obj1: Record<string, unknown>,
  obj2: Record<string, unknown>,
): boolean => {
  if (Object.keys(obj1).length !== Object.keys(obj2).length) {
    return false;
  }

  for (const key in obj1) {
    if (isRecord(obj1[key]) && isRecord(obj2[key])) {
      if (!deepCompare(obj1[key], obj2[key])) {
        return false;
      }
    } else if (obj1[key] !== obj2[key]) {
      return false;
    }
  }

  return true;
};
