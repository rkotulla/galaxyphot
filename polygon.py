#!/usr/bin/env python

import os
import sys
import pyfits
import numpy
import matplotlib
import matplotlib.path

# hi lauren

if __name__ == "__main__":

    img_fn = sys.argv[1]

    reg_fn = sys.argv[2]

    extname = sys.argv[3]

    #
    # read image file
    #
    hdulist = pyfits.open(img_fn)
    data = hdulist[extname].data.T.copy()
    print data.shape

    #
    # read region file
    #
    with open(reg_fn, "r") as reg:
        lines = reg.readlines()
        for line in lines:
            if (not line.startswith("polygon")):
                continue
            print line

            coords = [float(f)-1. for f in line.split("(")[1].split(")")[0].split(",")]
            print coords
            coords = numpy.array(coords).reshape((-1,2))
            print coords

            _min = numpy.min(coords, axis=0)
            _max = numpy.max(coords, axis=0)
            print _min, _max

            p = matplotlib.path.Path(coords) #[(0,0), (0, 1), (1, 1), (1, 0)])
            print p

            iy,ix = numpy.indices(data.shape)
            print ix
            print iy
            i_xy = numpy.append(ix.reshape((-1,1)), iy.reshape((-1,1)), axis=1)
            print i_xy

            mask = p.contains_points(i_xy)
            print mask

            mask_2d = mask.reshape(data.shape)

            primhdu = pyfits.PrimaryHDU(data=mask_2d.astype(numpy.int))
            primhdu.writeto("mask.fits", clobber=True)
            #hdulist[0].data = mask_2d.astype(numpy.int)
            #hdulist.writeto("mask.fits", clobber=True)


            inside_mask = data[mask_2d]
            n_pixels = numpy.sum(mask_2d)
            print n_pixels

            flux = numpy.sum(inside_mask)
            print flux
