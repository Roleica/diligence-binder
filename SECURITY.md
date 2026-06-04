# Security

This project processes financial vouchers and may handle sensitive business
documents. Do not commit real vouchers, extracted outputs, review CSV files, Excel
exports, screenshots, or `.env` files.

Before publishing or sharing a fork:

1. Run a secret scan.
2. Check that `.env` and API tokens are not tracked.
3. Check that sample data is synthetic or fully anonymized.
4. Rotate any API key that was ever committed, pasted into an issue, or shared
   in a public artifact.

Report security issues privately to the repository maintainer.
