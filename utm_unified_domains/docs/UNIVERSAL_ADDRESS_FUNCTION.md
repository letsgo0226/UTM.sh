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
GET  /snapshot/<GOBJECT>/<version>
```

POST example:

```json
{"type":"json","value":{"a":1,"b":2}}
```

The response contains `canonical`, `GOBJECT`, and `utm_address`.

`/object/<GOBJECT>` and `/decode/<GOBJECT>` reverse the address to the typed canonical value.

## Snapshot semantics

`/snapshot/<GOBJECT>/<version>` currently provides an immutable identity for the pair `(object, version)`. It explicitly reports `result_persistence:false`: it does **not** persist live web-search observations. Durable historical search-result snapshots require persistent storage and are a separate layer.

## Search relation

Search remains time/environment dependent:

```text
q -> search address -> R(q,t,e)
```

The same query is additionally exposed through the universal object address generated from `text:q`. Thus addressability is stable while live retrieval may vary or fail.

## Boundary

"Arbitrary" means any finite value admitted by the canonicalization interface. It does not imply that every mathematical object has a finite representation, nor that an address guarantees real-world truth, existence, or successful retrieval.
