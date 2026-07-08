import { HEXAGRAMS, TAG_TO_OP } from '../src/database.js';
import { readFileSync, writeFileSync } from 'node:fs';
import { fileURLToPath } from 'node:url';
import { dirname, resolve } from 'node:path';
const __dirname = dirname(fileURLToPath(import.meta.url));
const ROOT = resolve(__dirname, '..');

// --- Step 1: Find which unique opcodes are actually USED by hexagrams ---
const usedOpcodes = new Set();
HEXAGRAMS.forEach(h => {
  h.tags.forEach(t => {
    const op = TAG_TO_OP[t];
    if (op) usedOpcodes.add(op);
  });
});
console.log('Opcodes actually used by hexagrams:', usedOpcodes.size);

// --- Step 2: Load current templates ---
const html = readFileSync(ROOT + '/src/engine.html', 'utf-8');
const tmpl = html.match(/const opTemplates = \{(.+?)\};/s);
const templateKeys = tmpl ? [...tmpl[1].matchAll(/'(\w+)':\s*\{/g)].map(m => m[1]) : [];
console.log('Existing template keys:', templateKeys.length);

// --- Step 3: Find missing templates for USED opcodes ---
const missingUsed = [...usedOpcodes].filter(op => !templateKeys.includes(op));
console.log('\nMissing templates for USED opcodes (' + missingUsed.length + '):');
missingUsed.forEach(op => {
  const tags = Object.entries(TAG_TO_OP).filter(([,v]) => v === op).map(([k]) => k);
  console.log('  ' + op + ' <- ' + tags.join(', '));
});

// --- Step 4: Find duplicate Chinese keys in tagToOp ---
const chineseKeys = Object.keys(TAG_TO_OP);
const seen = {};
const duplicates = [];
chineseKeys.forEach(k => {
  if (seen[k]) duplicates.push(k + ' -> ' + seen[k] + ' | ' + TAG_TO_OP[k]);
  seen[k] = TAG_TO_OP[k];
});
console.log('\nDuplicate Chinese keys in tagToOp (' + duplicates.length + '):');
duplicates.forEach(d => console.log('  ' + d));

// --- Step 5: Suggest opcode merges (synonyms) ---
const synonyms = {
  'INCR': 'INCREMENT', 'PUBLISH': 'RELEASE', 'COMPILE': 'BUILD',
  'EVAL': 'ANALYZE', 'TEST': 'CHECK', 'FINETUNE': 'TUNE',
  'ALLIANCE': 'UNITE', 'COOPERATE': 'COLLABORATE', 'OBEY': 'FOLLOW',
  'REVOLUTION': 'CHANGE', 'NEAR': 'IMMINENT', 'RAW': 'PRIMITIVE',
  'CONSERVATIVE': 'STABILIZE', 'SLEEP': 'SUSPEND',
  'COORDINATE': 'MANAGE', 'COMMAND': 'LEAD',
  'ALLOCATE': 'DISTRIBUTE', 'ASSEMBLE': 'GATHER',
  'STILL': 'PAUSE', 'EVADE': 'RETREAT',
  'SCATTER': 'DISPATCH', 'DIFFUSE': 'SPREAD',
  'DECORATE': 'FORMAT', 'SHOW': 'DISPLAY',
  'LOSE': 'REDUCE', 'DECLINE': 'DECAY',
  'EXPECT': 'WAIT', 'PREPARE': 'INIT',
  'PROSPEROUS': 'ABUNDANT', 'WEALTHY': 'ABUNDANT',
  'AMPLE': 'ENRICH', 'SURPLUS': 'ENRICH',
  'GRAND': 'SCALE', 'BEAUTIFY': 'FORMAT',
  'HOME': 'LOCAL', 'GROUP': 'UNITE',
  'HAPPY': 'JOY', 'HONEST': 'TRUST',
  'FINAL': 'COMPLETE', 'OUTCOME': 'RESULT',
  'SMOOTH': 'SUCCESS',
  'DIRECTION': 'PATH', 'CHANNEL': 'CONNECT',
  'FORWARD': 'ASCEND', 'BACKWARD': 'DESCEND',
  'WITHDRAW': 'LEAVE', 'EXCEED': 'OVERFLOW',
  'KEEP': 'PERSIST', 'MAINTAIN': 'CARE',
  'CONTINUE': 'ITERATE',
  'REQUIRE': 'DEPEND', 'SUPPLY': 'RESOURCE',
  'SOURCE': 'ORIGIN', 'BIRTH': 'SPROUT',
  'WAKE': 'TRIGGER', 'VIBRATE': 'SIGNAL',
  'CULTIVATE': 'DEVELOP', 'FORGE': 'BUILD',
  'CONTAIN': 'SUPPORT', 'ELIMINATE': 'CLEAN',
  'GENERATE': 'CREATE', 'SERIALIZE': 'ENCODE',
  'CONVERT': 'TRANSFORM', 'SORT': 'FILTER',
  'REGISTER': 'AUTH', 'ACQUIRE': 'FETCH',
  'NOURISH': 'ENRICH',
  'CONCEAL': 'HIDE', 'LURK': 'HIDE',
  'SECURE': 'PROTECT', 'CONDENSE': 'COMPRESS',
  'COHERE': 'UNITE', 'CONFRONT': 'MONITOR',
  'STABILIZE': 'PERSIST',
  'TERMINATE': 'STOP', 'FINAL': 'COMPLETE',
  'RESERVE': 'BACKUP', 'ACCUMULATE': 'GROW',
  'RECTIFY': 'FIX', 'REFORM': 'REFACTOR',
  'CRASH': 'ERROR', 'FAULT': 'ERROR',
  'STALL': 'PAUSE', 'CLOG': 'BLOCK',
  'DIFFICULTY': 'RISK', 'HARDSHIP': 'RISK',
  'DILEMMA': 'CRISIS', 'POVERTY': 'DEPLETE',
  'LITIGATE': 'CONFLICT', 'DISPUTE': 'CONFLICT',
  'DIVERGE': 'CONFLICT', 'DIFFER': 'SEPARATE',
  'DEVIATE': 'SEPARATE', 'SEPARATE': 'FORK',
  'ADJUDICATE': 'JUDGE', 'OBSTACLE': 'BARRIER',
  'TRAP': 'RISK', 'DANGER': 'CRISIS',
  'COMPETE': 'CONFLICT',
  'DOMINATE': 'LEAD', 'STRONG': 'POWER',
  'FORCE': 'POWER', 'MASSIVE': 'SCALE',
  'VIBRANT': 'GROW', 'STIMULATE': 'TRIGGER',
  'EXPAND': 'SCALE',
  'DATASOURCE': 'SOURCE',
  'KEEPALIVE': 'CONNECT',
  'SELFTEST': 'CHECK',
  'WRITE': 'SAVE', 'READ': 'LOAD',
  'SUBMIT': 'FOLLOW',
  'IO': 'CONNECT',
  'LOWKEY': 'HUMBLE',
  'CENTRALIZE': 'MANAGE',
  'DISPERSE': 'DISPATCH',
  'DISPERSED': 'SEPARATE',
  'BOOT': 'INIT',
  'IMMINENT': 'APPROACH',
  'RANDOM': 'CHANGE',
  'AUTHENTIC': 'INNOCENT',
  'SIGNAL': 'TRIGGER',
  'PROCESS': 'ITERATE',
  'STEP': 'ITERATE',
  'ORGANIZE': 'SORT',
  'REVIVE': 'RESTORE',
  'ESTABLISH': 'CREATE',
  'PERFORM': 'EXEC',
  'PRACTICE': 'EXEC',
  'INTRANET': 'LOCAL',
  'BELONG': 'LOCAL',
  'CONTAIN': 'SUPPORT',
  'CORE': 'INIT',
  'DESTINATION': 'COMPLETE',
  'UNEXPECTED': 'ERROR',
  'EMERGENCY': 'CRISIS',
  'SUPPORT': 'DEPEND',
  'UNIVERSAL': 'INTEGRATE',
  'ENLIGHTEN': 'LEARN',
  'IGNORANT': 'LEARN',
  'EDUCATE': 'TRAIN',
  'CIVILIZE': 'BRIGHT',
  'COORDINATE': 'MANAGE',
  'DISPATCH': 'SCHEDULE',
  'LIBERATE': 'FREE',
  'EASE': 'RELEASE',
  'GUARD': 'PROTECT',
  'DISCONNECT': 'CLOSE',
  'MERGE': 'INTEGRATE',
  'EXCHANGE': 'COMMUNICATE',
  'REACT': 'RESPOND',
  'FACE': 'CONFRONT',
  'PEAK': 'OVERFLOW',
  'OVERLOAD': 'OVERFLOW',
  'COMPUTE': 'ANALYZE',
  'MAP': 'ENCODE',
  'UNFINISHED': 'PENDING',
  'OVERLAY': 'COLLABORATE',
  'IGRATE': 'INTEGRATE',
};

// Count how many would be reduced
const merged = new Set();
Object.values(synonyms).forEach(v => merged.add(v));
console.log('\nSynonyms merge would reduce unique opcodes from ' + usedOpcodes.size + ' to approximately ' + merged.size);
