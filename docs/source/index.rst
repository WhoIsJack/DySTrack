DySTrack - Dynamic Sample Tracking
==================================


**DySTrack ("diss track")** is a simple, modular, python-based, open-source 
**automated feedback microscopy tool** for live tracking of moving samples like 
migratory cells or tissues.


.. figure:: images/index/DySTrack.gif
    :alt: DySTrack lateral line animation
    :align: center
    :width: 95%

    This example shows the zebrafish *posterior lateral line primordium*, a 
    highly migratory tissue, as it crawls along the flank of a developing 
    embryo. DySTrack was used to enable autonomous tracking and 3D confocal 
    imaging of the primordium over several hours on a Zeiss LSM980 microscope.


DySTrack works on common commercial microscopes, with current out-of-the-box
support covering ``ZEN Black``, ``ZEN Blue``, and ``NIS Elements``. Adaptation 
to any other microscope control software that supports basic macros/automation
is relatively straightforward.

The source code for DySTrack is `on GitHub`_, where you may also contribute to
DySTrack's continued development and maintenance. Please raise a GitHub Issue 
if you encounter a problem with DySTrack or would like to suggest a feature.
Note that the authors cannot guarantee support.

.. admonition:: **Citing DySTrack**
    :class: note

    DySTrack was developed by Jonas Hartmann and Zimeng Wu, in collaboration with 
    many others (acknowledged on GitHub). If you are using DySTrack in your 
    research, please cite the `preprint`_:

    ``Wu, Zimeng, ..., and Hartmann, Jonas; [citation forthcoming]``

.. TODO: ADD LINKS!
.. _on GitHub: https://domain.invalid/
.. _preprint: https://domain.invalid/



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
    * No specialized custom microscope setup or custom control software 
      required
    * Allows easy switching/reuse of the same image analysis pipeline; no 
      lock-in to vendor ecosystems

2. **Simple and modular python tool**
    * Usable, understandable, and extendable for a large and growing fraction 
      of life scientists

3. **Custom python image analysis pipelines**
    * Python is the *de facto* standard for both basic and advanced bioimage 
      analysis
    * DySTrack lets you use it to automate your microscopes!



.. admonition:: **DANGER: USE AT YOUR OWN RISK**
    :class: danger

    Modern microscopes are expensive machines, and automating them comes with
    an inherent risk of damage.
    
    Although DySTrack includes some basic precautions and has been extensively 
    tested, and although several labs have been using (prototypes of) DySTrack 
    successfully for years, **DySTrack is ultimately a minimal tool that does
    not offer comprehensive built-in safety features.**

    We recommend that installation and initial tests be conducted by expert 
    users with experience in microscopy and coding, and that the microscope be 
    supervised during initial tests of your DySTrack setup and of any newly 
    customized pipelines.

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

    Using DySTrack<usage/index>


.. toctree::
    :maxdepth: 2

    Developing DySTrack pipelines<develop/index>


.. toctree::
    :maxdepth: 2

    API Reference<api/index>

