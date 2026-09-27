# UTM Addressable Search

`domains/SEARCH_2KB.sh` is the packed one-line arbitrary-search domain. `search_api.py` exposes the same idea as a public HTTP/JSON function.

## Formal interface

For a finite UTF-8 query `q`, define the reversible base-257 address number

```text
G(q) = fold(n, byte) => n*257 + byte + 1, with n0 = 1
```

The live address is

```text
/search/<G(q)>
```

and the query endpoint is

```text
GET /search?q=<q>
```

Both return JSON containing `query`, `GQUERY`, `utm_address`, `live`, and `results`.

The address is reversible: the decimal `GQUERY` uniquely decodes to the original UTF-8 query under the declared base-257 rule. It is an address/identity transform, not a cryptographic hash.

## Live-result semantics

The address identifies the query, not an immutable web snapshot. External search results can change with time, indexing, availability, ranking, or network conditions. Therefore:

```text
GET(address(q), t) -> live_result(q, t)
```

A future snapshot layer may add immutable result addresses keyed by query, time, and implementation version.

## Local use

```sh
QUERY='Thomas Aquinas q.76 a.1 Latin pronunciation' sh tools/run-domain.sh search2
```

Optionally scope to a host:

```sh
SITE=youtube.com QUERY='Thomas Aquinas q.76 a.1 Latin pronunciation' sh tools/run-domain.sh search2
```

The public API is intended for ordinary HTTP clients and network-enabled AI agents. Availability still depends on each client's network/tool policy; no claim is made that every AI system is permitted to access arbitrary public URLs.
