
import cv2 as cv
'''
        This method find the countour of the mask (that is a binary image)

        There are three arguments in cv.findContours() function, first one is source image,
        second is contour retrieval mode, third is contour approximation method. And it outputs a modified image,
        the contours and hierarchy. contours is a Python list of all the contours in the image. Each individual contour
        is a Numpy array of (x,y) coordinates of boundary points of the object.
    '''
def find_exterior_contours( mask):
    ## lets filter the mask to eliminate some noise
    #mask = cv.morphologyEx(mask, cv.MORPH_OPEN,cv.getStructuringElement(cv.MORPH_ELLIPSE, (5, 5)))
    # print(mask)
    contours = cv.findContours(mask, cv.RETR_EXTERNAL, cv.CHAIN_APPROX_SIMPLE)
    contour = None
    if len(contours) == 2:
        contour = contours[0]
    elif len(contours) == 3:
        contour = contours[1]
    else:
        raise Exception("Check the signature for `cv.findContours()`.")
    contour = max(contour, key=cv.contourArea) if len(contour) > 0 else None

    # epsilon = 0.0001 * cv.arcLength(big_contour, True)
    # approx = cv.approxPolyDP(big_contour, epsilon, True)


    return contour


def drawMaskOnImage(image, mask):


    """Updates an image in the already drawn window."""
    viz = image.copy()
    contours = find_exterior_contours(mask)  ##find countours of the binary image mask


    ## Generate random color for the mask
    from random import randrange
    maskColor = (randrange(255), randrange(255), randrange(255))

    '''
        Overlap the mask to the image
    '''
    viz = cv.drawContours(viz, [contours], -1, color=maskColor, thickness=-2)
    viz = cv.addWeighted(image, 0.60, viz, 0.40, 0)
    viz = cv.drawContours(viz, [contours], -2, color=maskColor, thickness=1)

    return viz, contours, mask


