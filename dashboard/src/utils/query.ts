export const retryHandler = (retryCount: number | boolean = 3) => {
  return (failureCount: number, error: Error): boolean => {
    const splittedError = error.message.split(':');
    if (
      splittedError &&
      splittedError.length > 1 &&
      splittedError[0] === '200'
    ) {
      return false;
    }

    if (typeof retryCount === 'boolean') {
      return retryCount;
    }

    if (typeof retryCount === 'number' && failureCount >= retryCount) {
      return false;
    }
    return true;
  };
};
