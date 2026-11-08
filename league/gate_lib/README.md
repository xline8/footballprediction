# Gate library

This stdlib-only package provides four guards for future builds: a fail-closed
dev-pass assertion before sealed data is loaded; mechanical preregistration
tokens; explicit per-league derivations for template constants; and one
calibration sign convention, predicted minus actual. A build parses its prereg,
derives and checks constants, records its dev token, then uses the metrics and
artefact readers for Gate Zero and only calls `load_sealed_rows` after the token
exists.
