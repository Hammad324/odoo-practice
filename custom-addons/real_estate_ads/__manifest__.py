{
    "name": "Real Estate Ads",
    "version": "1.0",
    "website": "https://odooguys.com",
    "author": "Hammad Farrukh Rohilla",
    "description": """
    Real Estate Module to show available properties.
    """,
    "category": "Sales",
    "depends": ['base', 'mail', 'utm', 'website'],
    "data": [

        # Security Groups
        'security/ir.model.access.csv',
        'security/res_groups.xml',
        'security/model_access_rights.xml',
        'security/ir_rule.xml',

        # Views
        'views/property_view.xml',
        'views/property_type_view.xml',
        'views/property_tag_view.xml',
        'views/property_offer_view.xml',
        'views/menu_items.xml',

        # Data Files
        # 'data/property_type.xml',
        'data/estate.property.type.csv',
        'data/mail_template.xml',

        # Report
        'report/report_template.xml',
        'report/property_report.xml',
    ],
    "demo":[
        "demo/property_tag.xml"
    ],
    "assets": { # add the xml and js files.
        "web.assets_backend": [ # main error was here when creating a custom action, i named this as web.assets.backend, it should be web.assets_backend
            "real_estate_ads/static/src/js/my_custom_tag.js",
            "real_estate_ads/static/src/xml/my_custom_tag.xml"
        ]
    },
    "application": True,
    "Installable": True,
    "license": "LGPL-3",
}