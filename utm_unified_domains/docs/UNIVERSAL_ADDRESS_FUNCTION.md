# UTM Universe Address Function

The universal address layer maps any finite value supported by the canonicalization interface to a reversible UTM Universe object address.

## Definition

```text
A_U(x) = /object/G(C(x))
```

`C` is a typed canonical representation and `G` is the repository's reversible base-257 encoding. This is numbering, not hashing.

Supported canonical input types:

- `text`: `t:<UTF-8 text>`
- `json`: `j:<canonical JSON>` where object keys are sorted and separators are compact
- `bytes`: `b:<canonical base64>`

The type prefix prevents a text string containing JSON syntax from colliding with the corresponding JSON value.

## API

```text
GET  /address?type=text&value=hello
GET  /address?type=json&value={"b":2,"a":1}
POST /address
GET  /object/<GOBJECT>
GET  /decode/<GOBJECT>
POST /snapshot
GET  /snapshot/<GSNAPSHOT>
```

POST address example:

```json
{"type":"json","value":{"a":1,"b":2}}
```

The response contains `canonical`, `GOBJECT`, and `utm_address`. `/object/<GOBJECT>` and `/decode/<GOBJECT>` reverse the address to the typed canonical value.

## Persistent snapshot semantics

A time-dependent observation can be frozen separately from the stable object identity:

```json
{
  "GOBJECT":"<GOBJECT>",
  "version":"2026-09-27T19:56+08:00",
  "result":{"status":404}
}
```

submitted to `POST /snapshot`.

The snapshot address is derived from:

```text
GSNAPSHOT = G("snapshot:" + version + ":" + GOBJECT)
```

and can be retrieved at `/snapshot/<GSNAPSHOT>`. Snapshot files use create-only semantics: repeating the same `(GOBJECT, version)` does not overwrite the first stored result. Records carry a SHA-256 integrity value.

`SNAPSHOT_DIR` defaults to `/tmp/utm-address-snapshots`. This provides application-level immutable records, but `/tmp` is normally ephemeral. Durable retention across Railway/container replacement requires a persistent volume and a path such as:

```text
SNAPSHOT_DIR=/data/utm-address-snapshots
```

Thus immutable record semantics and durable hosting are separate guarantees. See `PERSISTENT_SNAPSHOTS.md`.

## Search relation

Search remains time/environment dependent:

```text
q -> search address -> R(q,t,e)
```

The same query is additionally exposed through the universal object address generated from `text:q`. Thus addressability is stable while live retrieval may vary or fail. A `404`, timeout, or later changed result can be stored as one immutable observation without changing the underlying object address.

## Boundary

"Arbitrary" means any finite value admitted by the canonicalization interface. It does not imply that every mathematical object has a finite representation, nor that an address guarantees real-world truth, existence, or successful retrieval.
