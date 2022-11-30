from setuptools import setup

setup(name='LBTK',
    version='0.1',
    description='Language bias working repo',
    url='https://github.com/michaelsaxon/LangBiasGenImg',
    author='Michael Saxon',
    author_email='saxon@ucsb.edu',
    packages=['langbiastoolkit'],
    install_requires=[
        'transformers',
        'click',
        'pytorch_lightning',
        'wandb'
    ],
    zip_safe=False
)
