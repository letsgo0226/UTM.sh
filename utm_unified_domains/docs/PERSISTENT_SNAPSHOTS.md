# Persistent UTM Object Snapshots

The universal address layer separates stable object identity from time-dependent observations.

For any finite value accepted by the canonicalizer:

\[
A_U(x)=/object/G(C(x))
\]

A stored observation uses a second identity:

\[
S_U(x,v)=/snapshot/G("snapshot:"+v+":"+G(C(x)))
\]

where `v` is an explicit version or observation label.

## API

Create an address:

```http
POST /address
Content-Type: application/json

{"type":"json","value":{"b":2,"a":1}}
```

Create an immutable snapshot:

```http
POST /snapshot
Content-Type: application/json

{
  "GOBJECT":"<GOBJECT returned by /address>",
  "version":"2026-09-27T19:56+08:00",
  "result":{"status":404,"external_url":"https://example.invalid/x"}
}
```

Retrieve it:

```text
GET /snapshot/<GSNAPSHOT>
```

The record stores the canonical object, version, optional result, creation timestamp, `GSNAPSHOT`, and SHA-256 integrity value. Snapshot files are created with create-only filesystem semantics. Repeating the same `(GOBJECT, version)` cannot overwrite the stored observation; the existing record is returned.

This lets a local failure remain an observation rather than changing object identity:

```text
stable object address != observation result
404 at t1 != global nonexistence
```

## Durability boundary

`SNAPSHOT_DIR` controls storage and defaults to:

```text
/tmp/utm-address-snapshots
```

This is immutable-once-created storage at the application layer, but `/tmp` is normally ephemeral. For durable Railway deployment, mount a persistent volume and use for example:

```text
SNAPSHOT_DIR=/data/utm-address-snapshots
```

A persistent volume is therefore required before describing snapshots as durable across container replacement.
