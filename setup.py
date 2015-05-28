try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

config = {
    'description': 'Business day calculations',
    'author': 'Dafydd Francis',
    'url': 'URL to get it at.',
    'download_url': 'Where to download it.',
    'author_email': 'dafydd.francis@andwhathave.eu',
    'version': '0.1',
    'install_requires': ['nose', 'pyyaml', 'python-dateutil'],
    'packages': ['business'],
    'package_data': {
        'business': ['data/*.yml'],
    },
    'scripts': [],
    'name': 'business'
}

setup(**config)
