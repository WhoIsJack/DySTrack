.. include:: /_includes/add_a_bit_of_extra_empty_space.rst

DySTrack - Dynamic Sample Tracking
==================================

.. raw:: html
    
    <!-- Logo inserted next to title, with hacked custom spacings... -->
    <div style="display: flex; justify-content: space-between; margin-bottom: -100px">
        <p></p>
        <img 
            src="_static/DySTrack_logo_dark.svg" 
            class="only-dark" 
            alt="DySTrack Logo Dark" 
            style="height: 120px; transform: translate(-25px, -110px)"
        >
        <img 
            src="_static/DySTrack_logo_lite.svg" 
            class="only-light" 
            alt="DySTrack Logo Light" 
            style="height: 120px; transform: translate(-25px, -110px)"
        >
    </div>



**DySTrack ("diss track")** is a simple, modular, python-based, open-source 
**automated feedback microscopy tool** for live tracking of moving samples like 
migratory cells or tissues during acquisition.


.. figure:: images/landing_page/pllp_movie.gif
    :alt: DySTrack lateral line primordium animation (downsampled)
    :align: center
    :width: 95%

    This example shows the zebrafish *posterior lateral line primordium*, a 
    highly migratory tissue, as it crawls along the flank of a developing 
    embryo. DySTrack was used to enable autonomous tracking and 3D confocal 
    imaging of the primordium over several hours on a Zeiss LSM980 microscope.
    (This gif is maximum z-projected and downsampled to limit file size.)


DySTrack works on common commercial microscopes, with current out-of-the-box
support covering ``ZEN Black`` (via `MyPiC`_), ``ZEN Blue`` (via `Macros`_), 
and ``NIS Elements`` (via `JOBS`_). Adaptation to any other microscope control 
software that supports basic macros/automation is also possible, and support
for other systems may be added in the future.

The **source code** for DySTrack is `on GitHub`_, where you may also 
`contribute`_ to DySTrack's continued development and maintenance. Please raise 
a GitHub Issue if you encounter a problem with DySTrack or would like to 
suggest a new feature. *Note that the authors cannot guarantee support.*


.. admonition:: **Citing DySTrack**
    :class: note

    DySTrack was developed by Jonas Hartmann and Zimeng Wu, in collaboration 
    with many others (acknowledged on GitHub). If you are using DySTrack in 
    your research, please cite `the preprint`_:

    .. code-block:: none

      @article {Wu2025.12.02.691816,
        author = {Wu, Zimeng and Voiculescu, Octavian and Mongera, Alessandro and Mayor, Roberto and Wong, Mie and Hartmann, Jonas},
        title = {DySTrack: a modular smart microscopy tool for live tracking of dynamic samples on modern commercial microscopes},
        elocation-id = {2025.12.02.691816},
        year = {2025},
        doi = {10.64898/2025.12.02.691816},
        publisher = {Cold Spring Harbor Laboratory},
        URL = {https://www.biorxiv.org/content/10.64898/2025.12.02.691816v1},
        journal = {bioRxiv}
      }


.. _MyPiC: https://github.com/manerotoni/mypic/
.. _Macros: https://github.com/zeiss-microscopy/OAD
.. _JOBS: https://www.microscope.healthcare.nikon.com/en_EU/products/software/nis-elements/nis-elements-jobs
.. _contribute: https://github.com/WhoIsJack/DySTrack/contribute
.. _the preprint: https://www.biorxiv.org/content/10.64898/2025.12.02.691816v1



Why use DySTrack?
-----------------

DySTrack is useful when imaging moving, growing, or drifting samples where the
microscope's limited field of view becomes an issue. Instead of sitting at the
microscope all day and all night, or accepting lower quality (reducing 
magnification to increase the field of view) or lower time-resolution (using 
tiled/stitched acquisition to cover a larger field of view), DySTrack can be
deployed to have the microscope autonomously follow cells or tissues of 
interest.

Some advantages of DySTrack over other tools include:
   
1. **Minimal interface with the microscope**

   * Can interface with any microscope control software that has basic
     macro/automation support
   * No specialized custom microscope setup or custom control software required
   * Allows easy switching/reuse of the same image analysis pipeline; no 
     lock-in to vendor ecosystems

2. **Simple and modular python tool**

   * Usable, understandable, and extendable for a large & growing fraction of
     life scientists

3. **Custom python image analysis pipelines**

   * Python is the *de facto* standard for both basic and advanced bioimage 
     analysis
   * DySTrack lets you use it to automate your microscopes!



A word of warning...
--------------------

.. admonition:: **DANGER: USE AT YOUR OWN RISK!**
    :class: danger

    Modern microscopes are expensive machines, and automating them comes with
    an inherent **risk of damage**.
    
    Although DySTrack includes some basic precautions and has been extensively 
    tested, and although several labs have been using (prototypes of) DySTrack 
    successfully for years, **DySTrack is ultimately a minimal tool that does
    not offer comprehensive built-in safety features.**

    We recommend that installation and initial tests be conducted by expert 
    users with experience in microscopy and coding, and that the microscope be 
    monitored during initial tests and when running newly customized pipelines.

    **Users are advised that the authors provide no warranty of any kind for 
    DySTrack and are not liable for damages of any kind resulting from its 
    use.** Note the relevant part of DySTrack's MIT license:

        THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
        IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
        FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
        AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
        LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
        OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
        SOFTWARE.



Table of contents
-----------------

.. toctree::
    :maxdepth: 2

    Getting started<intro/index>


.. toctree::
    :maxdepth: 2

    Running DySTrack<usage/index>


.. toctree::
    :maxdepth: 2

    Image analysis pipelines<pipelines/index>


.. toctree::
    :maxdepth: 2

    API Reference<api/index>

