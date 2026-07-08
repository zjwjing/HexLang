#!/usr/bin/env node

import { Hex64Engine } from '../src/core.js';
import { HEXAGRAMS, TAG_TO_OP } from '../src/database.js';

const B = s => `\x1b[1m${s}\x1b[22m`;
const D = s => `\x1b[2m${s}\x1b[22m`;
const CYAN = s => `\x1b[36m${s}\x1b[39m`;
const GREEN = s => `\x1b[32m${s}\x1b[39m`;
const YELLOW = s => `\x1b[33m${s}\x1b[39m`;
const MAGENTA = s => `\x1b[35m${s}\x1b[39m`;
const RED = s => `\x1b[31m${s}\x1b[39m`;
const BLUE = s => `\x1b[34m${s}\x1b[39m`;
const RESET = '\x1b[0m';

const opTemplates = {
  'INIT':       { js: 'system.init({ mode: \'%s\' });',                 py: 'system.init(mode=\'%s\')' },
  'RUN':        { js: 'process.run(\'%s\');',                           py: 'process.run(\'%s\')' },
  'STOP':       { js: 'process.stop(\'%s\');',                          py: 'process.stop(\'%s\')' },
  'PAUSE':      { js: 'scheduler.pause(\'%s\');',                       py: 'scheduler.pause(\'%s\')' },
  'WAIT':       { js: 'await delay(%d);',                               py: 'await asyncio.sleep(%d)' },
  'ASYNC':      { js: 'await async_task(\'%s\');',                      py: 'await async_task(\'%s\')' },
  'POLL':       { js: 'poll(\'%s\', interval=%d);',                    py: 'poll(\'%s\', interval=%d)' },
  'SAVE':       { js: 'storage.save(\'%s\', data);',                    py: 'storage.save(\'%s\', data)' },
  'CACHE':      { js: 'cache.set(\'%s\', data, TTL=%d);',              py: 'cache.set(\'%s\', data, ttl=%d)' },
  'BACKUP':     { js: 'backup.create(\'%s\');',                         py: 'backup.create(\'%s\')' },
  'STAGE':      { js: 'git.stage(\'%s\');',                             py: 'git.stage(\'%s\')' },
  'BUFFER':     { js: 'buffer.write(data, \'%s\');',                    py: 'buffer.write(data, \'%s\')' },
  'LOAD':       { js: 'import(\'%s\');',                                py: 'import %s' },
  'PREFETCH':   { js: 'prefetch(\'%s\');',                              py: 'prefetch(\'%s\')' },
  'UPDATE':     { js: 'db.update(\'%s\', { ...changes });',             py: 'db.update(\'%s\', **changes)' },
  'UPGRADE':    { js: 'system.upgrade(\'%s\', version);',               py: 'system.upgrade(\'%s\', version)' },
  'REPLACE':    { js: 'config.replace(\'%s\', newValue);',              py: 'config.replace(\'%s\', new_value)' },
  'FLIP':       { js: 'flag = !flag;',                                  py: 'flag = not flag' },
  'REFRESH':    { js: 'ui.refresh();',                                  py: 'ui.refresh()' },
  'RESET':      { js: 'system.reset(\'%s\');',                          py: 'system.reset(\'%s\')' },
  'REBOOT':     { js: 'process.reboot();',                              py: 'process.reboot()' },
  'CLEAN':      { js: 'gc.clean(\'%s\');',                              py: 'gc.clean(\'%s\')' },
  'RECYCLE':    { js: 'resource.recycle(\'%s\');',                      py: 'resource.recycle(\'%s\')' },
  'TRIM':       { js: 'log.trim(maxLines=%d);',                         py: 'log.trim(max_lines=%d)' },
  'COMPRESS':   { js: 'zip.compress(\'%s\');',                          py: 'zip.compress(\'%s\')' },
  'EXEC':       { js: 'exec(\'%s\');',                                  py: 'exec(\'%s\')' },
  'DEPLOY':     { js: 'deploy(\'%s\', env);',                           py: 'deploy(\'%s\', env)' },
  'RELEASE':    { js: 'ci.release(\'%s\', tag);',                       py: 'ci.release(\'%s\', tag)' },
  'BUILD':      { js: 'builder.build(\'%s\');',                         py: 'builder.build(\'%s\')' },
  'CONNECT':    { js: 'client.connect(\'%s\');',                        py: 'client.connect(\'%s\')' },
  'DISCONNECT': { js: 'client.disconnect();',                           py: 'client.disconnect()' },
  'HANDSHAKE':  { js: 'ws.handshake(\'%s\');',                          py: 'ws.handshake(\'%s\')' },
  'COMMUNICATE':{ js: 'channel.send(\'%s\', payload);',                 py: 'channel.send(\'%s\', payload)' },
  'CALLBACK':   { js: 'emitter.on(\'%s\', callback);',                  py: 'emitter.on(\'%s\', callback)' },
  'TRIGGER':    { js: 'event.trigger(\'%s\', data);',                   py: 'event.trigger(\'%s\', data)' },
  'EVENT':      { js: 'bus.emit(\'%s\', payload);',                     py: 'bus.emit(\'%s\', payload)' },
  'BROADCAST':  { js: 'pubsub.broadcast(\'%s\', msg);',                 py: 'pubsub.broadcast(\'%s\', msg)' },
  'NOTIFY':     { js: 'notification.send(\'%s\');',                     py: 'notification.send(\'%s\')' },
  'MESSAGE':    { js: 'queue.send(\'%s\', msg);',                       py: 'queue.send(\'%s\', msg)' },
  'SUBSCRIBE':  { js: 'pubsub.subscribe(\'%s\', handler);',             py: 'pubsub.subscribe(\'%s\', handler)' },
  'LISTEN':     { js: 'server.listen(port, callback);',                 py: 'server.listen(port, callback)' },
  'MONITOR':    { js: 'monitor.watch(\'%s\');',                         py: 'monitor.watch(\'%s\')' },
  'AUDIT':      { js: 'audit.log({ action: \'%s\', user });',           py: 'audit.log(action=\'%s\', user=user)' },
  'CHECK':      { js: 'assert(condition, \'%s\');',                    py: 'assert condition, \'%s\'' },
  'REVIEW':     { js: 'code.review(\'%s\');',                           py: 'code.review(\'%s\')' },
  'VERIFY':     { js: 'validator.verify(\'%s\', input);',               py: 'validator.verify(\'%s\', input)' },
  'AUTH':       { js: 'auth.authenticate(token);',                      py: 'auth.authenticate(token)' },
  'GRANT':      { js: 'rbac.grant(role, \'%s\');',                      py: 'rbac.grant(role, \'%s\')' },
  'TOKEN':      { js: 'jwt.sign({ sub: \'%s\' });',                     py: 'jwt.sign({\'sub\': \'%s\'})' },
  'ANALYZE':    { js: 'analyzer.run(\'%s\', data);',                    py: 'analyzer.run(\'%s\', data)' },
  'CMP':        { js: 'diff(a, b); // compare \'%s\'',                  py: 'diff(a, b)  # compare \'%s\'' },
  'TRAIN':      { js: 'model.train(\'%s\', dataset);',                  py: 'model.train(\'%s\', dataset)' },
  'LEARN':      { js: 'agent.learn(\'%s\', experience);',               py: 'agent.learn(\'%s\', experience)' },
  'EXPLORE':    { js: 'agent.explore(\'%s\');',                         py: 'agent.explore(\'%s\')' },
  'TRAVERSE':   { js: 'tree.traverse(node, visitor);',                  py: 'tree.traverse(node, visitor)' },
  'RECURSE':    { js: 'function recurse(n) { return n<=1 ? 1 : n*recurse(n-1); }', py: 'def recurse(n): return 1 if n<=1 else n*recurse(n-1)' },
  'ITERATE':    { js: 'for (const item of collection) { process(item); }', py: 'for item in collection: process(item)' },
  'INCREMENT':  { js: 'counter += %d;',                                 py: 'counter += %d' },
  'GROW':       { js: 'population.grow(rate=%f);',                      py: 'population.grow(rate=%f)' },
  'ASCEND':     { js: 'stack.push(\'%s\');',                            py: 'stack.append(\'%s\')' },
  'PROMOTE':    { js: 'user.role = \'%s\';',                           py: 'user.role = \'%s\'' },
  'DEVELOP':    { js: 'feature.branch(\'%s\');',                        py: 'feature.branch(\'%s\')' },
  'OPTIMIZE':   { js: 'optimizer.tune(\'%s\', params);',                py: 'optimizer.tune(\'%s\', params)' },
  'ENHANCE':    { js: 'feature.enhance(\'%s\');',                       py: 'feature.enhance(\'%s\')' },
  'SCALE':      { js: 'cluster.scale(%d);',                             py: 'cluster.scale(%d)' },
  'ACCELERATE': { js: 'gpu.accelerate(\'%s\');',                        py: 'gpu.accelerate(\'%s\')' },
  'DECIDE':     { js: 'switch(decision) { case \'%s\': break; }',      py: 'match decision: case \'%s\': pass' },
  'SELECT':     { js: 'const chosen = select(\'%s\', options);',        py: 'chosen = select(\'%s\', options)' },
  'FORK':       { js: 'const child = fork(\'%s\');',                    py: 'child = os.fork()' },
  'CTRL':       { js: 'controller.set(\'%s\', value);',                 py: 'controller.set(\'%s\', value)' },
  'ADJUST':     { js: 'pid.adjust(\'%s\', delta);',                     py: 'pid.adjust(\'%s\', delta)' },
  'REGULATE':   { js: 'regulator.throttle(\'%s\', limit);',             py: 'regulator.throttle(\'%s\', limit)' },
  'THROTTLE':   { js: 'rateLimiter.limit(\'%s\', %d);',                 py: 'rate_limiter.limit(\'%s\', %d)' },
  'SCHEDULE':   { js: 'cron.schedule(\'%s\', task);',                   py: 'cron.schedule(\'%s\', task)' },
  'LOCK':       { js: 'mutex.lock(\'%s\');',                            py: 'mutex.lock(\'%s\')' },
  'UNLOCK':     { js: 'mutex.unlock(\'%s\');',                          py: 'mutex.unlock(\'%s\')' },
  'SUSPEND':    { js: 'thread.suspend(\'%s\');',                        py: 'thread.suspend(\'%s\')' },
  'DONE':       { js: 'callback(null, result);',                        py: 'callback(None, result)' },
  'SUCCESS':    { js: 'console.log(\'✓ %s completed\');',               py: 'print(f\'✓ %s completed\')' },
  'RESTORE':    { js: 'db.restore(\'%s\', snapshot);',                  py: 'db.restore(\'%s\', snapshot)' },
  'ROLLBACK':   { js: 'transaction.rollback();',                        py: 'transaction.rollback()' },
  'RECOVER':    { js: 'system.recover(\'%s\');',                        py: 'system.recover(\'%s\')' },
  'FIX':        { js: 'patch.apply(\'%s\');',                           py: 'patch.apply(\'%s\')' },
  'PATCH':      { js: 'hotfix.deploy(\'%s\');',                         py: 'hotfix.deploy(\'%s\')' },
  'CORRECT':    { js: 'data.correct(\'%s\', errata);',                  py: 'data.correct(\'%s\', errata)' },
  'CALIBRATE':  { js: 'sensor.calibrate(\'%s\');',                      py: 'sensor.calibrate(\'%s\')' },
  'TUNE':       { js: 'params.tune(\'%s\', value);',                    py: 'params.tune(\'%s\', value)' },
  'REFACTOR':   { js: 'refactor(\'%s\').then(deploy);',                py: 'refactor(\'%s\')' },
  'MIGRATE':    { js: 'db.migrate(\'%s\');',                            py: 'db.migrate(\'%s\')' },
  'MOVE':       { js: 'fs.rename(\'%s\', dest);',                       py: 'os.rename(\'%s\', dest)' },
  'MERGE':      { js: 'git.merge(\'%s\');',                             py: 'git.merge(\'%s\')' },
  'SYNC':       { js: 'await sync(\'%s\');',                            py: 'sync(\'%s\')' },
  'COLLECT':    { js: 'gc.collect();',                                  py: 'gc.collect()' },
  'GATHER':     { js: 'const results = await Promise.all(tasks);',      py: 'results = await asyncio.gather(*tasks)' },
  'INTEGRATE':  { js: 'integration.test(\'%s\');',                      py: 'integration.test(\'%s\')' },
  'CREATE':     { js: 'new %s(config).init();',                         py: '%s(config).init()' },
  'INNOVATE':   { js: '// TODO: implement innovation for %s',           py: '# TODO: implement innovation for %s' },
  'ENCODE':     { js: 'encoder.encode(\'%s\', data);',                  py: 'encoder.encode(\'%s\', data)' },
  'DECODE':     { js: 'decoder.decode(\'%s\', buffer);',                py: 'decoder.decode(\'%s\', buffer)' },
  'OUTPUT':     { js: 'console.log(output);',                           py: 'print(output)' },
  'DISPLAY':    { js: 'ui.render(\'%s\', data);',                       py: 'ui.render(\'%s\', data)' },
  'RENDER':     { js: 'ReactDOM.render(<%s />, container);',            py: 'template.render(\'%s\', context)' },
  'FORMAT':     { js: 'formatter.format(\'%s\', input);',               py: 'formatter.format(\'%s\', input)' },
  'PARSE':      { js: 'parser.parse(\'%s\', input);',                   py: 'parser.parse(\'%s\', input)' },
  'FILTER':     { js: 'data.filter(item => item.%s);',                  py: 'filter(lambda x: x.%s, data)' },
  'SEARCH':     { js: 'db.search(\'%s\', query);',                      py: 'db.search(\'%s\', query)' },
  'MATCH':      { js: 'input.match(/pattern/%s/);',                     py: 're.match(r\'pattern_%s\', input)' },
  'LOGIN':      { js: 'session.login(\'%s\', credentials);',            py: 'session.login(\'%s\', credentials)' },
  'LOGOUT':     { js: 'session.logout();',                              py: 'session.logout()' },
  'OPEN':       { js: 'fs.open(\'%s\', \'r\');',                        py: 'open(\'%s\', \'r\')' },
  'CLOSE':      { js: 'connection.close();',                            py: 'connection.close()' },
  'BLOCK':      { js: 'blocker.block(\'%s\', reason);',                 py: 'blocker.block(\'%s\', reason)' },
  'REJECT':     { js: 'return res.status(403).send(\'%s\');',           py: 'return Response(status=403, body=\'%s\')' },
  'ISOLATE':    { js: 'sandbox.run(\'%s\', code);',                     py: 'sandbox.run(\'%s\', code)' },
  'PERSIST':    { js: 'db.persist(\'%s\');',                            py: 'db.persist(\'%s\')' },
  'MAINTAIN':   { js: 'system.maintenance(\'%s\');',                    py: 'system.maintenance(\'%s\')' },
  'HOST':       { js: 'server.host(\'%s\', port);',                     py: 'server.host(\'%s\', port)' },
  'HIDE':       { js: 'element.style.display = \'none\';',              py: 'element.hide()' },
  'PROTECT':    { js: 'helmet(\'%s\');',                                py: 'protect(\'%s\')' },
  'REDUCE':     { js: 'cost.reduce(\'%s\', amount);',                   py: 'cost.reduce(\'%s\', amount)' },
  'END':        { js: 'process.exit(0);',                               py: 'sys.exit(0)' },
  'ARCHIVE':    { js: 'archive.create(\'%s\');',                        py: 'archive.create(\'%s\')' },
  'OBSERVE':    { js: 'observer.observe(target, config);',              py: 'observer.observe(target, config)' },
  'SUPERVISE':  { js: 'supervisor.watch(\'%s\');',                      py: 'supervisor.watch(\'%s\')' },
  'MANAGE':     { js: 'manager.allocate(\'%s\', resources);',           py: 'manager.allocate(\'%s\', resources)' },
  'LEAD':       { js: 'coordinator.elect(\'%s\');',                     py: 'coordinator.elect(\'%s\')' },
  'COLLABORATE':{ js: 'collab.merge(request, response);',               py: 'collab.merge(request, response)' },
  'UNITE':      { js: 'cluster.join(\'%s\');',                          py: 'cluster.join(\'%s\')' },
  'SHARE':      { js: 'cache.share(\'%s\', data);',                     py: 'cache.share(\'%s\', data)' },
  'EXCHANGE':   { js: 'exchange.trade(\'%s\', quote);',                 py: 'exchange.trade(\'%s\', quote)' },
  'INTERACT':   { js: 'ui.on(\'click\', \'%s\', handler);',             py: 'ui.bind(\'click\', \'%s\', handler)' },
  'RESPOND':    { js: 'sensor.on(\'%s\', readings => { ... });',       py: 'sensor.on(\'%s\', lambda r: ...)' },
  'ADAPT':      { js: 'adapter.transform(\'%s\', data);',               py: 'adapter.transform(\'%s\', data)' },
  'FOLLOW':     { js: 'watcher.watch(\'%s\', callback);',               py: 'watcher.watch(\'%s\', callback)' },
  'PROXY':      { js: 'proxy.forward(req, \'%s\');',                    py: 'proxy.forward(req, \'%s\')' },
  'SEND':       { js: 'transport.send(\'%s\', packet);',                py: 'transport.send(\'%s\', packet)' },
  'DISTRIBUTE': { js: 'loadBalancer.distribute(\'%s\', tasks);',        py: 'load_balancer.distribute(\'%s\', tasks)' },
  'SPREAD':     { js: 'gossip.spread(\'%s\', message);',                py: 'gossip.spread(\'%s\', message)' },
  'PERMEATE':   { js: 'agent.infect(\'%s\');',                          py: 'agent.infect(\'%s\')' },
  'CONVERGE':   { js: 'results.reduce((a,b) => a.concat(b), []);',      py: 'sum(results, [])' },
  'APPROACH':   { js: 'client.connect(\'%s\');',                        py: 'client.connect(\'%s\')' },
  'ENTER':      { js: 'vm.enter(\'%s\', context);',                     py: 'vm.enter(\'%s\', context)' },
  'PASS':       { js: 'middleware.pass(\'%s\');',                        py: 'middleware.pass(\'%s\')' },
  'ENCOUNTER':  { js: 'discovery.find(\'%s\');',                        py: 'discovery.find(\'%s\')' },
  'JOIN':       { js: 'network.join(\'%s\');',                          py: 'network.join(\'%s\')' },
  'LEAVE':      { js: 'network.leave(\'%s\');',                         py: 'network.leave(\'%s\')' },
  'RETREAT':    { js: 'deployment.rollback(\'%s\');',                   py: 'deployment.rollback(\'%s\')' },
  'RISK':       { js: 'risk.assess(\'%s\');',                           py: 'risk.assess(\'%s\')' },
  'ERROR':      { js: 'throw new Error(\'%s\');',                      py: 'raise Exception(\'%s\')' },
  'EXCEPTION':  { js: 'try { ... } catch(e) { logger.error(e); }',      py: 'try: ... except Exception as e: logger.error(e)' },
  'CONFLICT':   { js: 'git.conflict(\'%s\'); // resolve manually',      py: 'git.conflict(\'%s\')  # resolve manually' },
  'CHANGE':     { js: 'state.transition(\'%s\');',                      py: 'state.transition(\'%s\')' },
  'TRANSFORM':  { js: 'transformer.transform(\'%s\', data);',           py: 'transformer.transform(\'%s\', data)' },
  'PRIMITIVE':  { js: '// %s is a primitive type',                      py: '# %s is a primitive type' },
  'POWER':      { js: 'cluster.scaleUp(%d);',                           py: 'cluster.scale_up(%d)' },
  'SLEEP':      { js: 'await new Promise(r => setTimeout(r, %d));',     py: 'await asyncio.sleep(%d)' },
  'HUMBLE':     { js: 'logger.info(\'%s\')\n// keep低调',                py: 'logger.info(\'%s\')\n# keep 低调' },
  'WITHDRAW':   { js: 'service.deregister(\'%s\');',                    py: 'service.deregister(\'%s\')' },
  'DEPEND':     { js: 'import { %s } from \'dependency\';',             py: 'from dependency import %s' },
  'RESOURCE':   { js: 'pool.acquire(\'%s\');',                          py: 'pool.acquire(\'%s\')' },
  'NOURISH':    { js: 'scheduler.feed(\'%s\', interval);',              py: 'scheduler.feed(\'%s\', interval)' },
  'GAIN':       { js: 'profit.calculate(\'%s\');',                      py: 'profit.calculate(\'%s\')' },
  'ACCUMULATE': { js: 'buffer.accumulate(\'%s\', chunk);',              py: 'buffer.accumulate(\'%s\', chunk)' },
  'STORE':      { js: 'localStorage.setItem(\'%s\', value);',           py: 'os.environ[\'%s\'] = value' },
  'ENRICH':     { js: 'data.enrich(\'%s\', source);',                   py: 'data.enrich(\'%s\', source)' },
  'EXCEED':     { js: 'if (value > limit) { alert(\'%s\' exceeded); }', py: 'if value > limit: alert(\'%s\' exceeded)' },
  'OVERFLOW':   { js: 'buffer.write(data); // check bounds!',           py: 'buffer.write(data)  # check bounds!' },
  'PEAK':       { js: 'autoScaling.setMax(%d);',                        py: 'auto_scaling.set_max(%d)' },
  'PENDING':    { js: '// TODO: %s is pending implementation',           py: '# TODO: %s is pending implementation' },
  'TODO':       { js: '// FIXME: %s not yet implemented',                py: '# FIXME: %s not yet implemented' },
  'INTERNAL':   { js: '// internal API — do not expose',                py: '# internal API — do not expose' },
  'LOCAL':      { js: 'const %s = require(\'./local\');',               py: 'from . import %s as local' },
  'PRIVATE':    { js: 'class %s { #privateField; }',                    py: 'class %s: __private_field' },
  'JOY':        { js: 'console.log(\'🎉 %s\');',                         py: 'print(\'🎉 %s\')' },
  'SMOOTH':     { js: 'animation.ease(\'%s\', duration);',              py: 'animation.ease(\'%s\', duration)' },
  'PEACE':      { js: 'cluster.quiesce(\'%s\');',                       py: 'cluster.quiesce(\'%s\')' },
  'HARMONY':    { js: 'version.resolve(\'%s\');',                       py: 'version.resolve(\'%s\')' },
  'RANDOM':     { js: 'Math.random() > 0.5 ? \'%s\' : fallback',        py: 'random.choice([\'%s\', fallback])' },
  'TRUST':      { js: 'cert.verify(\'%s\');',                           py: 'cert.verify(\'%s\')' },
  'HONEST':     { js: '// invariant: %s must be truthful',              py: '# invariant: %s must be truthful' },
  'CONTAIN':    { js: 'container.add(\'%s\', item);',                     py: 'container.add(\'%s\', item)' },
  'GENTLE':     { js: 'smooth.defer(\'%s\');',                            py: 'smooth.defer(\'%s\')' },
  'PASSIVE':    { js: 'listener.passive(\'%s\', handler);',               py: 'listener.passive(\'%s\', handler)' },
  'STABILIZE':  { js: 'circuitBreaker.stabilize(\'%s\');',                py: 'circuit_breaker.stabilize(\'%s\')' },
  'DECAY':      { js: 'ttl.decay(\'%s\', factor);',                       py: 'ttl.decay(\'%s\', factor)' },
  'ELIMINATE':  { js: 'cache.evict(\'%s\');',                             py: 'cache.evict(\'%s\')' },
  'ALLY':       { js: 'cluster.ally(\'%s\');',                            py: 'cluster.ally(\'%s\')' },
  'COOPERATE':  { js: 'semaphore.cooperate(\'%s\', tasks);',              py: 'semaphore.cooperate(\'%s\', tasks)' },
  'ALLIANCE':   { js: 'federation.join(\'%s\');',                         py: 'federation.join(\'%s\')' },
  'INSPECT':    { js: 'inspector.check(\'%s\');',                         py: 'inspector.check(\'%s\')' },
  'PREPARE':    { js: 'env.prepare(\'%s\');',                             py: 'env.prepare(\'%s\')' },
  'PLAN':       { js: 'scheduler.plan(\'%s\', cron);',                    py: 'scheduler.plan(\'%s\', cron)' },
  'READY':      { js: 'health.ready(\'%s\');',                            py: 'health.ready(\'%s\')' },
  'ENLIGHTEN':  { js: 'tutorial.show(\'%s\');',                           py: 'tutorial.show(\'%s\')' },
  'EDUCATE':    { js: 'trainer.educate(\'%s\', data);',                   py: 'trainer.educate(\'%s\', data)' },
  'DANGER':     { js: 'alert.danger(\'%s\');',                            py: 'alert.danger(\'%s\')' },
  'CRISIS':     { js: 'emergency.handler(\'%s\');',                       py: 'emergency.handler(\'%s\')' },
  'FAULT':      { js: 'fault.detector(\'%s\');',                          py: 'fault.detector(\'%s\')' },
  'CONTINUE':   { js: 'loop.continue(\'%s\');',                           py: 'loop.continue(\'%s\')' },
  'UNFINISHED': { js: '// %s: pending completion',                        py: '# %s: pending completion' },
  'RECTIFY':    { js: 'linter.fix(\'%s\');',                              py: 'linter.fix(\'%s\')' },
  'REFORM':     { js: 'migration.reform(\'%s\', schema);',                py: 'migration.reform(\'%s\', schema)' },
  'SUPPLY':     { js: 'supply.chain(\'%s\', inventory);',                 py: 'supply.chain(\'%s\', inventory)' },
  'SOURCE':     { js: 'datasource.register(\'%s\');',                     py: 'datasource.register(\'%s\')' },
  'COMPLY':     { js: 'policy.enforce(\'%s\');',                          py: 'policy.enforce(\'%s\')' },
  'KEEP':       { js: 'heartbeat.keep(\'%s\');',                          py: 'heartbeat.keep(\'%s\')' },
  'PERMANENT':  { js: 'storage.makePermanent(\'%s\');',                   py: 'storage.make_permanent(\'%s\')' },
  'ESTABLISH':  { js: 'foundation.establish(\'%s\');',                    py: 'foundation.establish(\'%s\')' },
  'BIRTH':      { js: 'lifecycle.birth(\'%s\');',                         py: 'lifecycle.birth(\'%s\')' },
  'SPROUT':     { js: 'sprout(\'%s\', seed);',                            py: 'sprout(\'%s\', seed)' },
  'BOOT':       { js: 'system.boot(\'%s\');',                             py: 'system.boot(\'%s\')' },
  'STIMULATE':  { js: 'event.emit(\'stimulus.%s\');',                     py: 'event.emit(\'stimulus.%s\')' },
  'WAKE':       { js: 'scheduler.wake(\'%s\');',                          py: 'scheduler.wake(\'%s\')' },
  'INNOCENT':   { js: '// %s: clean slate — no assumptions',             py: '# %s: clean slate — no assumptions' },
  'UNEXPECTED': { js: 'catch((err) => { logger.warn(\'%s\', err); });',   py: 'except: logger.warn(\'%s\', err)' },
  'CONCEAL':    { js: 'config.conceal(\'%s\');',                          py: 'config.conceal(\'%s\')' },
  'ENDURE':     { js: 'retry.withBackoff(\'%s\');',                       py: 'retry.with_backoff(\'%s\')' },
  'DECORATE':   { js: 'decorator.apply(\'%s\', target);',                 py: 'decorator.apply(\'%s\', target)' },
  'BEAUTIFY':   { js: 'code.formatter(\'%s\');',                          py: 'code.formatter(\'%s\')' },
  'COMPLETE':   { js: 'promise.resolve(\'%s\');',                         py: 'promise.resolve(\'%s\')' },
  'HOME':       { js: 'cwd = \'%s\';',                                   py: 'os.chdir(\'%s\')' },
  'ABUNDANT':   { js: 'pool.expand(\'%s\', limit);',                      py: 'pool.expand(\'%s\', limit)' },
  'BRIGHT':     { js: 'theme.set(\'light\', \'%s\');',                    py: 'theme.set(\'light\', \'%s\')' },
  'FINAL':      { js: 'finalize(\'%s\');',                                py: 'finalize(\'%s\')' },
  'PERFORM':    { js: 'benchmark.run(\'%s\');',                           py: 'benchmark.run(\'%s\')' },
  'STRONG':     { js: 'consistency.strong(\'%s\');',                      py: 'consistency.strong(\'%s\')' },
  'DECISIVE':   { js: 'breaker.trip(\'%s\', threshold);',                 py: 'breaker.trip(\'%s\', threshold)' },
  'CORE':       { js: '// %s: core system — do not modify',              py: '# %s: core system — do not modify' },
  'DOMINATE':   { js: 'leader.elect(\'%s\');',                            py: 'leader.elect(\'%s\')' },
};

