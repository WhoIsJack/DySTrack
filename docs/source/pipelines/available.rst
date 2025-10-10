Available image analysis pipelines
==================================

Whenever the microscope produces a new (prescan) image, the DySTrack manager
detects it and calls an image analysis pipeline to load the image, process it,
and return new coordinates for the subsequent (main scan) acquisition.

DySTrack comes with a few pre-configured pipelines, which are described below.
More pipelines may be added in the future. If you are developing you own 
pipeline, please review the other pages :doc:`in this section<index>`.

.. admonition:: Note
    :class: note
    
    All pipelines start by loading a target image and all pipelines limit the
    amount by which the z-position can be changed within a single time step (as 
    a safety feature). See :doc:`Anatomy of a pipeline<anatomy>` for more info.

*Currently available DySTrack pipelines:*



Center-of-mass tracking
-----------------------

The most straightforward use case for automated tracking is to keep a bright 
foreground object (e.g. a labeled cell, tissue, or organoid) in the center of
the field of view as it slowly moves or drifts. This can be accomplished by 
tracking the center of mass of the signal in the image.

This pipeline first applies some Gaussian smoothing to reduce noise in the
input image, followed by one of three different methods of retrieving the
center of mass, some of which may work better than others depending on the type 
of sample:

* ``"intensity"``: This method computes the center of mass of all signal in the
  image/stack. It may perform better than the others when tracking sparsely 
  labeled tissues.

* ``"otsu"``: This method uses standard Otsu thresholding to mask foreground
  signal, then retains only the largest foreground object and finds the center
  of mass of its mask. This often performs well for tracking of distinct,
  densely-labeled objects/tissues/organoids.

  .. admonition:: Tip: Start here!
      :class: tip
      
      For many simple tracking tasks, Otsu-based center-of-mass tracking may be
      a good starting point!

* ``"objct"``: This method applies object-count thresholding to mask foreground
  signal, which is a method that can be more robust than Otsu if there is a lot
  of structure in the background signal. This method has historically been very
  robust for lateral line tracking (see below), but usually probably shouldn't 
  be your first choice. As with the Otsu mask, this method retains only the 
  largest foreground object and returns the center of mass of its mask as the 
  new coordinates.

Note that all these methods assume the foreground signal to be bright. For
transmission imaging, where the object of interest will usually appear dark,
an inversion of the input image needs to be added to the pipeline.

For details on the function's call signature, see the
:doc:`API reference</api/pipelines/dystrack.pipelines.center_of_mass>`.



Tracking the zebrafish lateral line primordium
----------------------------------------------

This pipeline is how the example on the landing page was generated:

.. figure:: /images/landing_page/pllp_movie.gif
    :alt: DySTrack lateral line primordium animation
    :align: center
    :width: 95%

The zebrafish posterior lateral line primordium is a group of embryonic cells 
in fish and amphibia that undergo collective cell migration over a large 
distance along the embryo's flank, periodically depositing clusters of cells 
that develop into sensory organs, so-called neuromasts. Because of its coherent
long-range migration behavior, the lateral line primordium is an ideal use case
for DySTrack (and indeed inspired the development of the first DySTrack 
prototype).

The lateral line pipeline employs Gaussian smoothing and object-count 
thresholding to find a foreground mask, then retains only the largest object
therein (the primordium itself). The new coordinates for z and y are the 
centers of mass for this mask, whereas the new x-coordinate is calculated based
on the leading edge such that migratory movement is anticipated.

.. admonition:: Convention
    :class: note
    
    By convention, pipelines assume that embryos are mounted with the anterior
    to the left, so the leading edge of the primordium is on the right of the
    image.

For details on the function's call signature, see the
:doc:`API reference</api/pipelines/dystrack.pipelines.lateral_line>`.

.. collapse:: [Expand to view more details on this pipeline]
    
    Object-count thresholding applies a series of thresholds (from low to high) 
    and checks how many individual objects result at each threshold. In images 
    with a patterned background (such as the skin cells in the ``cldnB:EGFP``
    transgenic zebrafish line), the number of individual objects is high at low
    thresholds and then rapidly decreases before reaching a low trough or 
    plateau, which corresponds to a good threshold value.

    Only the largest object from the resulting foreground mask is retained, 
    which robustly corresponds to the main body of the lateral line primordium
    itself.

    Since the primordium is aligned with the x-axis and migrating from left to
    right (by convention, see above), the leading edge can be detected as the
    right-most voxel of the foreground mask. The new x-coordinate is then 
    calculated such that the leading edge will end up 1/5th of the x-axis 
    extent behind the right border of the image, leaving enough space for 
    migration before the next prescan. (More optimal alternatives to this 
    approach could conceivably be implemented, but this solution has 
    empirically proven highly robust.)

    Two additional fallback mechanisms are in place to handle occasional 
    issues. First, if the leading edge position is too far back (i.e. in the
    rear half of the image), the masking likely failed to pick up a significant
    chunk of the tissue. A default distance of 1/8th of the x-axis extent is 
    moved in this case, though how reasonable this is depends on the field of
    view and acquisition speed. Second if the mask touches the right border of
    the image, a default catch-up distance of 1/5th of the x-axis extent is 
    moved
    
    In future, this explicit handling of issues could be improved using tools
    such as PID controllers or Kalman filters.



Tracking regression of the chick Hensen's node
----------------------------------------------

The organizer of chick gastrulation, Hensen's node, regresses caudally through 
the primitive streak as gastrulation proceeds. This pipeline is used to track 
the node based on electroporated labeling and to image cells that leave the 
node toward the anterior.

The chick node pipeline uses a different approach to find coordinates that is 
not based on foreground masking. Instead, it defines simple models of expected
instensity profiles along each axis, then fits these models to the observed
intensity profiles, and finally uses parameters of the models as new
coordinates.

.. admonition:: Convention
    :class: note
    
    By convention, pipelines assume that embryos are mounted with the anterior
    to the left, so the node regresses toward the right and labeled cells leave
    the node toward the left.

For details on the function's call signature, see the
:doc:`API reference</api/pipelines/dystrack.pipelines.chick_node>`.

.. collapse:: [Expand to view more details on this pipeline]

  To track z, a mean-intensity projection is performed over the y and x axis to
  get a 1d intensity profile along the z-axis. A Gaussian curve is then fit to 
  this profile and its mean is used as the new z coordinate.

  The equivalent is done to track y (mean-projecting x and z).

  To track x, a mean-projection across all of z and across a 1-sigma range of 
  the fitted y-profile is performed to get a 1d itensity profile along the 
  x-axis. A sigmoid curve decreasing from left to righ is then fit to this 
  profile and its inflection point is used as the new x coordinate. This 
  captures the fact that labeled cells will leave the node toward the anterior
  (left, by convention), so the intensity profile will tend to be high at the 
  left boundary but low at the right (caudal/posterior) boundary.

