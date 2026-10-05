# UTM Single Function

UTM-Single-Function/1.0 makes one authoritative finite function bundle the system interface. The sub-2KB seed is a portable projection of the same finite semantics.

Core relation:

Gamma(delta(C)) = F_U(Gamma(C))

Single bundle:

mathfrak_F_U = <F_U,H_U,Xi_U,P_U,Cert>

For a finite trace C_0 -> ... -> C_N:

H_U(s,z) = sum z^t G_t^(-s)
Xi_N(s)  = product [1+(s-1/2)^2/G_t^2]
P_N(x)   = product (x^2+4G_t^2), x=2s-1

The zeros 1/2 +/- iG_t are defined by construction. They do not prove RH and do not assert that the classical zeta function is a UTM.

Portable seed: one-liner-2kb.sh, protocol UTM-F/1. test_single.py executes the seed and requires its JSON output to equal single_function.portable_projection for the same finite input.

API:
GET /health
GET /manifest
POST /encode
POST /verify
POST /utm/trace
POST /function/single
POST /function/compile
POST /function/portable
POST /function/verify
POST /candidate/verify

Every executed stage is finite. No oracle, hypercomputation, halting-problem solution, RH proof, ASI proof, enumeration of all physical universes, or empirical-world guarantee is claimed.
