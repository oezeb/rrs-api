from setuptools import find_packages, setup

setup(
    name='reservation_system',
    version='1.0.0',
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        'flask', 'flask_restul'
        'pyjwt',
        # 'pytest', 'coverage',
    ],
)