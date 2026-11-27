# A runner's stand-in is type-checked

A change that edits a test runner's stand-in for a host's surface type-checks the stand-in against
the host's pinned declarations in that change, and leaves the check green. The lint program covers
what ships, and a stand-in no program takes compiles nowhere: the shapes it invents are checked
against nothing, and a field the host does not declare passes as one it declares.

Where the stand-in cannot be taken by a check — a shape the declarations leave open, a runtime value
they do not publish — a comment names the field it models and where in the declarations that field is
declared. A stand-in the check cannot see is read in prose or not at all.

The check holds that a name exists at the host's pinned version, never that a read is right: a
correctly typed field read as the wrong kind of message passes it. What a host value means is the
host reference's to say, and the read is checked against that
([A hook contract is read, not assumed](a-hook-contract-is-read-not-assumed.md)).
