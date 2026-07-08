import { readFileSync, writeFileSync } from 'fs';

const SPECIAL = {
  INIT: { rs: 'system::init(mode: "%s");', go: 'system.Init(map[string]string{"mode": "%s"})' },
  UPDATE: { rs: 'db::update("%s", changes);', go: 'db.Update("%s", map[string]any{})' },
  AUDIT: { rs: 'audit::log(action: "%s");', go: 'audit.Log(action: "%s")' },
  TOKEN: { rs: 'jwt::sign(sub: "%s");', go: 'jwt.Sign(map[string]any{"sub": "%s"})' },
  RECURSE: { rs: 'fn recurse(n: u32) -> u32 { if n <= 1 { 1 } else { n * recurse(n-1) } }', go: 'func recurse(n int) int { if n <= 1 { return 1 }; return n * recurse(n-1) }' },
  ITERATE: { rs: 'for item in collection { process(item); }', go: 'for _, item := range collection { process(item) }' },
  DECIDE: { rs: 'match decision { "%s" => { break; } }', go: 'switch decision { case "%s": break }' },
  RESPOND: { rs: 'sensor.on("%s", |readings| { ... });', go: 'sensor.On("%s", func(readings any) { ... })' },
  EXCEPTION: { rs: 'match err { _ => warn!("%s", err) }', go: 'if err != nil { log.Printf("%s", err) }' },
  DEPEND: { rs: 'use dependency::%s;', go: 'import "dependency/packages/%s"' },
  EXCEED: { rs: 'if value > limit { warn!("%s exceeded"); }', go: 'if value > limit { log.Warnf("%s exceeded") }' },
  PRIVATE: { rs: '// %s: private — unexported field', go: '// %s: private — lower-case unexported' },
  UNEXPECTED: { rs: 'catch_err!(warn!("%s", err));', go: 'if err != nil { log.Printf("%s", err) }' },
  TEST: { rs: '#[test]\nfn test_%s() { todo!(); }', go: 'func Test%s(t *testing.T) { t.Skip("TODO") }' },
  RANDOM: { rs: 'rand::random::<f64>() > 0.5 { "%s" } else { fallback };', go: 'if rand.Float64() > 0.5 { "%s" } else { fallback }' },
  JOY: { rs: 'println!("🎉 %s");', go: 'fmt.Println("🎉 %s")' },
  ERROR: { rs: 'panic!("%s");', go: 'errors.New("%s")' },
  SLEEP: { rs: 'tokio::time::sleep(Duration::from_millis(%d)).await;', go: 'time.Sleep(%d * time.Millisecond)' },
  WAIT: { rs: 'delay(%d).await;', go: 'delay(%d)' },
  COPY: { rs: 'fs::copy("%s", dest);', go: 'fs.Copy("%s", dest)' },
   DESCEND: { rs: 'stack::pop("%s");', go: 'stack.Pop("%s")' },
  INPUT: { rs: 'io::stdin().read_line(&mut "%s");', go: 'fmt.Scan("%s")' },
  STORE: { rs: 'std::env::set_var("%s", value);', go: 'os.Setenv("%s", value)' },
  LOCAL: { rs: 'mod %s;', go: 'import "./%s"' },
  COMPLY: { rs: 'policy::enforce("%s");', go: 'policy.Enforce("%s")' },
  DISCONNECT: { rs: 'client::disconnect();', go: 'client.Disconnect()' },
  GRANT: { rs: 'rbac::grant(role, "%s");', go: 'rbac.Grant(role, "%s")' },
  FREE: { rs: 'memory::free("%s");', go: 'memory.Free("%s")' },
  HIDE: { rs: 'element::hide();', go: 'element.Hide()' },
  END: { rs: 'process::exit(0);', go: 'os.Exit(0)' },
  COLLECT: { rs: 'gc::collect();', go: 'gc.Collect()' },
  CONVERGE: { rs: 'results::reduce(...);', go: 'collapse(results)' },
  FLIP: { rs: 'flag = !flag;', go: 'flag = !flag' },
  AUTH: { rs: 'auth::authenticate(token);', go: 'auth.Authenticate(token)' },
  CHECK: { rs: 'assert!(condition, "%s");', go: 'assert(condition, "%s")' },
  VERIFY: { rs: 'validator::verify("%s", input);', go: 'validator.Verify("%s", input)' },
  CALLBACK: { rs: 'emitter::on("%s", callback);', go: 'emitter.On("%s", callback)' },
  SORT: { rs: 'data::sort_by(|a, b| a.%s.cmp(&b.%s));', go: 'sort.Slice(data, func(i, j int) bool { return data[i].%s < data[j].%s })' },
  MAP: { rs: 'data::iter().map(|item| item.%s).collect()', go: 'Map(data, func(item) { return item.%s })' },
  GATHER: { rs: 'futures::future::join_all(tasks).await', go: 'JoinTasks(tasks)' },
  CORE: { rs: '// %s: core system — do not modify', go: '// %s: core system — do not modify' },
  INTERNAL: { rs: '// internal API — do not expose', go: '// internal API — do not expose' },
  INNOCENT: { rs: '// %s: clean slate — no assumptions', go: '// %s: clean slate — no assumptions' },
  HONEST: { rs: '// invariant: %s must be truthful', go: '// invariant: %s must be truthful' },
  STATELESS: { rs: '// %s is stateless — no side effects', go: '// %s is stateless — no side effects' },
  GRAND: { rs: '// grand plan: %s', go: '// grand plan: %s' },
  DILEMMA: { rs: '// dilemma: %s — requires tradeoff', go: '// dilemma: %s — requires tradeoff' },
  PENDING: { rs: '// TODO: %s is pending implementation', go: '// TODO: %s is pending implementation' },
  TODO: { rs: '// FIXME: %s not yet implemented', go: '// FIXME: %s not yet implemented' },
  UNFINISHED: { rs: 'linter::fix("%s");', go: 'linter.Fix("%s")' },
  IGNORANT: { rs: '// ignorant of %s — add logging', go: '// ignorant of %s — add logging' },
  SERIALIZE: { rs: 'serde_json::to_string(%s);', go: 'json.Marshal(%s)' },
  REJECT: { rs: 'return Err(Forbidden("%s"));', go: 'return http.StatusForbidden(Response("%s"))' },
  PUBLISH: { rs: 'crates::io::publish("%s");', go: 'go_releases.Publish("%s")' },
  FORK: { rs: 'std::process::Command::new("%s").spawn()?;', go: 'exec.Command("%s").Start()' },
   DECORATE: { rs: 'attribute::apply("%s", target);', go: 'decorator.Apply("%s", target)' },
   INTEGRATE: { rs: 'new %s(config).init();', go: 'new %s(config).Init()' },
   PRIMITIVE: { rs: 'cluster::scale_up(%d);', go: 'cluster.ScaleUp(%d)' },
   ACCUMULATE: { rs: 'localStorage::set_item("%s", value);', go: 'localStorage.SetItem("%s", value)' },
   OVERFLOW: { rs: 'autoScaling::set_max(%d);', go: 'autoScaling.SetMax(%d)' },
   KEEP: { rs: 'storage::make_permanent("%s");', go: 'storage.MakePermanent("%s")' },
    CONCEAL: { rs: 'retry::with_backoff("%s");', go: 'retry.WithBackoff("%s")' },
    BLOCK: { rs: 'return res::status(403).send("%s");', go: 'return res.Status(403).Send("%s")' },
    REFACTOR: { rs: 'refactor::apply("%s").await;', go: 'refactor.Apply("%s")' },
 };

