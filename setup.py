from setuptools import setup

setup(
    name='yonbt',
    version='1.0.0b1',
    url='https://github.com/Kellador/YoNBT',
    packages=['yonbt'],
    install_requires=[
        'mutf8'
    ],
    python_requires='>=3.6',
    author='Kellador',
    license='MIT',
    description='A python library for Mojang\'s NBT file format and its various uses.',
    keywords='nbt minecraft-nbt minecraft-region',
    classifiers=[
        'Development Status :: 2 - Beta',
        'License :: OSI Approved :: MIT License',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Libraries',
        'Programming Language :: Python :: 3.6'
    ]
)
