import numpy as np


def conv2d(image, kernel):
    """
    2D convolution with zero padding. The output has the same size as the image.
    Inputs:
        image: (H, W)
        kernel: (2n + 1, 2m + 1)
    Output:
        (H, W) array, out[r, c] = sum_{i=-n..n} sum_{j=-m..m} F(i, j) * image[r - i, c - j],
        where F(i, j) = kernel[i + n, j + m] and pixels outside the image are 0

    HINT: looping over the kernel entries and adding shifted copies of the padded image
          is much faster than looping over the pixels.
    """
    image = np.asarray(image, dtype=float)
    kernel = np.asarray(kernel, dtype=float)
    H, W = image.shape
    n, m = kernel.shape[0] // 2, kernel.shape[1] // 2
    ########## Code starts here ##########

    out = np.zeros_like(image)

    # print(np.array(image.shape) - np.array(kernel.shape))
    # print(np.array(kernel.shape))
    padded = np.pad(image, ((n, n), (m, m)))  # zeros by default

    for i in range(-n,n+1):
        for j in range(-m,m+1):
            out += kernel[n+i,m+j] * padded[n-i:n-i+H, m-j:m-j+W]

    ########## Code ends here ##########
    return out


def gaussian_kernel(size, sigma):
    """
    Normalized Gaussian mask: samples exp(-(x^2 + y^2) / (2 sigma^2)) at the integer offsets
    x, y = -(size // 2), ..., size // 2 about the center, scaled so the entries sum to 1.
    Output:
        (size, size) array
    """
    ########## Code starts here ##########
    offsets = np.arange(-(size//2), (size+1)//2)

    xx, yy = np.meshgrid(offsets, offsets)
    G = np.exp(-(xx**2 + yy**2) / (2*sigma**2))
    G = G / np.sum(G)
    ########## Code ends here ##########
    return G


def sobel_gradients(image):
    """
    Image gradients with the Sobel masks from lecture,
        S_x = [[1, 0, -1], [2, 0, -2], [1, 0, -1]],  S_y = [[1, 2, 1], [0, 0, 0], [-1, -2, -1]]
    Output:
        Gx, Gy: (H, W) arrays, Gx = conv2d(image, S_x) and Gy = conv2d(image, S_y)
    """
    ########## Code starts here ##########
    S_x = np.array([[1, 0, -1], [2, 0, -2], [1, 0, -1]])
    S_y = np.array([[1, 2, 1], [0, 0, 0], [-1, -2, -1]])
    
    Gx = conv2d(image, S_x)
    Gy = conv2d(image, S_y)
    ########## Code ends here ##########
    return Gx, Gy


def patch_vectors(image, points, half_size=7):
    """
    Unit-length patch vector for each point, for normalized correlation.
    The vector for point (r, c) is image[r - h : r + h + 1, c - h : c + h + 1] flattened
    (row-major) and divided by its norm (use max(norm, 1e-8)).
    Points are at least half_size pixels from the image edges.
    Inputs:
        points: (K, 2) integer array of (row, col)
    Output:
        (K, (2h + 1)^2)
    """
    image = np.asarray(image, dtype=float)
    h = half_size
    ########## Code starts here ##########

    def vec(v):
        r,c, = v
        val = image[r - h : r + h + 1, c - h : c + h + 1].flatten()
        return val / max(np.linalg.norm(val), 1e-8)


    P = np.apply_along_axis(vec, 1, points)
    ########## Code ends here ##########
    return P


def match_patches(vecs1, vecs2):
    """
    Match each patch of image 1 to the patch of image 2 with the highest normalized correlation.
    Inputs:
        vecs1: (K1, D), vecs2: (K2, D), unit-length patch vectors
    Output:
        matches: (K1,) integer array, matches[i] = index j in vecs2 that maximizes vecs1[i] . vecs2[j]
                 (if several j tie, the smallest one)
        scores: (K1,) the normalized correlation of each match
    """
    ########## Code starts here ##########

    matches = []
    scores = []
    for v1 in vecs1:
        dots = np.array([np.dot(v1, v2) for v2 in vecs2])
        
        matches.append(np.argmax(dots))
        scores.append(np.max(dots)) # already unit vectors

    matches = np.asarray(matches, dtype=int)
    scores = np.asarray(scores)
    ########## Code ends here ##########
    return matches, scores
