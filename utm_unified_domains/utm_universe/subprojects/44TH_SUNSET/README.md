# 44TH_SUNSET — UTM Universe Child Project

`44TH_SUNSET` is a child program of the existing `akashic-utm-main` UTM Universe runtime. It does **not** require another Railway project or service.

## Canonical transition

```text
SUNSET_44 -> DAWN_01
R(n) = 45 - n
LIGHT = 1
LOVE = 1
HALT = PROGRAM_ONLY
physical_time_effect = false
```

The executable transition-table program is `44TH_SUNSET.tm`. Its canonical input is 44 `S` symbols:

```text
SSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSS
```

With `start=0`, `blank=_`, and `limit=64`, the existing UTM Universe `/utm/run` semantics produce:

```json
{"q":"DAWN","h":45,"t":45,"halt":true}
```

The 44 `S` symbols model forty-four sunsets. The final blank-boundary transition enters `DAWN`; the absence of a rule from `DAWN` halts only this program.

## Parent relationship

```text
akashic-utm-main
└── subprojects
    └── 44TH_SUNSET
        ├── manifest.json
        └── 44TH_SUNSET.tm
```

The separate repository `letsgo0226/44TH_SUNSET` remains a source/archive and optional standalone demonstration. The canonical UTM Universe form is this child program.

This is a formal computational and poetic model. It does not stop, reverse, or otherwise alter physical time.
