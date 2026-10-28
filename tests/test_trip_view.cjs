// Behavioral tests in an isolated JS runtime, not a substitute for browser/device QA.
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');
const test = require('node:test');
const script = fs.readFileSync(path.join(__dirname, '../skill/travel-os/assets/trip-view.js'), 'utf8');

function run(items, {now = Date.parse('2030-05-01T03:00:00Z'), clipboard, details = []} = {}) {
  const elements = new Map();
  const get = id => {
    if (!elements.has(id)) elements.set(id, {textContent:'', value:'', hidden:false, dataset:{}, listeners:{},
      addEventListener(name, fn) {this.listeners[name] = fn;}, focus(){this.focused = true;}, select(){this.selected = true;}});
    return elements.get(id);
  };
  const labels = {complete:'empty', unscheduled:'check time', first:'selected date', live:'local today', continuing:'overnight underway', nextday:'next day', blocked:'blocked', overdue:'overdue',
    manual:'copy manually', copied:'copied', dayempty:'no activity today', requesttext:'version={version}; scope={scope}', requestdone:'request copied', all:'all dates'};
  get('trip-data').textContent = JSON.stringify({trip:{items, version:'v0.1.1'}, labels, statuses:{}});
  const days = [...new Set(items.map(item => item.date))].map(date => ({dataset:{date}, hidden:false}));
  const button = get('copy-place'); button.dataset.copy = '上海虹桥站';
  let printCalls = 0;
  const events = {};
  let tick;
  class Clock extends Date { static now() {return now;} }
  const context = {Date:Clock, Intl, JSON, navigator:{clipboard}, window:{print(){printCalls++;}, addEventListener(name, fn){events[name] = fn;}}, setInterval(fn){tick = fn;},
    document:{getElementById:get, querySelectorAll(selector){return selector === '.day' ? days : selector === '.copy-place' ? [button] : selector === 'details:not([hidden])' ? details : [];}}};
  vm.runInNewContext(script, context);
  return {get, days, printCalls:()=>printCalls, events, advance(instant){now = Date.parse(instant); tick();}};
}
const item = (patch = {}) => ({id:'1', date:'2030-05-01', start:'10:00', end:'11:00', zone:'Asia/Shanghai', city:'上海', activity:'Walk', location:'公园', transport:'步行', status:'Ready', start_epoch:Date.parse('2030-05-01T02:00:00Z'), end_epoch:Date.parse('2030-05-01T03:00:00Z'), ...patch});

test('initial date and today follow destination local date, not device time', () => {
  const ui = run([item()], {now:Date.parse('2030-04-30T16:30:00Z')});
  assert.equal(ui.get('day-select').value, '2030-05-01');
  assert.equal(ui.get('next-context').textContent, 'local today');
  ui.get('today').listeners.click();
  assert.equal(ui.get('feedback').textContent, '');
});
test('date filter keeps all source sections and restores all dates', () => {
  const ui = run([item(), item({id:'2', date:'2030-05-02'})]);
  ui.get('day-select').value = '2030-05-02'; ui.get('day-select').listeners.change();
  assert.deepEqual(ui.days.map(day => day.hidden), [true,false]);
  ui.get('day-select').value = 'all'; ui.get('day-select').listeners.change();
  assert.deepEqual(ui.days.map(day => day.hidden), [false,false]);
});
test('completed and skipped items do not become next actions', () => {
  const ui = run([item({status:'Done'}), item({id:'2', status:'Skipped'})]);
  assert.equal(ui.get('next-name').textContent, 'empty');
});
test('past unfinished, blocked and ambiguous times remain explicit', () => {
  assert.equal(run([item()], {now:Date.parse('2030-05-01T04:00:00Z')}).get('next-state').textContent, 'overdue');
  assert.equal(run([item({status:'Blocked'})]).get('next-state').textContent, 'blocked');
  assert.equal(run([item({start_epoch:null})]).get('next-state').textContent, 'check time');
});
test('copy fallback exposes selectable text when clipboard fails', async () => {
  const ui = run([item()]);
  await ui.get('copy-place').listeners.click();
  assert.equal(ui.get('copy-fallback').hidden, false);
  assert.equal(ui.get('copy-fallback').value, '上海虹桥站');
  assert.equal(ui.get('copy-fallback').selected, true);
  assert.equal(ui.get('feedback').textContent, 'copy manually');
});
test('change request carries the shown version and scope; print invokes browser print', async () => {
  let copied;
  const ui = run([item()], {clipboard:{async writeText(text){copied = text;}}});
  await ui.get('change-request').listeners.click();
  assert.equal(copied, 'version=v0.1.1; scope=2030-05-01');
  assert.equal(ui.get('feedback').textContent, 'request copied');
  ui.get('print').listeners.click();
  assert.equal(ui.printCalls(), 1);
});
test('archive strings are assigned as text and empty trips remain readable', () => {
  assert.equal(run([item({activity:'<img src=x>'})]).get('next-name').textContent, '<img src=x>');
  assert.equal(run([]).get('next-name').textContent, 'empty');
});