function toRust(js) {
  let r = js;
  r = r.replace(/console\.log\(/g, 'println!(');
  r = r.replace(/console\.show\(/g, 'println!(');
  r = r.replace(/throw new Error\((.*?)\)/g, 'panic!($1)');
  r = r.replace(/\bnull\b/g, 'None');
  r = r.replace(/\bundefined\b/g, 'None');
  r = r.replace(/\.length\b/g, '.len()');
  r = r.replace(/JSON\.stringify\(/g, 'serde_json::to_string(');
  r = r.replace(/import \{ /g, 'use ');
  r = r.replace(/\} from '/g, '::');
  r = r.replace(/require\(/g, 'use(');
  r = r.replace(/new Promise\(r => setTimeout\(r, %d\)\)/g, 'tokio::time::sleep(Duration::from_millis(%d)).await');
  r = r.replace(/`/g, '');
  r = r.replace(/emitter\.on\(/g, 'emitter::on(');
  r = r.replace(/event\.emit\(/g, 'bus::emit(');
  r = r.replace(/bus\.emit\(/g, 'bus::emit(');
  r = r.replace(/===/g, '==');
  r = r.replace(/!==/g, '!=');
  r = r.replace(/'([^']*)'/g, '"$1"');
  r = r.replace(/([a-zA-Z_]\w*)\.([a-zA-Z_]\w*)(\s*[(<])/g, '$1::$2$3');
  const t = r.trimEnd();
  if (!t.endsWith(';') && !t.includes('//') && !t.endsWith('}') && !t.endsWith('{') && t.length > 0) r = t + ';';
  r = r.replace(/;;/g, ';');
  return r;
}

function toGo(js) {
  let g = js;
  g = g.replace(/console\.log\(/g, 'fmt.Println(');
  g = g.replace(/console\.show\(/g, 'fmt.Println(');
  g = g.replace(/throw new Error\((.*?)\)/g, 'errors.New($1)');
  g = g.replace(/\bnull\b/g, 'nil');
  g = g.replace(/\bundefined\b/g, 'nil');
  g = g.replace(/\.length\b/g, '');
  g = g.replace(/JSON\.stringify\(/g, 'json.Marshal(');
  g = g.replace(/import \{ /g, 'import "');
  g = g.replace(/\} from '/g, '"');
  g = g.replace(/require\(/g, 'import(');
  g = g.replace(/new Promise\(r => setTimeout\(r, %d\)\)/g, 'time.Sleep(%d * time.Millisecond)');
  g = g.replace(/await /g, 'go ');
  g = g.replace(/\.then\(/g, ' // then ');
  g = g.replace(/emitter\.on\(/g, 'emitter.On(');
  g = g.replace(/event\.emit\(/g, 'bus.Publish(');
  g = g.replace(/bus\.emit\(/g, 'bus.Publish(');
  g = g.replace(/===/g, '==');
  g = g.replace(/!==/g, '!=');
  g = g.replace(/`/g, '');
  g = g.replace(/'([^']*)'/g, '"$1"');
  g = g.replace(/([a-zA-Z_]\w*)\.([a-zA-Z_]\w*)(\s*\()/g, (m, obj, method, paren) => 
    obj + '.' + method.charAt(0).toUpperCase() + method.slice(1) + paren);
  if (g.endsWith(';')) g = g.slice(0, -1);
  return g;
}

function extractBlock(text) {
  const start = text.indexOf('opTemplates = {');
  if (start < 0) throw new Error('opTemplates not found');
  const braceStart = text.indexOf('{', start);
  let depth = 1, pos = braceStart + 1;
  while (depth > 0 && pos < text.length) {
    if (text[pos] === '{') depth++;
    if (text[pos] === '}') depth--;
    pos++;
  }
  // consume trailing semicolons  
  while (pos < text.length && text[pos] === ';') pos++;
  return {
    fullText: text.slice(start, pos),
    inner: text.slice(braceStart + 1, pos - 1),
    prefix: text.slice(start, braceStart + 1),
    hasConst: text.slice(start, start + 6) === 'const '
  };
}

function rebuildFile(filePath) {
  const content = readFileSync(filePath, 'utf-8');
  const block = extractBlock(content);
  
  const entries = [];
  const lines = block.inner.split('\n');
  
  for (let i = 0; i < lines.length; i++) {
    const line = lines[i];
    const nameMatch = line.match(/^\s*'(\w+)':\s*\{/);
    if (!nameMatch) continue;
    const name = nameMatch[1];
    
    let entryText = line;
    // If the current line already closes the entry (single-line), use it as-is
    if (!/},\s*$/.test(entryText)) {
      let j = i + 1;
      while (j < lines.length) {
        const nl = lines[j];
        if (/^\s*'\w+':\s*\{/.test(nl)) break; // next entry starts
        entryText += '\n' + nl;
        if (/},\s*$/.test(nl)) break;
        j++;
      }
    }
    
    const kv = {};
    const valRegex = /(\w+):\s*'((?:[^'\\]|\\.)*)'/g;
    let km;
    while ((km = valRegex.exec(entryText)) !== null) {
      if (!kv[km[1]]) {  // only take first occurrence (avoids spill from next entry)
        kv[km[1]] = km[2].replace(/\\'/g, "'");
      }
    }
    
    if (kv.js) {
      if (SPECIAL[name]) {
        kv.rs = SPECIAL[name].rs;
        kv.go = SPECIAL[name].go;
      } else {
        kv.rs = toRust(kv.js);
        kv.go = toGo(kv.js);
      }
    }
    entries.push({ name, ...kv });
  }
  
  console.log(`${filePath}: parsed ${entries.length} entries`);
  
  let newBlock = block.prefix + '\n';
  for (const e of entries) {
    const esc = s => s.replace(/'/g, "\\'").replace(/\n/g, '\\n');
    const js = esc(e.js);
    const py = esc(e.py || '');
    const rs = esc(e.rs || '');
    const go = esc(e.go || '');
    newBlock += `  '${e.name}':     { js: '${js}',                           py: '${py}',                           rs: '${rs}',                          go: '${go}' },\n`;
  }
  newBlock += '};\n';
  
  const idx = content.indexOf(block.fullText);
  const updatedContent = content.slice(0, idx) + newBlock + content.slice(idx + block.fullText.length);
  writeFileSync(filePath, updatedContent, 'utf-8');
  
  // Verify with brace counting
  const v = readFileSync(filePath, 'utf-8');
  const vb = extractBlock(v);
  const names = [...vb.inner.matchAll(/'(\w+)':/g)].map(x => x[1]);
  console.log(`  verified: ${names.length} total`);
  let missRS = 0, missGO = 0;
  for (const name of names) {
    const idx = vb.inner.indexOf(`'${name}':`);
    const snippet = vb.inner.slice(idx, idx + 500);
    if (!snippet.includes('rs:')) missRS++;
    if (!snippet.includes('go:')) missGO++;
  }
  console.log(`  missing rs: ${missRS}, missing go: ${missGO}`);
}

rebuildFile('src/engine.html');
rebuildFile('bin/hex64.js');
