{
    "name": "POS Cash Out Limit",
    "summary": "Prevent POS cash withdrawals above the available drawer balance",
    "version": "18.0.1.1.0",
    "category": "Point of Sale",
    "license": "LGPL-3",
    "depends": ["point_of_sale"],
    "assets": {
        "point_of_sale._assets_pos": [
            "pos_cash_out_limit/static/src/xml/cash_move_popup.xml",
        ],
    },
    "installable": True,
    "application": False,
}
