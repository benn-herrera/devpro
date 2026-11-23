### [Package and Command](../../PROJECT_DOCS/SPEC/package-and-command.md)

**As it stands:**

```
both print the same `--help`, and the same arguments install the same product, byte for byte.
The install verbs — `render`, `install`, `install-agents-file`, `render-agents-file` and the
hidden `harness` — exit 0 on success and 2 on a refusal or an operating-system failure, printing
`error: <message>` on
stderr;
```

**Becomes:**

```
both print the same `--help`, and the same arguments install the same product, byte for byte.

Three maintainer verbs — `dev-render`, `render-agents-file` and `harness` — exist only where the
environment variable `DEVPRO_DEV` is `1`. Elsewhere they are absent from `--help` and refused as an
invalid choice, as any verb the command does not have is; no README, guide or installed definition
names them.

The install verbs — `install` and `install-agents-file` — and the maintainer verbs exit 0 on success
and 2 on a refusal or an operating-system failure, printing `error: <message>` on stderr;
```

**As it stands:**

```
panel the board the retired `devpro kanban` served. The verbs run wherever the `devpro` command
runs; they are not part of the install product.
```

**Becomes:**

```
panel the board the retired `devpro kanban` served. The verbs run wherever the `devpro` command
runs, and from an installation's own copy of devpro (Deployed Surfaces, Shipped files).
```

