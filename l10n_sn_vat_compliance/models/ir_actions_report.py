from odoo import api, models


class IrActionsReport(models.Model):
    _inherit = "ir.actions.report"

    @api.model
    def _build_wkhtmltopdf_args(
        self,
        paperformat_id,
        landscape,
        specific_paperformat_args=None,
        set_viewport_size=False,
    ):
        args = super()._build_wkhtmltopdf_args(
            paperformat_id,
            landscape,
            specific_paperformat_args=specific_paperformat_args,
            set_viewport_size=set_viewport_size,
        )
        # wkhtmltopdf on Windows otherwise interprets UTF-8 report files using
        # the active ANSI code page and corrupts French accented characters.
        if "--encoding" not in args:
            args.extend(["--encoding", "utf-8"])
        return args