function compileHex(hex) {
  const ops = [...new Set(hex.tags.map(t => TAG_TO_OP[t] || t.toUpperCase()))];
  const param = hex.name || 'system';
  const linesJS = ops.map(op => {
    const tpl = opTemplates[op];
    if (!tpl) return `${op.toLowerCase()}('${param}');`;
    let code = tpl.js.replace(/%s/g, param).replace(/%d/g, '60').replace(/%f/g, '1.5');
    return code;
  });
  const linesPY = ops.map(op => {
    const tpl = opTemplates[op];
    if (!tpl) return `${op.toLowerCase()}('${param}')`;
    let code = tpl.py.replace(/%s/g, param).replace(/%d/g, '60').replace(/%f/g, '1.5');
    return code;
  });
  return {
    name: hex.name,
    js: `// HexLang → JS  ·  ${hex.name}  (${hex.bin})\n${linesJS.map(l => '  ' + l).join('\n')}`,
    py: `# HexLang → Python  ·  ${hex.name}  (${hex.bin})\n${linesPY.map(l => '  ' + l).join('\n')}`
  };
}

function formatOutput(input, r, compiled, jsonMode) {
  if (jsonMode) {
    return JSON.stringify({ input, ...r.hexCode, featureVec: r.featureVec, pseudoCode: r.pseudoCode, controlSignal: r.controlSignal, compiledJS: compiled.js, compiledPY: compiled.py }, null, 2);
  }
  const hc = r.hexCode;
  const sep = D('\u2500'.repeat(50));
  let out = '';
  out += `\n${B(' \u250C\u2500\u2500 Hex64 Engine')} ${D('\u2500'.repeat(35))}\n`;
  out += ` ${B('\u2502')} ${CYAN('Input:')} ${B(hc.name)} ${D(`(${input})`)}\n`;
  out += ` ${B('\u2502')} ${CYAN('Hexagram:')} ${YELLOW(hc.bin)} ${B(`\u2022 ${hc.name}`)} ${D(`(${hc.pinyin})`)}\n`;
  out += ` ${B('\u2502')} ${D(hc.en)}\n`;
  out += ` ${B('\u2502')} ${CYAN('Index:')} ${hc.index}  ${CYAN('Weight:')} ${hc.weight}  ${CYAN('Category:')} ${hc.category}\n`;
  out += ` ${B('\u2514')}${D('\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500')}\n`;
  out += ` ${CYAN('Feature:')} [${r.featureVec.map(v => v ? GREEN(v) : D(v)).join(', ')}]\n`;
  out += ` ${CYAN('GPIO:')}    ${r.controlSignal.map(s => s === 'ON' ? GREEN(B('ON')) : RED('OFF')).join(' | ')}\n`;
  out += ` ${CYAN('Tags:')}    ${hc.tags.join(', ')}\n`;
  out += `\n ${MAGENTA('HexLang:')} ${r.pseudoCode}\n`;
  out += `\n ${BLUE('JavaScript:')}\n${compiled.js.split('\n').map(l => `   ${l}`).join('\n')}\n`;
  out += `\n ${BLUE('Python:')}\n${compiled.py.split('\n').map(l => `   ${l}`).join('\n')}\n`;
  return out;
}

