import io

from setuptools import find_packages, setup

with io.open('README.rst', 'rt', encoding='utf8') as f:
    readme = f.read()

setup(
    name='utair',
    version='0.1.0',
    url='https://github.com/Kolaer',
    maintainer_email='overlordin777@gmail.com',
    description='Utair test project.',
    long_description=readme,
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        'flask',
        'mongoengine',
        'flask-mongoengine',
        'python-dateutil',
    ],
    extras_require={
        'example': [
            'requests',
        ],
    },
)
