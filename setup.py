from setuptools import setup
import versioneer

setup( 
    version=versioneer.get_version(),
    cmdclass=versioneer.get_cmdclass(),
    entry_points = {
        'console_scripts': ['gpt=gpt.cli:cli'],
    }
)
