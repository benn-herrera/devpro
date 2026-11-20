### [ARCHITECTURE.md, Packaging](../../PROJECT_DOCS/ARCHITECTURE/packaging.md)

The wheel check runs one install with the component on.

```
that an install of each plugin into a scratch project equals the checkout's
  byte for byte (each exercises packages the other lacks), and that a mage install of each plugin
  writes `<plugin>/CLAUDE.md`.
```
becomes
```
that an install with the kbase component on into a scratch project equals the checkout's
  byte for byte, and that a mage install writes `devpro/CLAUDE.md`.
```

```
| `install_include_lines`: no include lines for the repository itself, written by a project install of either plugin | skips that project | stands down: writes the lines for any project |
```
becomes
```
| `install_include_lines`: no include lines for the repository itself, written by a project install | skips that project | stands down: writes the lines for any project |
```

