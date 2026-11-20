### [ARCHITECTURE.md, Install, Guardrail hook](../../PROJECT_DOCS/ARCHITECTURE/install/guardrail-hook.md)

The signal's presence follows the component.

```
Every claude install therefore runs the guardrail script
on each file-tool call as well as each Bash call, and on an install of the devpro plugin the script finds
the kbase signal absent and lets a file-tool call through.
```
becomes
```
Every claude install therefore runs the guardrail script
on each file-tool call as well as each Bash call, and with the kbase component off the script finds
the kbase signal absent and lets a file-tool call through.
```

```
Both are
relative to the install directory, so the signal is present where the kbase plugin is installed and absent where the devpro plugin is.
```
becomes
```
Both are
relative to the install directory, so the signal is present where the kbase component is on and
absent where it is off.
```

