# POS Cash Out Limit (Odoo 18)

Blocks the standard POS **Cash Out** operation when the requested amount exceeds
the theoretical cash available in that POS session. The available balance is:

`opening cash + captured cash payments + POS cash statement lines`

The check runs on the Odoo server, displays the requested and available amounts,
and serializes concurrent withdrawals from the same session. Cash In is unchanged.
The blocking messages are written in Spanish directly, so they do not depend on
the user's active Odoo language or a regional translation file.

While entering an amount in the POS Cash In/Out popup, a live preview below the
field uses Odoo's own currency formatter. For example, entering `450000` in an
Argentine-peso POS displays `$ 450.000,00`. The editable field and submitted
amount are left unchanged.

## Install

1. Copy this directory into an Odoo 18 custom-addons path.
2. Restart Odoo, update the Apps list, and install or upgrade **POS Cash Out Limit**.
3. Reload the POS browser page so the updated frontend assets are loaded.
4. Test in a staging database before deploying to production.

## Acceptance checks

- Open a session with $19,414.72 and no cash sales. Cash Out $19,414.73 is
  rejected; Cash Out $19,414.72 succeeds and leaves zero available.
- Two successive withdrawals cannot together exceed the available balance.
- A Cash In increases the available balance.
- Captured cash sales increase the available balance; non-cash payments do not.
- Cash Out with zero, a negative amount, or a closed session is rejected.
- Enter `450000` and verify the preview reads `$ 450.000,00` in an ARS POS;
  confirm that the server still receives 450000, not 450 or 45000000.

## Scope

This protects the standard POS Cash In/Out action (`pos.session.try_cash_in_out`).
It does **not** impose a general accounting restriction on manual journal entries,
direct creation/editing of bank statement lines, or cash refunds. It does not
correct historical movements. The balance is theoretical; staff should still
count physical cash and transfer withdrawals to the actual destination account.
Cash sales not yet synchronized to the server are not counted as available.
