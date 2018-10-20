from setuptools import setup, find_packages

version = "0.1"

setup(
    name='ghobserver',
    packages=find_packages(),
    include_package_data=True,
    version=version,
    description='Python package for Ghobserver',
    author='synw',
    author_email='synwe@yahoo.com',
    url='https://github.com/synw/ghobserver',
    download_url='https://github.com/synw/ghobserver/releases/tag/' + version,
    keywords=['github'],
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.6',
    ],
    install_requires=[
        'dataswim',
        'arrow',
        "notify2",
        "requests",
    ],
    zip_safe=False
)
