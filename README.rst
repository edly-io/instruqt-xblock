[![Python CI](https://github.com/edly-io/instruqt-xblock/actions/workflows/ci.yml/badge.svg)](https://github.com/edly-io/instruqt-xblock/actions/workflows/ci.yml)


XBlock to embed Instruqt track in Open edX
##########################################

About Instruqt
**************

Instruqt is a hands-on virtual IT Lab Platform for interactive learning. Virtual IT labs provide learners with hands-on sandbox environments.
Learners can use the platform to learn about products and technology.

About Instruqt XBlock
*********************

Instruqt XBlock allows Open edX users to embed Instruqt tracks inside an Open edX course. It provides ability to track
learner progress and reflects track completion in Open edX. Using this block instructor can compute score of a track using this
formula::


    $ SCORE = NUMBER OF COMPLETED CHALLENGES / TOTAL CHALLENGES IN TRACK


How to use Instruqt XBlock
**************************

Instruqt XBlock can be installed using pip::


    $ pip install instruqt-xblock

Once installed add ``instruqtxblock`` in advanced module list of course advanced settings. It should availabe in Advanced component list of course unit afterwards.
