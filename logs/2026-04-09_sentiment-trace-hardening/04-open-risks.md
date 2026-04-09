# Open Risks

- The deterministic sentiment audit rewards explicit tone cues, so subtle provider-written prose may still score a little lower than a human reader would expect.
- Runtime logs intentionally store the generated story text for debugging; that is useful for coursework inspection, but the file will keep growing across repeated runs.
- The new audit is strongest on the current supported sentiments only. Adding new sentiment labels later will require explicit audit rules rather than inheriting generic behavior.
