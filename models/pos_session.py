"""Guard the standard Odoo 18 POS Cash In/Out operation."""

from math import isfinite

from odoo import _, models
from odoo.exceptions import UserError


class PosSession(models.Model):
    _inherit = "pos.session"

    def _cash_out_limit_available(self):
        """Return the theoretical cash available in an open POS session.

        Compute it from the database after locking the session, instead of using
        the non-stored cash_register_balance_end value that may be cached by an
        earlier read in the current request. Only this session's cash journal
        counts; bank statement lines cannot fund a cash withdrawal.
        """
        self.ensure_one()
        cash_method = self.payment_method_ids.filtered("is_cash_count")[:1]
        if not cash_method:
            raise UserError(_("This POS session has no cash payment method."))

        payment_domain = self._get_captured_payments_domain() + [
            ("payment_method_id", "=", cash_method.id),
        ]
        payment_totals = self.env["pos.payment"]._read_group(
            payment_domain, aggregates=["amount:sum"]
        )
        cash_payments = payment_totals[0][0] if payment_totals else 0.0

        statement_totals = self.env["account.bank.statement.line"]._read_group(
            [
                ("pos_session_id", "=", self.id),
                ("journal_id", "=", self.cash_journal_id.id),
            ],
            aggregates=["amount:sum"],
        )
        cash_movements = statement_totals[0][0] if statement_totals else 0.0
        return self.cash_register_balance_start + cash_payments + cash_movements

    def try_cash_in_out(self, _type, amount, reason, extras):
        if _type not in ("in", "out"):
            raise UserError(_("Invalid cash movement type."))
        if (
            isinstance(amount, bool)
            or not isinstance(amount, (int, float))
            or not isfinite(amount)
            or amount <= 0
        ):
            raise UserError(_("The cash movement amount must be greater than zero."))

        if _type == "out":
            sessions = self.filtered("cash_journal_id")
            # Serialize simultaneous Cash Out requests on the same session.
            # Locking before the balance query also makes the second request
            # observe the first withdrawal after it commits.
            for session in sessions.sorted("id"):
                self.env.cr.execute(
                    "SELECT id FROM pos_session WHERE id = %s FOR UPDATE",
                    [session.id],
                )
                if session.state not in ("opened", "closing_control"):
                    raise UserError(_("Cash can only be withdrawn from an open POS session."))

                available = session._cash_out_limit_available()
                if session.currency_id.compare_amounts(amount, max(available, 0.0)) > 0:
                    raise UserError(
                        _(
                            "Cash Out blocked in %(session)s: requested %(requested)s, "
                            "but only %(available)s is available in the drawer.",
                            session=session.display_name,
                            requested=session.currency_id.format(amount),
                            available=session.currency_id.format(max(available, 0.0)),
                        )
                    )

        return super().try_cash_in_out(_type, amount, reason, extras)
