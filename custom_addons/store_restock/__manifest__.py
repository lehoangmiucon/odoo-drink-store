{
    'name': 'Yêu cầu bổ sung hàng',
    'summary': 'Nhân viên gửi phiếu và quản lý duyệt hoặc từ chối',
    'version': '20.0.1.0.8',
    'category': 'Inventory',
    'license': 'LGPL-3',
    'depends': ['product'],
    'data': [
        'security/restock_security.xml',
        'security/ir.access.csv',
        'data/restock_sequence.xml',
        'wizard/restock_reject_views.xml',
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
