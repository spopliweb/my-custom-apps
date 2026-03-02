# Copyright <Year> <Your Name/Company>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

import logging
import os
import re
import tempfile
from html import unescape

from odoo import api, models

_logger = logging.getLogger(__name__)

try:
    import fitz  # PyMuPDF
except ImportError:
    _logger.warning(
        "The PyMuPDF (fitz) library is not installed. TOC generation will fail."
    )


class ReportActions(models.AbstractModel):
    _inherit = "ir.actions.report"

    @api.model
    def _render_qweb_pdf(self, report_ref, res_ids, data=None, **kwargs):
        """
        Intercept PDF rendering to inject a Table of Contents.
        The process involves:
        1. Rendering the original report.
        2. Scanning for headings to map page numbers.
        3. Calculating TOC length to offset page links.
        4. Merging the TOC and re-calculating footers.
        """
        report = self._get_report(report_ref)

        # Render original report normally
        main_pdf_bytes, content_type = super()._render_qweb_pdf(
            report_ref, res_ids, data=data, **kwargs
        )

        # Avoid recursion: If this is the TOC report itself, return immediately
        if report.report_name == "report_toc.report_toc_template":
            return main_pdf_bytes, content_type

        # Check if we need to add a TOC (if configuration records exist)
        toc_records = self.env["report.toc"].search(
            [
                ("main_report_id", "=", report.id),
                ("active", "=", True),
            ],
            limit=1,
        )

        if not toc_records:
            return main_pdf_bytes, content_type

        # ANALYSIS PHASE: Find headings and calculate TOC length
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as f:
            f.write(main_pdf_bytes)
            main_pdf_path = f.name

        doc = fitz.open(main_pdf_path)
        toc_page_map = {}

        # Scan Main PDF for Headings defined in the TOC configuration
        for line in toc_records.toc_line_ids:
            search_text = unescape(line.search_heading).upper().strip()
            for i, page in enumerate(doc, start=1):
                page_text = page.get_text().upper()
                if search_text in page_text:
                    toc_page_map[line.id] = i
                    break

        doc.close()
        if os.path.exists(main_pdf_path):
            os.unlink(main_pdf_path)

        # CALCULATE OFFSET FOR TOC LINKS
        # 0-based index for insertion (e.g., insert_page 2 becomes index 1)
        insert_index = max(0, toc_records.insert_page - 1)

        # Render a "Dummy" TOC to count how many pages the TOC itself takes
        toc_report = toc_records.toc_report_id
        temp_toc_data = dict(data or {})
        temp_toc_data.update({"toc_page_map": toc_page_map, "toc_id": toc_records.id})

        dummy_toc_bytes, _ = toc_report._render_qweb_pdf(
            toc_report.report_name, [toc_records.id], data=temp_toc_data
        )

        with fitz.open(stream=dummy_toc_bytes, filetype="pdf") as dummy_doc:
            toc_len = dummy_doc.page_count

        # Apply logic: If a heading is AFTER insertion point, add TOC length to page number
        final_page_map = {}
        insertion_point_1_based = insert_index + 1

        for line_id, original_page in toc_page_map.items():
            if original_page >= insertion_point_1_based:
                final_page_map[line_id] = original_page + toc_len
            else:
                final_page_map[line_id] = original_page

        # RENDER REAL TOC & MERGE
        toc_data = dict(data or {})
        toc_data.update(
            {
                "toc_page_map": final_page_map,
                "toc_id": toc_records.id,
            }
        )

        toc_pdf_bytes, _ = toc_report._render_qweb_pdf(
            toc_report.report_name, [toc_records.id], data=toc_data
        )

        final_doc = fitz.open(stream=main_pdf_bytes, filetype="pdf")
        toc_doc = fitz.open(stream=toc_pdf_bytes, filetype="pdf")

        # Insert TOC at the specified location
        final_doc.insert_pdf(toc_doc, start_at=insert_index)

        # TARGETED FOOTER REDACTION AND RE-PAGINATION
        raw_html = toc_records.footer_content or ""
        clean_footer_text = re.sub("<[^<]+?>", "", raw_html)
        total_pages = final_doc.page_count

        for pg_num, page in enumerate(final_doc):
            page_width = page.rect.width
            page_height = page.rect.height

            # Define a tight box at the bottom for redaction
            bottom_footer_area = fitz.Rect(0, page_height - 80, page_width, page_height)

            if hasattr(page, "add_redact_annot"):
                page.add_redact_annot(bottom_footer_area, fill=(1, 1, 1))

            page.apply_redactions()

            # Insert Custom Footer Content
            footer_content_box = fitz.Rect(
                0, page_height - 60, page_width, page_height - 35
            )
            page.insert_textbox(
                footer_content_box,
                clean_footer_text,
                fontsize=8,
                fontname="helv",
                color=(0.3, 0.3, 0.3),
                align=1,
            )

            # Insert New Page Numbering
            new_text = f"Page {pg_num + 1} of {total_pages}"
            new_footer_box = fitz.Rect(0, page_height - 30, page_width, page_height - 5)

            page.insert_textbox(
                new_footer_box,
                new_text,
                fontsize=9,
                fontname="helv",
                color=(0.3, 0.3, 0.3),
                align=1,  # Center
            )

        output = final_doc.tobytes()
        final_doc.close()
        toc_doc.close()

        return output, content_type