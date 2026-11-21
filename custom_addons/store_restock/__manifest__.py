{
    'name': 'Yêu cầu bổ sung hàng',
    'summary': 'Yêu cầu, duyệt, chuyển kho tổng và kiểm nhận tại siêu thị',
    'author': 'Nhóm Odoo Drink Store',
    'version': '20.0.2.0.0',
    'category': 'Inventory',
    'license': 'LGPL-3',
    'depends': ['stock'],
    'data': [
        'security/restock_security.xml',
        'security/ir.access.csv',
        'data/restock_sequence.xml',
        'data/product_categories.xml',
        'wizard/restock_reject_views.xml',
        'wizard/restock_receive_views.xml',
        'views/restock_route_views.xml',
        'views/restock_product_views.xml',
        'views/restock_request_views.xml',
    ],
    'application': True,
    'assets': {
        'web.assets_backend': [
            'store_restock/static/src/js/restock_list.js',
            'store_restock/static/src/scss/restock.scss',
        ],
    },
    'installable': True,
}
