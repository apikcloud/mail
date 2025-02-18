from odoo import models
from odoo.tools import config
from odoo.tools.safe_eval import safe_eval

from ..utils import _id_get


class MailThread(models.AbstractModel):
    _inherit = "mail.thread"

    def _message_add_suggested_recipient(
        self, result, partner=None, email=None, lang=None, reason=""
    ):
        result = super()._message_add_suggested_recipient(
            result, partner=partner, email=email, lang=lang, reason=reason
        )
        test_condition = config["test_enable"] and not self.env.context.get(
            "test_restrict_follower"
        )
        if test_condition or self.env.context.get("no_restrict_follower"):
            return result
        domain = self.env[
            "mail.wizard.invite"
        ]._mail_restrict_follower_selection_get_domain()
        eval_domain = safe_eval(
            str(domain), locals_dict={"ref": lambda str_id: _id_get(self.env, str_id)}
        )
        items_to_remove = []
        for item in result:
            partner_id = item.get("partner_id", False)
            if partner_id:
                partner_count = self.env["res.partner"].search_count(
                    [("id", "=", partner_id)] + eval_domain
                )
                if not partner_count:
                    items_to_remove.append(item)
        for item in items_to_remove:
            result.remove(item)

        return result
