from distutils.core import setup

setup(

    name='xbee2mqtt',
    version='0.99',
    description='Xbee WSN MQTT publisher',
    author='Xose Pérez',
    author_email='xose.perez@gmail.com',
    url='http://github.com/xoseperez/xbee2mqtt',
    download_url='http://github.com/xoseperez/xbee2mqtt',
    license='GNU General Public License v3 or later (GPLv3+)',
    py_modules=['xbee2mqtt'],

    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)'
        'Operating System :: MacOS :: MacOS X',
        'Operating System :: Microsoft :: Windows',
        'Operating System :: POSIX',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Topic :: Communications',
        'Topic :: Internet',
    ]

)
