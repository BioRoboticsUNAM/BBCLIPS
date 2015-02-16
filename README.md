BBCLIPS
=======

An interface to BlackBoard (our "home-made" message passing and shared variables hub... somewhat equivalent to ROS) from python with a CLIPS interpreter embeded using pyCLIPS.

This software depends on the libraries [pyRobotics](https://github.com/BioRoboticsUNAM/pyRobotics), which is our python API to create modules that connect to the BlackBoard, and [pyCLIPS](http://pyclips.sourceforge.net/web/).

These softwares are all part of the work developed at the Bio-Robotics Laboratory at UNAM, and are used in our service robots.

If someone should be interested in knowing more about any of these projects, you can contact me at adrianrc[dot]89[at]gmail[dot]com.


Documentation
----------------

In order to use this software, a python interpreter is needed (of course), as well as the [pyCLIPS](http://pyclips.sourceforge.net/web/) and [pyRobotics](https://github.com/BioRoboticsUNAM/pyRobotics) libraries.

#### To install pyRobotics

Check the pyRobotics [getting started documentation](http://bioroboticsunam.github.io/pyRobotics/gettingStarted.html).

#### To install pyCLIPS

Go to the [downloads site of pyCLIPS](http://sourceforge.net/projects/pyclips/files/).

* For **WINDOWS**: download the installer from the win32 package.

* For **LINUX**:

  * For **Debian** distributions (such as Ubuntu):
    1. Enter to the Debian Packages folder and download the package to your corresponding architecture (32 or 64 bits)
    2. Execute the command:
      
      `dpkg -i package-name-here.deb`

    (You will probably need superuser permissions.)
  
  * For **RedHat** distributions (such as Fedora) (also to install from source):
    
    Following pyCLIPS instructions from the README file:
    
    1. Make sure you have the package `python-dev` installed.
    2. Download the .tar.gz file that contains the source code from the folder labeld `pyclips`.
    3. In your computer, create a folder called `pyclips_src` and put the compressed file there.
    4. Uncompress from console with the command: `tar -xzvf compressed-name.tar.gz`
    5. Change directory to the uncompressed folder. (`cd pyclips`)
    6. Execute the command: `python setup.py build` (This will download CLIPS source code)
    7. With superuser permissions execute the command `python setup.py install`
    8. You can now delete the folder `pyclips_src` and its contents if you want.
    
    WARNING: It seems it needs to load some environment variables for it to work, so in order to test the
    installation do this:
    
    1. Open a **new** terminal (this will load all necessary environment variables)
    2. Type in `python` and press `Return` to start an interactive session.
    3. Enter `>>> import clips` (it should not throw any error messages)
    4. Enter `>>> clips.Assert('(test_fact)')`

#### To use the tool

- Executing the command `python GUI.py` will open a GUI to use CLIPS, without connecting or doing anything related to BlackBoard.
- Executing the command `python BBCLIPS.py` will connect to BlackBoard and then open the GUI.
- The GUI can read two kinds of files: `*.clp` and either `*.lst` or `*.dat` which should have the same content independently of the extension. `*.clp` files are clips files that contain CLIPS constructs. `*.lst` and `*.dat` files should contain a list of relative paths (relative to that file's location) to other `*.clp`, `*.lst` or `*.dat` files and loads them recursively.
- The program already comes with useful functions and rules to handle communication with BlackBoard. Check out the files inside the CLIPS folder in this project to know how to use them. To know more about BlackBoard and pyRobotics, check out the [pyRobotics documentation](http://bioroboticsunam.github.io/pyRobotics)
- I think the GUI is pretty straight forward for someone who knows how to use the CLIPS interpreter, if there's something not clear enough (or you would like to give some other kind of feedback), please contact me.

#### Additional remarks

This software should be ready to use, however if someone would like to use another python function to call from CLIPS, besides coding the actual function, it should register it to the clips interpreter in the Initialize function in the BBCLIPS.py module.

LICENSE
----------------
This software is distributed under the MIT License.
