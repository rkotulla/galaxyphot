#!/usr/bin/env python

import os
import sys
import pyfits
import numpy
import matplotlib
import matplotlib.path
import scipy
import scipy.ndimage

import polygon

if __name__ == "__main__":

    img_fn = sys.argv[1]
    img_hdu = pyfits.open(img_fn)

    polygon_reg = sys.argv[2]

    sex_config = sys.argv[3]

    filebase = os.path.splitext(img_fn)[0]

    sci_fn, wht_fn = filebase+".SCI.fits", filebase+".WHT.fits"
    segmentation_fn = filebase=".segmentation.fits"
    pyfits.PrimaryHDU(
        data=img_hdu['SCI'].data,
        header=img_hdu['SCI'].header).writeto(sci_fn, clobber=True)
    pyfits.PrimaryHDU(
        data=img_hdu['WHT'].data,
        header=img_hdu['WHT'].header).writeto(wht_fn, clobber=True)

    sextractor_cmd = """
    sex -c %s
    -CHECKIMAGE_TYPE SEGMENTATION
    -CHECKIMAGE_NAME %s
    -WEIGHT_TYPE MAP_WEIGHT
    -WEIGHT_IMAGE %s
    -FILTER N
    -VERBOSE_TYPE QUIET
    %s""" % (sex_config, segmentation_fn, wht_fn, sci_fn)
    sex_cmd = " ".join(sextractor_cmd.split())
    print sex_cmd
    os.system(sex_cmd)

    mask_2d = polygon.create_mask(img_fn, polygon_reg, 'SCI')

    seg_hdu = pyfits.open(segmentation_fn)
    not_detected = seg_hdu[0].data <= 0

    background = ~mask_2d & not_detected

    background_mask = (~background).astype(numpy.float)
    bg_grown = scipy.ndimage.filters.gaussian_filter(
        input=background_mask,
        sigma=5,
        order=0,
        mode='reflect',
    )

    # pyfits.PrimaryHDU(data=background_mask).writeto("bgmask.fits", clobber=True)
    # pyfits.PrimaryHDU(data=bg_grown).writeto("bggrown.fits", clobber=True)

    noise_img = img_hdu['SCI'].data.copy()
    # noise_img[~background] = numpy.NaN
    noise_img[bg_grown > 1e-5] = numpy.NaN

    # pyfits.PrimaryHDU(data=noise_img).writeto("noise.fits", clobber=True)


    bg_level = numpy.nanmedian(noise_img)
    bg_level2 = numpy.nanmean(noise_img)
    bg_std = numpy.nanstd(noise_img)

    noise_img -= bg_level

    print "sky-level mean/median:", bg_level2, bg_level
    print "sky noise:", bg_std
    print "sky dist -1sigma/+1sigma: ", numpy.nanpercentile(noise_img, [16,84])