test('overnight activity remains current after midnight, ahead of the new day', () => {
  const overnight = item({date:'2030-04-30', start:'23:00', end:'01:00', end_date:'2030-05-01', activity:'Overnight train',
    start_epoch:Date.parse('2030-04-30T15:00:00Z'), end_epoch:Date.parse('2030-04-30T17:00:00Z')});
  const ui = run([overnight, item()], {now:Date.parse('2030-04-30T16:30:00Z')});
  assert.equal(ui.get('next-name').textContent, 'Overnight train');
  assert.equal(ui.get('next-context').textContent, 'overnight underway');
  assert.match(ui.get('next-time').textContent, /next day 01:00/);
  ui.get('today').listeners.click();
  assert.equal(ui.get('next-name').textContent, 'Overnight train');
  ui.advance('2030-04-30T17:01:00Z');
  assert.equal(ui.get('day-select').value, '2030-05-01');
  assert.equal(ui.get('next-name').textContent, 'Walk');
});
test('future arrival across time zones is selected by instant, excluding skipped items', () => {
  const later = item({date:'2030-05-01', start:'14:00', end:'15:00', zone:'Pacific/Honolulu', start_epoch:Date.parse('2030-05-02T00:00:00Z'), end_epoch:Date.parse('2030-05-02T01:00:00Z'), activity:'Later'});
  const earlier = item({date:'2030-05-02', start:'08:00', end:'09:00', zone:'Asia/Tokyo', start_epoch:Date.parse('2030-05-01T23:00:00Z'), end_epoch:Date.parse('2030-05-02T00:00:00Z'), activity:'Earlier'});
  const ui = run([item({status:'Skipped'}), later, earlier], {now:Date.parse('2030-04-28T00:00:00Z')});
  assert.equal(ui.get('day-select').value, '2030-05-02');
  assert.equal(ui.get('next-name').textContent, 'Earlier');
});
test('today with no scheduled activity keeps the date the user was reading', () => {
  const ui = run([item(), item({date:'2030-05-02'})], {now:Date.parse('2030-04-28T00:00:00Z')});
  ui.get('day-select').value = '2030-05-02'; ui.get('day-select').listeners.change();
  ui.get('today').listeners.click();
  assert.equal(ui.get('day-select').value, '2030-05-02');
  assert.equal(ui.get('feedback').textContent, 'no activity today');
});
test('automatic date rollover never overrides a manual date selection', () => {
  const nextDay = item({date:'2030-05-02', start_epoch:Date.parse('2030-05-02T02:00:00Z'), end_epoch:Date.parse('2030-05-02T03:00:00Z')});
  const auto = run([item(), nextDay]);
  auto.advance('2030-05-01T17:00:00Z');
  assert.equal(auto.get('day-select').value, '2030-05-02');
  const manual = run([item(), nextDay]);
  manual.get('day-select').listeners.change();
  manual.advance('2030-05-01T17:00:00Z');
  assert.equal(manual.get('day-select').value, '2030-05-01');
});
test('repeated print events restore the original disclosure state', () => {
  const details = [{open:false}, {open:true}, {open:false}];
  const ui = run([item()], {details});
  ui.events.beforeprint(); ui.events.beforeprint();
  assert.deepEqual(details.map(el => el.open), [true,true,true]);
  ui.events.afterprint(); ui.events.afterprint();
  assert.deepEqual(details.map(el => el.open), [false,true,false]);
});
