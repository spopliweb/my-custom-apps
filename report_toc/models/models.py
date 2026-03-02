# Copyright <Year> <Your Name/Company>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ReportTOC(models.Model):
    _name = "report.toc"
    _description = "Report Table of Contents"
    _order = "name"

    name = fields.Char(
        string="TOC Name",
        required=True,
    )

    active = fields.Boolean(
        default=True,
        help="If unchecked, it will allow you to hide the TOC configuration "
        "without removing it.",
    )

    insert_page = fields.Integer(
        string="Insert Page",
        default=1,
        help="The page number where the TOC will be inserted.",
    )

    main_report_id = fields.Many2one(
        comodel_name="ir.actions.report",
        string="Main Report",
        required=True,
        domain="[('report_type', '=', 'qweb-pdf')]",
        help="The original report where you want to add the TOC.",
    )

    toc_report_id = fields.Many2one(
        comodel_name="ir.actions.report",
        string="TOC Report Template",
        required=True,
        domain="[('report_type', '=', 'qweb-pdf')]",
        default=lambda self: self.env.ref(
            "report_toc.action_report_toc_report", raise_if_not_found=False
        ),
        help="The QWeb template used to render the TOC pages.",
    )

    footer_content = fields.Html(
        string="Report Footer",
        help="Enter company address or disclaimer here for the footer. "
        "Do not include page numbers as they are handled automatically.",
        default="<p class='text-center'>123 Business Street, City, Country</p>",
    )

    toc_line_ids = fields.One2many(
        comodel_name="report.toc.line",
        inverse_name="toc_id",
        string="TOC Lines",
    )


class ReportTOCLine(models.Model):
    _name = "report.toc.line"
    _description = "Report TOC Line"
    _order = "sequence, id"
    _rec_name = "toc_heading"

    toc_id = fields.Many2one(
        comodel_name="report.toc",
        string="TOC Reference",
        ondelete="cascade",
        required=True,
    )

    sequence = fields.Integer(
        default=10,
    )

    toc_heading = fields.Char(
        string="TOC Heading",
        required=True,
        help="Heading text that will be displayed in the TOC page.",
    )

    search_heading = fields.Char(
        string="Search Text in PDF",
        required=True,
        help="The exact text the system should look for in the generated PDF "
        "to determine the page number.",
    )