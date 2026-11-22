"use strict";

// The nav's chrome on every view: the live/idle state indicator and the stop. It reads the one
// cheap state endpoint the dashboard answers, so a view whose page carries no payload of its own —
// the profiler view's — shows the state the server is in, and it posts the stop the board panel
// serves. The dashboard inlines this text into each of its pages; the board page names the file
// the profiler path serves.
//
// The indicator's states are colored — the brand's phosphor where the server serves, the alert's
// where it does not — and carry the serving version as hover text, the devpro the dashboard runs.
//
// The index's moments are rewritten in the reader's local time, the browser's: `H:MM to H:MM` while
// both instants share the reader's calendar day, each carrying its date where they do not. The raw
// UTC the page served stays in the cell's title, where a hover wants the exact instant.

(() => {
  const connection = document.getElementById("connection");
  const stop = document.getElementById("stop");
  const server = document.querySelector(".nav-server");
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

// A moment's text the page served: `<first> UTC to <last>`, the first to the second and the last as
// an ISO instant, which `Date` reads as the same instant either part names.
const MOMENTS = /^(\d{4}-\d{2}-\d{2}) (\d{2}):(\d{2}):(\d{2}) UTC to (\S+)$/;
const clock = (date) => `${date.getHours()}:${String(date.getMinutes()).padStart(2, "0")}`;
const calendar = (date) => `${date.getFullYear()}-${date.getMonth()}-${date.getDate()}`;
const dayOf = (date) =>
  `${date.getFullYear()}-${String(date.getMonth() + 1).padStart(2, "0")}-${String(date.getDate()).padStart(2, "0")}`;

// The two instants in the reader's local time: the times alone where they share the reader's calendar
// day, and each with its date where they do not, so a span across midnight reads as two days.
const localMoments = (first, last) => {
  const [a, b] = [new Date(first), new Date(last)];
  if (Number.isNaN(a.getTime()) || Number.isNaN(b.getTime())) return null;
  return calendar(a) === calendar(b) ? `${clock(a)} to ${clock(b)}` : `${dayOf(a)} ${clock(a)} to ${dayOf(b)} ${clock(b)}`;
};

// Each moments cell's text becomes the local reading; its title keeps the raw UTC untouched.
document.querySelectorAll("td .moments").forEach((cell) => {
  const [, day, hours, minutes, seconds, last] = MOMENTS.exec(cell.textContent) || [];
  const local = day && localMoments(`${day}T${hours}:${minutes}:${seconds}Z`, last);
  if (local) cell.textContent = local;
});
