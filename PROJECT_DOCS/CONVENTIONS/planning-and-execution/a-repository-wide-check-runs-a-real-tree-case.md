# A repository-wide check runs a real-tree case

A repository-wide check's own case set includes one run over the real tree it polices; a fixture-only
case leaves the check unexercised on its inputs. A check that passes against fixtures alone proves
the fixtures, not the check over the trees it will actually read.
