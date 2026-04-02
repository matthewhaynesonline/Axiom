import config from "../../config.json";

export function getDisplayScore(score: number): string {
  let displayScore = score.toFixed(config.theme.numDecimalsDisplay);

  if (score > 0) {
    displayScore = `+${displayScore}`;
  }

  return displayScore;
}
