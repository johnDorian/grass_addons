# Various GRASS GIS Addons
This repository contains several modules for [GRASS GIS](http://grass.osgeo.org). They are mainly designed to be used in conjunction with the [r.stream](http://grasswiki.osgeo.org/wiki/R.stream.*_modules) to create stream spatial networks to be used with the R [SSN](http://cran.r-project.org/web/packages/SSN/index.html) package.

## Vector Modules 
There are currently two modules:
    1. v.sites.cont
    2. _v.edges.cont_ (To be added shortly)
    3. v.streams.netid

### v.sites.cont
This module determines the contributing area for each site in the vector. In addition the module also allows for the estimation of the contributing area statistics of raster maps of two types. Continuous variable and categorical type maps. 