import data from '../data/hex64_full.json' with { type: 'json' };

export const HEXAGRAMS = data.hexagrams;
export const TAG_TO_OP = data.tagToOp || {};
