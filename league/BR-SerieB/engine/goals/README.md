# G-BRB goals engine

Reads the BR-SerieB match data and evaluates the preregistered 1X2 and OU goals arms. Use `run_g_br.py dev` for the recorded development evaluation; conditional virgin evaluation is authorized only after a passing dev gate. Gate Zero failed the recorded dev gate, so no virgin run, parameters, or predictions are authorized.

The preregistered X2 lambda-space implementation is retained in the engine as a shrink variant, but it is moot after Gate Zero failure.