function formatOpOutput(opResult, jsonMode) {
  if (jsonMode) {
    return JSON.stringify(opResult, null, 2);
  }
  const i = opResult.input;
  const r = opResult.result;
  const sep = D('\u2500'.repeat(50));
  let out = '';
  out += `\n${B(' \u250C\u2500\u2500 Hex64 Operation')} ${D('\u2500'.repeat(32))}\n`;
  out += ` ${B('\u2502')} ${CYAN('Op:')} ${B(opResult.op)}  ${D('- ')}\n`;
  out += ` ${B('\u2502')} ${CYAN('Input:')} ${YELLOW(i.bin)} ${B(i.name)} ${D(`(${i.en})`)}\n`;
  out += ` ${B('\u2502')} ${CYAN('Result:')} ${YELLOW(opResult.resultBin)} ${B(r.name)} ${D(`(${r.en})`)}\n`;
  if (r.bin) {
    const compiled = compileHex(r);
    out += ` ${B('\u2514')}${D('\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500')}\n`;
    out += ` ${BLUE('JavaScript:')}\n${compiled.js.split('\n').map(l => `   ${l}`).join('\n')}\n`;
    out += `\n ${BLUE('Python:')}\n${compiled.py.split('\n').map(l => `   ${l}`).join('\n')}\n`;
  }
  return out;
}

