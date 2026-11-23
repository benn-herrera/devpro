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
// A moment's text the page served is the raw UTC, kept in the element's own title where a hover wants
// the exact instant — the cell's title stating the pair, a lone stamp's its own — and the cell's
// second `<time>` element, the last instant's machine form, keeps that form as its text. The instants
// themselves reach this script as `<time datetime>` elements the render writes, so no served text is
// parsed here. A cell whose text is no reading — one with no pair of cells — keeps its raw text.

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

// A clock reading in the reader's local time, 24-hour: built from the date's own fields, so the
// separator and the digits are this page's rather than the reader's locale's — `toLocaleTimeString`
// reads the ICU settings of whatever browser it runs in.
const pad = (n) => String(n).padStart(2, "0");
const momentClock = (date) => `${pad(date.getHours())}:${pad(date.getMinutes())}`;
const dayOf = (date) => `${date.getFullYear()}-${pad(date.getMonth() + 1)}-${pad(date.getDate())}`;
const sameDay = (a, b) => dayOf(a) === dayOf(b);

// The two instants in the reader's local time: the times alone where they share the reader's calendar
// day, and where they do not the date on the first end alone — the finish being the next day's is
// obvious — so a span across midnight reads as one day and one clock running into the next.
const localMoments = (first, last) => {
  const [a, b] = [new Date(first), new Date(last)];
  if (Number.isNaN(a.getTime()) || Number.isNaN(b.getTime())) return null;
  return sameDay(a, b) ? `${momentClock(a)} to ${momentClock(b)}` : `${dayOf(a)} ${momentClock(a)} to ${momentClock(b)}`;
};

// One moment standing alone — the session page's header stamp — reads with its date: a lone stamp is
// its page's only time, and the page's title says no day. It carries the date whole, not the pair's
// first-end-alone reading, which is a span's shorthand.
const localMoment = (stamp) => {
  const at = new Date(stamp);
  return Number.isNaN(at.getTime()) ? null : `${dayOf(at)} ${momentClock(at)}`;
};

// A moments cell's text becomes the local reading and a lone moment's its own; each keeps its title,
// the raw UTC untouched, and the `<time>` elements themselves — their `datetime` attributes are the
// machine form the served page promises. The index draws its rows after this script loads, so the
// sweep runs on the rows container's own changes as well as on what stands at load: a cell drawn
// later is read when it arrives. A cell is two `<time>` elements, a lone moment one, and the sweep
// tells them by the count.
const readMoments = (cell) => {
  const stamps = Array.from(cell.querySelectorAll("time"));
  const instants = stamps.map((time) => time.getAttribute("datetime"));
  const reading = instants.length === 1 ? localMoment(instants[0]) : instants.length === 2 ? localMoments(instants[0], instants[1]) : null;
  // The local reading lands in each `<time>`'s own text, where the raw UTC stood: rewriting the
  // elements' text changes nothing this sweep reads, so the observation it fires comes round to the
  // same text and stops. A lone moment's reading is its element's own text whole — it splits on no
  // separator, and its date would be the first end's if it did.
  if (!reading || cell.textContent === reading) return;
  const ends = stamps.length === 2 ? reading.split(" to ") : [reading];
  stamps.forEach((time, index) => (time.textContent = ends[index]));
};
const MOMENTS = ".moments, #subline time";
document.querySelectorAll(MOMENTS).forEach(readMoments);
const rows = document.getElementById("rows");
if (rows)
  new MutationObserver(() => rows.querySelectorAll(".moments").forEach(readMoments)).observe(rows, {
    childList: true,
  });
// The session page's header stamp is written by the page's own script, which loads after this one:
// the subline's changes carry it in.
const subline = document.getElementById("subline");
if (subline)
  new MutationObserver(() => subline.querySelectorAll("time").forEach(readMoments)).observe(subline, {
    childList: true,
  });
