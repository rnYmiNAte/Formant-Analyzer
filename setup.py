# setup.py
from setuptools import setup, find_packages
import os

# Get the long description from README.md
here = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='formant-analyzer',
    version='0.1.0',
    description='Extract and visualize vowel formants (F1, F2) from WAV audio files',
    long_description=long_description,
    long_description_content_type='text/markdown',
    
    author='PraatFoundation',
    # author_email='your.email@example.com',          # ← add your real email if desired
    url='https://github.com/yourusername/formant-analyzer',  # ← update with real repo URL
    
    # Important: src/ layout
    package_dir={'': 'src'},
    packages=find_packages(where='src'),
    
    python_requires='>=3.8',
    
    install_requires=[
        'numpy>=1.24.0',
        'scipy>=1.10.0',
        'matplotlib>=3.7.0',
        'soundfile>=0.12.0',     # preferred over wave for robustness
    ],
    
    extras_require={
        'dev': [
            'pytest>=7.4',
            'pytest-cov',
            'black>=23.0',
            'ruff',                  # fast modern linter/formatter
            'mypy',
        ],
        'test': ['pytest>=7.4'],
    },
    
    # Makes `formant-analyzer` command available after pip install
    entry_points={
        'console_scripts': [
            'formant-analyzer = main:main',   # assumes main.py is in root
        ],
    },
    
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Science/Research',
        'Topic :: Scientific/Engineering :: Audio Analysis',
        'Topic :: Multimedia :: Sound/Audio :: Analysis',
        'License :: OSI Approved :: MIT License',  # change if using different license
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Operating System :: OS Independent',
    ],
    
    keywords=[
        'formants', 'speech', 'phonetics', 'acoustics',
        'vowel', 'F1', 'F2', 'LPC', 'formant-analysis'
    ],
    
    # If you later add sample data, license file, etc.
    include_package_data=True,
    zip_safe=False,
    
    # Optional: project_urls if you want more links in PyPI
    project_urls={
        'Bug Tracker': 'https://github.com/yourusername/formant-analyzer/issues',
        'Source':     'https://github.com/yourusername/formant-analyzer',
    },
)
