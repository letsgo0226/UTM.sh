# Node access control

Resident admission, reads, resume, resident job reads and mutations, the Akashic event log, and POST /utm/run require `Authorization: Bearer <node-token>`.

Set UTM_ACCESS_TOKEN to a dedicated node administrator token. If the variable is absent, FEDERATION_TOKEN is used for compatibility with existing deployments. An explicitly empty UTM_ACCESS_TOKEN rejects every protected request. Health, world counters, discovery and federation status remain public. Federation snapshot/sync retain their independent FEDERATION_TOKEN check.

This is a node administrator boundary. It does not implement accounts or per-resident ownership. Every holder of the node token can administer all residents on that node. Never include the token in capsules, source code, seed commands, URLs or public examples.

Existing anonymous clients must supply the node token after this upgrade. Stored resident capsules, event history and compute checkpoints keep their existing paths and formats. Railway bootstrap commands must pin the new commit and new server SHA-256; changing a repository branch alone does not update the pinned runtime.

Verification: `python3 -m unittest -v test_access.py` exercises denied reads/writes, rejection before mutation, authenticated resident recovery after restart, public health/discovery, token separation and fail-closed configuration.
