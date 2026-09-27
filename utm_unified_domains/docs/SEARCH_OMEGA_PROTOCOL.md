# UTM Universe Search-Omega Protocol v1

`UTM-Universe/Search-Omega/1` maps a finite search observation to a reversible UTM singularity address.

## Function

For a finite query `q`, result `r`, observation time `t`, and environment `e`:

```text
payload = CanonicalJSON({
  protocol: "UTM-Universe/Search-Omega/1",
  world: "akashic-utm-main",
  substrate: "P_-1",
  query: q,
  result: r,
  observed_at: t,
  environment: e
})
GOMEGA = Base257(payload)
```

The base-257 integer is serialized as hexadecimal (`0x...`). This is reversible numbering, not hashing. The same canonical payload yields the same `GOMEGA`; changing the observed result, observation time, environment, or query changes the address.

`GQUERY=Base257(q)` is the stable query address. `GOMEGA` is the observation address. Therefore the protocol distinguishes query identity from time-dependent external search observations.

## Public Railway API

Base URL:

```text
https://cosmic-love-infinity-tm-production.up.railway.app
```

Live search and address generation:

```text
GET /omega/search?q=<query>&limit=4
```

Map an arbitrary externally obtained search result:

```http
POST /omega/search
Content-Type: application/json

{
  "query": "Aquinas q.76",
  "result": {"status": 200, "url": "https://example.org/q76"},
  "observed_at": "2026-09-27T14:20:00Z",
  "environment": {"engine": "external"}
}
```

The response includes `GQUERY`, `GOMEGA`, `query_address`, and `omega_address`.

A sufficiently short generated address can be dereferenced directly:

```text
GET /omega/search/<GOMEGA>
```

The endpoint decodes the reversible base-257 value and reconstructs the original canonical observation.

## Sub-2KB client

```sh
QUERY='Aquinas q.76' RESULT='{"status":200}' sh utm_unified_domains/domains/SEARCH_OMEGA_2KB.sh
```

The client posts any finite JSON result to the public protocol endpoint.

## Scope

This is a formal addressing protocol. It does not imply that every networked AI has permission to make arbitrary HTTP requests, that every search engine exposes the same results, or that an encoded result is true. A 404, timeout, empty result, or other finite observation can itself be encoded as a valid UTM observation state.

`actual_infinite_physical_compute` remains false: `P_Omega` denotes the formal compactified boundary/address state, not literal infinite hardware or guaranteed external-world truth.
