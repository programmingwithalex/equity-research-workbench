# Test policy

No application behavior exists yet, so this directory intentionally has no tests.
Do not add placeholder tests solely to make CI appear tested.

The first SEC-discovery increment must add pytest tests for actual selection
behavior and enable pytest in CI. Use recorded public-source response fixtures
and mocked HTTP calls; ordinary CI must not contact SEC or paid model APIs.

Keep tests focused on observable behavior. Explain the failure or requirement a
test protects; avoid tests that merely repeat constants or implementation details.
