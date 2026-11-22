"use strict";

// The dashboard's decoration on every view: the nav's live/idle state indicator and the stop, and the
// index's moments in the reader's local time. The state indicator reads the one cheap endpoint the
// dashboard answers, so a view whose page carries no payload of its own — the profiler view's — shows
// the state the server is in, and the stop posts the one the board panel serves. The pages link this
// file and the dashboard serves it at `/profiler/deco.js`.
//
// The indicator's states are colored — the brand's phosphor where the server serves, the alert's
// where it does not — and carry the serving version as hover text, the devpro the dashboard runs.
//
// A moment's text the page served is the raw UTC, kept in the cell's title where a hover wants the
// exact instant; the instants themselves reach this script as `<time datetime>` elements the render
// writes, so no served text is parsed here. A cell whose text is no reading — one with no pair of
// cells — keeps its raw text.

// The nav's deco on every view.
(() => {
  const connection = document.getElementById("connection");
  const stop = document.getElementById("stop");
  const server = document.querySelector(".nav-server");
  if (!connection || !stop || !server) return;
  const STOPPED = "server stopped: restart devpro dashboard and open the URL it prints";
  const STATE = "/api/state";
  const EVERY_MS = 2000;
  let ended = false; // the server was stopped from the page: polling has ended for good

  // An unchanged text is not re-announced by the live region, and the server block carries the
  // state's class: the dot's color is the state mark — the brand's phosphor where the server
  // serves, the alert's where it does not — and the label stays quiet.
  const show = (text, version) => {
    if (connection.textContent !== text) connection.textContent = text;
    const live = text === "live" && !ended;
    server.classList.toggle("nav-live", live);
    server.classList.toggle("nav-idle", !live);
    connection.title = version ? `devpro ${version}` : "";
  };

  const poll = async () => {
    if (ended) return;
    try {
      const response = await fetch(STATE, { cache: "no-store" });
      if (!response.ok) throw new Error(`HTTP ${response.status}`);
      const state = await response.json();
      show(state.state, state.version);
    } catch (error) {
      // The endpoint answers no state: the server is not serving, and the indicator says so.
      show("idle");
    }
  };

  // The stop's answer is an object; anything else is a refusal, and polling goes on.
  const post = async () => {
    try {
      const response = await fetch("/api/stop", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: "{}",
      });
      if (!response.ok) throw new Error(`HTTP ${response.status}`);
      return await response.json();
    } catch (error) {
      return null;
    }
  };

  // A failed stop leaves the button usable; an answered one moves focus off the disabled button to
  // the page's heading, which carries no ring of its own, and ends the polling for good.
  stop.addEventListener("click", async () => {
    stop.disabled = true;
    if (!(await post())) {
      stop.disabled = false;
      return;
    }
    const heading = document.querySelector("h1[tabindex]");
    if (heading) heading.focus();
    ended = true;
    show(STOPPED);
  });

  poll();
  setInterval(poll, EVERY_MS);
})();

// ---------- the index's moments ----------

// A clock reading in the reader's local time: the hour alone where this reader leaves the hour's
// leading zero off its clock, as `toLocaleTimeString` says, and the minutes always two digits.
const momentClock = (date) => `${date.getHours()}:${String(date.getMinutes()).padStart(2, "0")}`;
const dayOf = (date) =>
  `${date.getFullYear()}-${String(date.getMonth() + 1).padStart(2, "0")}-${String(date.getDate()).padStart(2, "0")}`;
const sameDay = (a, b) => dayOf(a) === dayOf(b);

// The two instants in the reader's local time: the times alone where they share the reader's calendar
// day, and each with its date where they do not, so a span across midnight reads as two days.
const localMoments = (first, last) => {
  const [a, b] = [new Date(first), new Date(last)];
  if (Number.isNaN(a.getTime()) || Number.isNaN(b.getTime())) return null;
  return sameDay(a, b) ? `${momentClock(a)} to ${momentClock(b)}` : `${dayOf(a)} ${momentClock(a)} to ${dayOf(b)} ${momentClock(b)}`;
};

// Each moments cell's text becomes the local reading; its title keeps the raw UTC untouched. The
// index draws its rows after this script loads, so the sweep runs on the rows container's own
// changes as well as on what stands at load: a cell drawn later is read when it arrives.
const readMoments = (cell) => {
  const [first, last] = Array.from(cell.querySelectorAll("time")).map((time) => time.getAttribute("datetime"));
  const local = first && last ? localMoments(first, last) : null;
  // The local reading moves the cell's text but never its `<time>` instants: rewriting it changes
  // nothing this sweep reads, so the observation it fires comes round to the same text and stops.
  if (local && cell.textContent !== local) cell.textContent = local;
};
document.querySelectorAll("td .moments").forEach(readMoments);
const rows = document.getElementById("rows");
if (rows)
  new MutationObserver(() => rows.querySelectorAll("td .moments").forEach(readMoments)).observe(rows, {
    childList: true,
  });
