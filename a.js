function reduce(arr, callback, initState) {
  for (let index = 0; index < arr.length; index++) {
    const element = arr[index];
    initState = callback(initState, element);
  }
  return initState;
}
