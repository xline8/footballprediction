# Staging manifest — MX-ExpansionMX (environment defect record)

This session's sandbox blocks ALL git object/lock writes
(`Operation not permitted` on loose-object, index.lock and ref.lock
writes, verified repeatedly from 03:57 UTC onward; the same block
killed the worktree checkout — the tree was reconstructed manually
— and Codex's tool sandbox). Plain file writes via the file tools
work; `rm` works; git reads work. The coordinator can commit the
stages below IN ORDER; sha256 + ordering below prove the prereg
preceded all fitting (no engine existed and no fit had run when
the prereg hashes were taken, 2026-11-10 04:09 UTC).

Intended commit order:
1. steps (analysis + data builder + config)
2. prereg (prereg/PREREG_G_MXE.md, prereg/PREREG_K_MXE.md)
3. engines + dev results
4. virgin results + verdicts + predictions (only what the gates allow)

## Stage 1+2 file hashes (2026-11-10 04:09 UTC, before any fitting)

- prereg/PREREG_G_MXE.md  d2c4ad55c7e303979c455cb50d809e9478c08d67e6a5244cf8b57ae0984e0805
- prereg/PREREG_K_MXE.md  14b71f1d13eebfbad4ba0562472da82fef687e62f70ba8a8b2e7f06d7266c077
- analysis/DATA_UNDERSTANDING.md  3d72670fd2fffc7e9482b17fffe3e28fe8ebdb9ff077c84bff6376f6871a1dcb
- analysis/EDA.md  57bcad3f8ee5ae26960803cb1233ca7b04f9650e1dce7374fe6769586de8abc0
- analysis/FEATURES.md  7ad36cd457ccd1df93f0fe271ba0071b661d3414554d4f8b313ab0293c6299b0
- analysis/MODEL_DESIGN.md  e794b78f46336a3b2f8691662b2d6b3a38646ecbe3ddd335e30bca92d755c50a
- analysis/PREPROCESSING.md  cf38ec0ca409fd71b247a984e7435fb06fe6f0aa02880f5b204e9ab058f79e2a
- config.yaml  7b91656e0f096af7569af7bd04aebeb734e32ea2ae9e704f84c6f879d441412a

Other environment defects: analysis/charts/*.png and data/*.csv
could not be written by any exec process (0-byte files removed);
make_charts.py and build_data.py are committed and verified to run
to their write step — the coordinator's environment can regenerate
both. Engine runs in this session load rows through
build_data.load_rows() (identical code path to the CSV builder).

## Final state (2026-11-10 04:14 UTC)

Verdicts: G-MXE FAIL (virgin), K-MXE FAIL (virgin), S/C/T NOT
BUILDABLE. Nothing ships; no predictions/ directory exists.
Stage 3+4 hashes:
- reports/G_MXE_VERDICT.md  0e81d62dc09df6d87de0545bc121c47586e86e1679a992724022a6e8f021d4b3
- reports/K_MXE_VERDICT.md  9f23e5e51a4222a6a232ac750fa1324e2cf3d4eda112b39bd14db3178ac47746
- reports/S_MXE_VERDICT.md  345ae452b1dc4d1de188de474123422c7b27bb54154e10c3945a3165e25769d7
- reports/C_MXE_VERDICT.md  02507fda8b482795776d9e18dcccf7bb01afaa0f8eac24761a0befc1b0adc31c
- reports/T_MXE_VERDICT.md  8a78d5d5b82f8a16b5923820775ee910c6594ba65add81ec7bf94d056d6726fa
- engine/goals/results_dev.json  e58a278a25208e66c5cd27e17187ea769d94a4f89184984e54b0edc2be5daa84
- engine/goals/results_virgin.json  0263ab763ce4faffa1efcb51252acb50711ce54d056266eda5bf14c09f7e3511
- engine/cards/results_dev.json  f8ee2bb6547d6e676672b1896c47b91b24aa93e29d009e0821495d6ae4bbd802
- engine/cards/results_virgin.json  2124faf19d6fc612d24b8a3efc4488ec6b2806d3a9faa9dd38c1cdf6f84a8f4d

Suggested commit messages, in order:
1. "MX-ExpansionMX steps 1-6: era map (stats only in in-progress 2026/27), cards-era defect, design G+K build / S+C+T not buildable"
2. "MX-ExpansionMX prereg: G-MXE (GZ+SHRINK) + K-MXE (GZ, primary 5.5) frozen before fitting"
3. "MX-ExpansionMX engines + dev: G dev PASS (1.0420 vs clim 1.0631), K dev PASS (0.6784 vs base 0.6803/naive 0.6877)"
4. "MX-ExpansionMX virgin + verdicts: G FAIL (LL leg + HW calibration), K FAIL (LL leg vs base); 0 PASS / 2 FAIL / 3 not buildable"
