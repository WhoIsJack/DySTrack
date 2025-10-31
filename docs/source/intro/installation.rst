Installation
============

Broadly speaking, three steps are required to get DySTrack running:

1. Installing software dependencies (git and python)

2. Installing the DySTrack python package

3. Setting up the microscope macro / automation workflow

4. Carefully testing that things work as intended


.. admonition:: Installation can be tricky...
    :class: tip

    Installing DySTrack is more complicated than simply using it.

    Before jumping in, be sure to familiarize yourself with 
    :doc:`how DyStrack works<howitworks>` in general and
    :doc:`how to use it</usage/index>` on your particular microscope.

    The person(s) performing the installation should be well-versed with the
    microscope in question and ideally have some experience with python and
    computers in general (though basic knowledge should be sufficient). It can 
    be useful for more than one person to work together, for example a user and
    a member of a microscope facility team.

    Also, do plan in ample time (at least a half-day) to go through all steps
    carefully and to debug any problems that crop up along the way. Since
    operating systems, microscope setups, and software versions all change
    frequently, there are many moving parts that may give rise to unexpected 
    roadblocks.

    If we might have missed something in our documentation or if something 
    seems out of date, we welcome questions and (constructive) feedback; please 
    raise an Issue `on GitHub`_. (Alas, we cannot guarantee that we will be 
    able to solve your problem or address your feedback.)


.. admonition:: Supported configurations
    :class: note

    Currently, DySTrack provides out-of-the-box support for microscopes running
    ``ZEN Black`` via `MyPiC`_ (tested on Zeiss LSM880), ``ZEN Blue`` via 
    `Macros`_ (Zeiss LSM980), or ``NIS Elements`` via `JOBS`_ (Nikon AXR).
    
    Adaptation to any other microscope control software that supports basic 
    macros/automation is also possible but requires extra work (see 
    :doc:`here</usage/other_scopes>`), and support for other systems may be 
    added in the future.

    The microscope PC's Operating System must be Windows 10 or 11.


.. _MyPiC: https://github.com/manerotoni/mypic/
.. _Macros: https://github.com/zeiss-microscopy/OAD
.. _JOBS: https://www.microscope.healthcare.nikon.com/en_EU/products/software/nis-elements/nis-elements-jobs


.. admonition:: Risk of damage
    :class: warning

    Modern microscopes are expensive machines, and automating them comes with
    an inherent risk of damage. 
    
    **Do not install DySTrack without permission from the microscopes
    administrator**, test the installed setup carefully, and always ask for
    help if you are unsure about something!



Part 1: Installing software dependencies
----------------------------------------

TODO!

[Installing git and python/miniforge]


Part 2: Installing the DySTrack python package
----------------------------------------------

TODO!

[Setting up an env]

[From from PyPI or locally (for offline scopes and developers)]


Part 3: Setting up the microscope macro
---------------------------------------

TODO!

[Partially redundant with explanations in Usage sections?]

[Use tabs for different microscopes?!]


Part 4: Testing that things work as intended
--------------------------------------------

TODO? 

[Is there anything worth saying about this? Or remove it (also in overview above)?]

