### [ARCHITECTURE.md, Install, Installing this repository](../../PROJECT_DOCS/ARCHITECTURE/install/installing-this-repository.md)

The mage sentence names the constant directory and one install.

```
(mage, whose `project_harness_dir` is `{plugin}` and whose `user_harness_dir` is `.`): the install
skips that call there, so a mage install of either plugin writes no include line and creates no `Makefile`.
```
becomes
```
(mage, whose `project_harness_dir` is `devpro` and whose `user_harness_dir` is `.`): the install
skips that call there, so a mage install writes no include line and creates no `Makefile`.
```