function processInput(engine, input, opFlag, jsonMode) {
  if (opFlag) {
    const opResult = engine.operate(opFlag, input);
    return formatOpOutput(opResult, jsonMode);
  }
  const r = engine.tranceive(input);
  const compiled = compileHex(r.hexCode);
  return formatOutput(input, r, compiled, jsonMode);
}

function processOpInput(engine, op, input, secondInput, jsonMode) {
  const opResult = engine.operate(op, input, secondInput);
  if (jsonMode) return JSON.stringify(opResult, null, 2);
  return formatOpOutput(opResult, jsonMode);
}

function usage() {
  console.log(`Usage:
  node bin/hex64.js <text>...
  echo <text> | node bin/hex64.js
  node bin/hex64.js --op <cuo|zong|bian|AND|OR|XOR> <text> [secondText]
  node bin/hex64.js --json <text>...
Options:
  --op <op>   Hexagram operation: cuo, zong, bian, AND, OR, XOR
  --json      JSON output (machine-readable)
  --help      Show this help`);
}

const args = process.argv.slice(2);
if (args.includes('--help') || args.includes('-h')) {
  usage();
  process.exit(0);
}

let opFlag = null;
let jsonMode = false;
let positional = [];

for (let i = 0; i < args.length; i++) {
  if (args[i] === '--op') {
    opFlag = args[++i];
  } else if (args[i] === '--json') {
    jsonMode = true;
  } else if (args[i] === '--help' || args[i] === '-h') {
    usage();
    process.exit(0);
  } else {
    positional.push(args[i]);
  }
}

