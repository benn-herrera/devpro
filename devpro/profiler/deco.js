"use strict";

// The dashboard's decoration on every view: the nav's live/idle state indicator and the stop. The
// state indicator reads the one cheap endpoint the dashboard answers, so a view whose page carries
// no payload of its own — the profiler view's — shows the state the server is in, and the stop posts
// the one the board panel serves. The pages link this file and the dashboard serves it at
// `/profiler/deco.js`.
//
// The indicator's states are colored — the brand's phosphor where the server serves, the alert's
// where it does not — and carry the serving version as hover text, the devpro the dashboard runs.
//
// It is also the one home of the notation the pages present moments and durations in: the local day
// and clock, 24-hour with seconds, and a duration's words. The session page and the index call it
// rather than each carrying a formatter of its own, and the standalone render inlines this file's
// text for the page that cannot link it.

// The one notation the pages present moments and durations in, exposed as one deliberate global —
// `devproFormat` in the page's scope, the `globalThis` assignment where this file may be pasted into
// a script that lives in a function rather than a program: the local day and clock, 24-hour with
// seconds, a duration's words, and a token count's figure. The session page and the index call it
// rather than each carrying a formatter of its own, and the standalone render inlines this file's
// text for the page that cannot link it.
globalThis.devproFormat = (() => {
  const padTwo = (n) => String(n).padStart(2, "0");
  // The reader's clock, built from the date's own local fields — the separator and the digits this
  // file's rather than the reader's locale's, which `toLocaleTimeString` reads off whatever browser
  // it runs in.
  const localDay = (d) => `${d.getFullYear()}-${padTwo(d.getMonth() + 1)}-${padTwo(d.getDate())}`;
  const clock = (d) => `${padTwo(d.getHours())}:${padTwo(d.getMinutes())}:${padTwo(d.getSeconds())}`;
  // A duration from milliseconds: no space between number and unit, one decimal only below ten
  // seconds, and the largest unit first from a minute up.
  const dur = (ms) => {
    if (!ms) return "0s";
    if (ms < 1000) return `${ms}ms`;
    if (ms < 9950) return `${(Math.round(ms / 100) / 10).toFixed(1)}s`;
    if (ms < 60000) return `${Math.round(ms / 1000)}s`;
    const seconds = Math.round(ms / 1000);
    if (seconds < 3600) {
      const rest = seconds % 60;
      return rest ? `${Math.floor(seconds / 60)}m ${rest}s` : `${Math.floor(seconds / 60)}m`;
    }
    const minutes = Math.round(seconds / 60) % 60;
    return minutes ? `${Math.floor(seconds / 3600)}h ${minutes}m` : `${Math.floor(seconds / 3600)}h`;
  };
  // The figure a token count carries — `1.2M`, `3.4k`, or the count itself.
  const scaled = (n) => (n >= 1e6 ? `${(n / 1e6).toFixed(1)}M` : n >= 1e3 ? `${(n / 1e3).toFixed(1)}k` : `${n}`);
  return { localDay, clock, dur, scaled };
})();

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
