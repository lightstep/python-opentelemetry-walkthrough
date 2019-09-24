from setuptools import setup, find_packages

setup(
    name='python-opentelemetry-walkthrough',
    version='0.1.0',
    description='Python OpenTelemetry Walkthrough',
    long_description='',
    author='LightStep',
    license='',
    install_requires=[],
    tests_require=[],
    classifiers=[
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3',
    ],

    keywords=[
        'opentracing',
        'lightstep',
        'traceguide',
        'tracing',
        'microservices',
        'distributed'
    ],
    packages=find_packages(exclude=['docs*', 'tests*', 'sample*']),
)
