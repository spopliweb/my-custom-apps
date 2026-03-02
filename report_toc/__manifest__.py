# Copyright 2025 Abdulla Basil
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Report Table of Contents (ToC)",
    "summary": "Generate automated Table of Contents for PDF reports to improve document navigation",
    "version": "18.0.1.0.0",
    "category": "Reporting",
    "author": "Abdulla Basil",
    "website": "https://github.com/Abdulla-basil/report_toc_module.git",  # Update with your actual URL
    "license": "AGPL-3",
    "application": True,
    "installable": True,
    "auto_install": False,
    "depends": [
        "base",
        "web",
    ],
    "external_dependencies": {
        "python": ["pymupdf"],
    },
    "data": [
        "security/ir.model.access.csv",
        "views/views.xml",
        "reports/report_action.xml",
        "reports/report_template.xml",
    ],
    'images': [
        'static/description/banner.png',
        'static/description/icon.png',
    ],
    "description": """
Table of Contents for Odoo Reports
==================================
This module allows users to automatically generate a Table of Contents (ToC) for complex PDF reports. 
It is designed to improve document navigation for long business records such as catalogs, 
lengthy quotations, or technical manuals.

Key Features
------------
* Automatically generate a Table of Contents (ToC).
* Customise ToC styling via standard QWeb templates.
* Improve document navigation for long business records.
* Seamless integration with existing Odoo PDF reports.
* Lightweight and easy to configure.

Use Case
--------
Perfect for companies generating large reports where page numbers and section 
references are critical for professional presentation.
    """,
}