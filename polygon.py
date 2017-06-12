#!/usr/bin/env python

import os
import sys
import pyfits
import numpy
import matplotlib
import matplotlib.path

from astLib import astWCS

# hi lauren

def create_mask(img_fn, reg_fn, extname):

    #
    # read image file
    #
    hdulist = pyfits.open(img_fn)
    data = hdulist[extname].data.copy()
    print data.shape

    # _ix,_iy = numpy.indices(data.shape, dtype=numpy.float)
    # data[:,:] = _ix #numpy.random.random(data.shape) - 0.5
    # hdulist[extname].data = data
    # hdulist.writeto("one.fits", clobber=True)

    #
    # read region file
    #
    full_mask = numpy.zeros(data.shape, dtype=numpy.bool)

    with open(reg_fn, "r") as reg:
        lines = reg.readlines()

        for line in lines:
            if (not line.startswith("polygon")):
                continue
            print line

            if (lines[2].strip() == "fk5"):
                print "#\n"*5,"# USING FK5 coords","\n#"*5


                skycoords = [float(f) for f in
                          line.split("(")[1].split(")")[0].split(",")]
                # print coords
                skycoords = numpy.array(skycoords).reshape((-1, 2))
                print skycoords

                wcs = astWCS.WCS(hdulist[extname].header, mode='pyfits')
                xy = wcs.wcs2pix(skycoords[:,0], skycoords[:,1])
                coords = numpy.array(xy)
                print coords


            else:
                coords = [float(f) - 1.5 for f in
                          line.split("(")[1].split(")")[0].split(",")]
                # print coords
                coords = numpy.array(coords).reshape((-1, 2))
                print coords



            _min = numpy.min(coords, axis=0)
            _max = numpy.max(coords, axis=0)
            print "min/max:", _min, _max

            p = matplotlib.path.Path(coords)  # [(0,0), (0, 1), (1, 1), (1, 0)])
            # print p

            iy, ix = numpy.indices(data.shape)
            # print ix
            # print iy
            i_xy = numpy.append(ix.reshape((-1, 1)), iy.reshape((-1, 1)), axis=1)
            # print i_xy

            mask = p.contains_points(i_xy)
            # print mask

            mask_2d = mask.reshape(data.shape)

            inside_mask = data[mask_2d]
            n_pixels = numpy.sum(mask_2d)
            print "area:", n_pixels

            # flux = numpy.sum(inside_mask[inside_mask>0])
            print "flux:", numpy.sum(inside_mask)
            print "mean:", numpy.median(inside_mask)
            print "median:", numpy.median(inside_mask)

            print "dx/dy", (_max[1] - _min[1]), (_max[0] - _min[0])
            print "box-size:", (_max[1] - _min[1]) * (_max[0] - _min[0])

            full_mask = full_mask | mask_2d

    primhdu = pyfits.PrimaryHDU(data=full_mask.astype(numpy.int))
    primhdu.writeto("mask.fits", clobber=True)
    # hdulist[0].data = mask_2d.astype(numpy.int)
    # hdulist.writeto("mask.fits", clobber=True)



    return full_mask

if __name__ == "__main__":

    img_fn = sys.argv[1]

    reg_fn = sys.argv[2]

    extname = sys.argv[3]


    create_mask(img_fn, reg_fn, extname)

