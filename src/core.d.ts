export interface Hexagram {
  index: number;
  bin: string;
  name: string;
  pinyin: string;
  en: string;
  category: string;
  tags: string[];
  weight: number;
  hash: number;
}

export interface TranceiveResult {
  input: string;
  hexCode: Hexagram;
  featureVec: number[];
  pseudoCode: string;
  controlSignal: string[];
}

export interface OperateResult {
  op: string;
  input: Hexagram;
  result: Hexagram;
  resultBin: string;
}

export class Hex64Engine {
  constructor(database?: Hexagram[]);
  lookup(input: string | number): Hexagram;
  featureVector(input: string | number): number[];
  pseudoCode(input: string | number): string;
  controlSignal(input: string | number): string[];
  tranceive(input: string | number): TranceiveResult;
  operate(op: string, input: string | number, secondInput?: string | number): OperateResult;
}
