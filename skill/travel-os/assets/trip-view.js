"use strict";
(() => {
  const {trip, labels, statuses} = JSON.parse(document.getElementById("trip-data").textContent);
  const $ = id => document.getElementById(id);
  const select = $("day-select");
  const dates = [...new Set(trip.items.map(item => item.date))].sort();
  const remaining = item => !["Done", "Skipped"].includes(item.status);
  const underway = (item, now) => remaining(item) && item.start_epoch !== null && item.end_epoch !== null && item.start_epoch <= now && now < item.end_epoch;
  const byInstant = (a, b) => (a.start_epoch ?? Infinity) - (b.start_epoch ?? Infinity);
  const localDate = (item, now) => {
    try {
      const parts = new Intl.DateTimeFormat("en-CA", {timeZone:item.zone, year:"numeric", month:"2-digit", day:"2-digit"}).formatToParts(now);
      const get = type => parts.find(part => part.type === type).value;
      return `${get("year")}-${get("month")}-${get("day")}`;
    } catch { return ""; }
  };
  const todayItem = now => trip.items.filter(item => underway(item, now)).sort(byInstant)[0]
    || trip.items.filter(item => remaining(item) && item.date === localDate(item, now)).sort(byInstant)[0]
    || trip.items.find(item => item.date === localDate(item, now));
  function showNext() {
    const now = Date.now();
    const items = trip.items.filter(item => (select.value === "all" || item.date === select.value) && remaining(item));
    // Do not silently mark past activities done or use the phone's time zone.
    const localToday = items.filter(item => item.date === localDate(item, now));
    const future = items.filter(item => item.start_epoch !== null && item.start_epoch > now).sort((a,b) => a.start_epoch - b.start_epoch);
    const current = items.filter(item => underway(item, now)).sort(byInstant)[0];
    const next = current || (select.value === "all" ? localToday[0] || future[0] || items[0] : items[0]);
    $("next").hidden = false;
    $("next-name").textContent = next ? next.activity : labels.complete;
    const dateLabel = next ? new Intl.DateTimeFormat(trip.locale || "en", {month:"short", day:"numeric", timeZone:"UTC"}).format(new Date(next.date + "T00:00:00Z")) : "";
    const end = next ? (next.end_date > next.date ? labels.nextday + " " : "") + (next.end || "?") : "";
    $("next-time").textContent = next ? `${dateLabel}  ${next.start || labels.unscheduled}–${end}` : "";
    $("next-place").textContent = next ? [next.city, next.location].filter(Boolean).join(" / ") : "";
    const isToday = next && next.date === localDate(next, now);
    $("next-context").textContent = !next ? "" : current && !isToday ? labels.continuing : isToday ? labels.live : labels.first;
    let state = next && !["Ready", "Planned"].includes(next.status) ? (statuses[next.status] || next.status) : "";
    if (next && next.status === "Blocked") state = labels.blocked;
    else if (next && (next.start_epoch === null || (next.end && next.end_epoch === null))) state = labels.unscheduled;
    else if (next && next.end_epoch !== null && next.end_epoch < now) state = labels.overdue;
    $("next-state").textContent = state;
  }
  function update() {
    document.querySelectorAll(".day").forEach(el => { el.hidden = select.value !== "all" && el.dataset.date !== select.value; });
    showNext();
  }
  async function copy(text, success) {
    $("copy-fallback").hidden = true;
    try {
      if (!navigator.clipboard) throw new Error("Clipboard unavailable");
      await navigator.clipboard.writeText(text);
      $("feedback").textContent = success;
    } catch {
      $("copy-fallback").value = text;
      $("copy-fallback").hidden = false;
      $("copy-fallback").focus();
      $("copy-fallback").select();
      $("feedback").textContent = labels.manual;
    }
  }
  let followingToday = false;
  select.addEventListener("change", () => { followingToday = false; update(); });
  $("today").addEventListener("click", () => {
    const now = Date.now();
    const match = todayItem(now);
    if (match) select.value = match.date;
    followingToday = !!match;
    $("feedback").textContent = match ? "" : labels.dayempty;
    update();
  });
  $("print").addEventListener("click", () => window.print());
  let foldedBeforePrint = null;
  window.addEventListener?.("beforeprint", () => {
    if (foldedBeforePrint !== null) return;
    foldedBeforePrint = [...document.querySelectorAll("details:not([hidden])")].filter(el => !el.open);
    foldedBeforePrint.forEach(el => { el.open = true; });
  });
  window.addEventListener?.("afterprint", () => {
    (foldedBeforePrint || []).forEach(el => { el.open = false; });
    foldedBeforePrint = null;
  });
  $("change-request").addEventListener("click", () => copy(labels.requesttext.replace("{version}", trip.version).replace("{scope}", select.value === "all" ? labels.all : select.value), labels.requestdone));
  document.querySelectorAll(".copy-place").forEach(button => button.addEventListener("click", () => copy(button.dataset.copy, labels.copied)));
  const now = Date.now();
  const match = todayItem(now);
  const upcoming = trip.items.filter(item => remaining(item) && item.start_epoch !== null && item.start_epoch > now).sort(byInstant)[0];
  followingToday = !!match;
  select.value = match ? match.date : upcoming ? upcoming.date : dates[0] || "all";
  update();
  setInterval(() => {
    const match = followingToday && todayItem(Date.now());
    if (match) { select.value = match.date; update(); }
    else showNext();
  }, 60000);
})();
