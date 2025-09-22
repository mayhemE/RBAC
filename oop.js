function SearchingChallenge(str) {
  const maximumPatternLength = Math.floor(str.length / 2);

  for (let len = maximumPatternLength; len >= 2; len--) {
    for (let i = 0; i <= str.length - len; i++) {
      const pattern = str.substring(i, i + len);

      const tempStr = str.substring(i + len);

      if (tempStr.includes(pattern)) {
        return `yes ${pattern}`;
      }
    }
  }

  return "no null";
}
console.log(SearchingChallenge("abcdef"))
console.log(SearchingChallenge("sskfssbbb9bbb"))