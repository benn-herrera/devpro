# Plugin membership has one home

The definitions that ship are decided in one place in code, the member lists in
`devpro/components.py`: the required set is every discovered definition no component names, the
optional components' lists enumerate their members. No harness, install step, render or test holds
a list of members; each reads the selection's `ships(name)`. A change to a member list changes
SPEC.md, Deployed Surfaces, Plugins with it.
