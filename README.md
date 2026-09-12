# POS Cash Out Limit (Odoo 18)

Blocks the standard POS **Cash Out** operation when the requested amount exceeds
the theoretical cash available in that POS session. The available balance is:

`opening cash + captured cash payments + POS cash statement lines`

The check runs on the Odoo server, displays the requested and available amounts,
and serializes concurrent withdrawals from the same session. Cash In is unchanged.

## Install

1. Copy this directory into an Odoo 18 custom-addons path.
2. Restart Odoo, update the Apps list, and install **POS Cash Out Limit**.
3. Test in a staging database before deploying to production.

## Acceptance checks

- Open a session with $19,414.72 and no cash sales. Cash Out $19,414.73 is
  rejected; Cash Out $19,414.72 succeeds and leaves zero available.
- Two successive withdrawals cannot together exceed the available balance.
- A Cash In increases the available balance.
- Captured cash sales increase the available balance; non-cash payments do not.
- Cash Out with zero, a negative amount, or a closed session is rejected.

## Scope

This protects the standard POS Cash In/Out action (`pos.session.try_cash_in_out`).
It does **not** impose a general accounting restriction on manual journal entries,
direct creation/editing of bank statement lines, or cash refunds. It does not
correct historical movements. The balance is theoretical; staff should still
count physical cash and transfer withdrawals to the actual destination account.
Cash sales not yet synchronized to the server are not counted as available.
