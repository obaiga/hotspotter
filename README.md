## Installation

1. Install Anaconda: Anaconda2-5.3.0-Windows-x86. 

Make sure that the installer adds Anaconda to the system PATH  
Make sure that the installer registers it as your default Python

If you already have an Anaconda. The installation path could be [the current Anaconda path] + [\envs], e.g. C:\Users\95316\Anaconda2\envs

2. Install relevant packages

```python
# Requirement package
pip install pylru
pip install utool
pip install opencv-python==3.4.0.14
conda install -c conda-forge qt=4 pyqt=4
#Possible package
pip install argparse==1.1.0
pip install PyHamcrest==1.9.0
```

## Issue1: The source code can directly run on Prompt NOT Spyder. 

Description: 'ImportError: cannot import name QString'

Solution
```python
try:
    from PyQt4.QtCore import QString
except ImportError:
    # QtCore.Qstring can't be imported in Spyder since 2.3.1
    QString = str
```

## To do list

1. Need to learn: Using PyQt4 and QT Design to create Python GUI progra
