{
    'name': 'POS Amount Based Qunatity Calculator',
    'version': '18.0.1.0.0',
    'category': 'Point of Sale',
    'summary': 'Type any amount — POS instantly calculates exact product quantity. Perfect for fruit, vegetable, spice & bulk retail stores.',
    'author': 'Spopli Web Development & Services',
    'company': 'Spopli Web Development & Services',
    'maintainer': 'Spopli Web Development & Services',
    'website': 'https://spopli.com', 
    'depends': ['point_of_sale', 'web', 'mail'],
    'assets': {
        'point_of_sale._assets_pos': [
            'custom_button/static/src/js/custom_button.js',
            'custom_button/static/src/xml/custom_button.xml',
            'custom_button/static/src/css/custom_button.css',
        ],
    },
    'images': [
        'static/description/banner.png',
        'static/description/icon.png',
    ],
    'price': 10,
    'currency': 'USD',
    'installable': True,
    'application': True,
    'license': 'OPL-1',
}
