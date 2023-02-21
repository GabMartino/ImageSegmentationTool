

import cv2
import numpy as np
from matplotlib import pyplot as plt

def show3DScatter(image):
    from mpl_toolkits.mplot3d import Axes3D
    from matplotlib import cm
    from matplotlib import colors
    r, g, b = cv2.split(image)
    fig = plt.figure()
    axis = fig.add_subplot(1, 1, 1, projection="3d")
    pixel_colors = image.reshape((np.shape(image)[0] * np.shape(image)[1], 3))
    norm = colors.Normalize(vmin=-1., vmax=1.)
    norm.autoscale(pixel_colors)
    pixel_colors = norm(pixel_colors).tolist()

    axis.scatter(r.flatten(), g.flatten(), b.flatten(), facecolors=pixel_colors, marker=".")
    axis.set_xlabel("Red")
    axis.set_ylabel("Green")
    axis.set_zlabel("Blue")
    plt.show()


def main():

    image = cv2.imread("./test_image.jpg")
    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)


    plt.imshow(image)
    plt.show()

    seed = (500, 500)

    cv2.floodFill(image, None, seedPoint=seed, newVal=(0, 0, 255), loDiff=(5, 5, 5, 5), upDiff=(5, 5, 5, 5))
    cv2.circle(image, seed, 2, (0, 255, 0), cv2.FILLED, cv2.LINE_AA)

    cv2.imshow('flood', image)
    cv2.waitKey(0)
    cv2.destroyAllWindows()
    #show3DScatter(image)


if __name__ == "__main__":
    main()