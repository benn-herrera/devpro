# Guardrail registration

- **Probe.** Before the first write, the install runs the source script once, with
  `GUARDRAIL_INTERPRETER` and no `CLAUDE_PROJECT_DIR`, on one allowed Bash call, and requires exit
  0 within `GUARDRAIL_PROBE_SECONDS`. A missing interpreter, a missing module, a broken script and
  a hang all fail it. A failed probe drops the script and writes the registration without the
  guardrail's entry.
  Its report line names the skip and its reason, and never a path.
  Whatever the probe's outcome, a guardrail script stands in the install directory after the run
  only where the probe passed: the replacement removed any earlier install's. The probe is one
  allowed call, not the case table, which runs in the test suite only.
- **Registration.** `GuardrailHook.registration`, built by `_guardrail_registration`, is written as
  a harness-rendered file; `GuardrailHook.registration_without_hook`, built by
  `_reminder_registration`, is the same file where the probe fails. It is
  written on every install, holding the guardrail's entry only where the probe passed, so a
  registration never names a script that does not run. It
  is rendered from a constant command, so no settings merge, no project-root path and no
  harness-directory quoting is involved, and `--subdir` does not change it.

- **Opencode.** It declares no `GuardrailHook`, so it has no probe and no registration file. Its
  registration is the plugin entry, which runs `guardrail.ts` within itself (Guardrail
  hook).

A user-level install runs no probe: `install` takes no `GuardrailHook` for it, the registration
staying a project install's; opencode's entry runs the guardrail resource beside it at user level as
in a project.

