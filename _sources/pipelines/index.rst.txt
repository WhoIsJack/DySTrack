Image analysis pipelines
========================


When the microscope produces a new (prescan) image, the DySTrack manager
detects it and triggers an **image analysis pipeline** to load the image, 
process it, and return new coordinates for subsequent acquisitions.

The first section of this chapter describes pipelines that are available in the
DySTrack repository, which is of interest for all users. The other sections
dive more deeply into how pipelines are constructed, which is primarily 
relevant for users who seek to develop their own pipelines.


.. toctree::
    :maxdepth: 2

    Available pipelines<available>
    Anatomy of a pipeline<anatomy>
    Developing pipelines<develop>
    Advanced tools & strategies<advanced>

    