
{
    "name": "Employee Document Update",
    "summary": "Manage your employee documents",
    "version": "1.0",
    "category": "Human Resources",
    "license": "AGPL-3",
    "author": "Fanasina",
    "website": "",
    "depends": [
        "employee_documents_expiry",
        "base",
        "hr"
    ],
    'data': [
        "security/ir.model.access.csv",
        # "views/hr_skill.xml",
        # "views/hr_employee.xml",
        "views/employee_document_view_inherit.xml",
    ],
    'images': [
        "static/img/folder-invoices.png",
    ],
    'installable': True,
}
