# Adversarial Samples (Phase 4)

This folder contains manually crafted text samples intended to probe detector behavior.

Scope and intent:

- These are **not** auto-generated adversarial attacks.
- Samples focus on safe patterns such as prompt-injection framing, obfuscation/encoding, repetition, and mixed-style writing.
- Use them to compare the heuristic (`simple`) detector vs the zero-shot (`zero-shot`) detector.

## How to run the comparison

Start the Detection service, then run:

```powershell
python .\tools\scripts\evaluate_adversarial_detectors.py --base-url http://127.0.0.1:8002
```

If you want the zero-shot model to run fully offline, start Detection with `ZERO_SHOT_MODEL_PATH` pointing at the local model directory under `astra-models/`.