const engine = new Hex64Engine();

if (positional.length > 0) {
  if (opFlag && (opFlag === 'AND' || opFlag === 'OR' || opFlag === 'XOR')) {
    const primary = positional[0];
    const secondary = positional[1];
    const output = processOpInput(engine, opFlag, primary, secondary, jsonMode);
    console.log(output);
  } else if (opFlag && opFlag === 'bian') {
    const primary = positional[0];
    const secondary = positional[1];
    const output = processOpInput(engine, opFlag, primary, secondary, jsonMode);
    console.log(output);
  } else {
    for (const input of positional) {
      if (opFlag) {
        const output = processInput(engine, input, opFlag, jsonMode);
        console.log(output);
      } else {
        const r = engine.tranceive(input);
        const compiled = compileHex(r.hexCode);
        console.log(formatOutput(input, r, compiled, jsonMode));
      }
    }
  }
} else if (!process.stdin.isTTY) {
  let buffer = '';
  process.stdin.setEncoding('utf-8');
  process.stdin.on('data', chunk => { buffer += chunk; });
  process.stdin.on('end', () => {
    const lines = buffer.split('\n').filter(l => l.trim());
    for (const line of lines) {
      const input = line.trim();
      if (!input) continue;
      if (opFlag && (opFlag === 'AND' || opFlag === 'OR' || opFlag === 'XOR')) {
        const parts = input.split(/\s+/);
        const primary = parts[0];
        const secondary = parts[1];
        console.log(processOpInput(engine, opFlag, primary, secondary, jsonMode));
      } else {
        console.log(processInput(engine, input, opFlag, jsonMode));
      }
    }
  });
} else {
  usage();
}
