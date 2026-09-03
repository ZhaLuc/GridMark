# Contributing

## Principles

1. Keep the **topic/TF/serial contract** stable or update `docs/api.md` and all nodes in the same change.
2. Update [field-test-log.md](field-test-log.md) when calibration or acceptance numbers change.
3. Prefer real runnable code over pseudocode.
4. Hardware docs: Mermaid + plain-text pin tables.

## Workflow

1. Branch from `main`.
2. Build affected packages with `colcon`.
3. Update docs for any behavior/parameter change.
4. Open a PR with summary + test plan.

## Commit messages

Write clear commit messages that describe the change (e.g. "Add frontier blacklist radius parameter").

## Code review checklist

- [ ] Topics/types match contract
- [ ] Launch order / gates still valid
- [ ] Field numbers / docs updated when behavior changes
- [ ] Package.xml dependencies updated

## Related

- [Development](development.md)
- [API](api.md)
