"""
cad_ogm.py
-------------------
Reusable module for converting CAD images (PNG) to 2D binary occupancy grid numpy arrays (OGM).

Usage:
    from cad_ogm import cad_to_ogm
    ogm = cad_to_ogm('path/to/image.png', grid_size=(200,200))

Main function:
    cad_to_ogm(input_path, ...):
        Input: path to PNG image
        Output: 2D binary numpy array (OGM)

All processing steps are encapsulated for reuse in other projects.
"""

import cv2
import numpy as np
import matplotlib.pyplot as plt
import os


def load_image_gray(path):
    """Loads a grayscale image from the specified path."""
    img = cv2.imread(path, cv2.IMREAD_GRAYSCALE)
    if img is None:
        raise FileNotFoundError(f"Input image not found: {path}")
    return img


def preprocess_classical(img, invert=True, thresh_val=200):
    """Preprocesses the grayscale image to extract a binary wall mask using classical image processing."""
    if invert:
        _, binary = cv2.threshold(img, thresh_val, 255, cv2.THRESH_BINARY_INV)
    else:
        _, binary = cv2.threshold(img, thresh_val, 255, cv2.THRESH_BINARY)
    kernel = np.ones((3, 3), np.uint8)
    cleaned = cv2.morphologyEx(binary, cv2.MORPH_OPEN, kernel, iterations=1)
    kernel2 = np.ones((5, 5), np.uint8)
    closed = cv2.morphologyEx(cleaned, cv2.MORPH_CLOSE, kernel2, iterations=2)
    dilated = cv2.dilate(closed, kernel2, iterations=2)
    return (dilated > 0).astype(np.uint8)


def normalize_wall_thickness(wall_mask, target_thickness=3):
    """Normalizes the wall thickness in the binary mask to a target thickness."""
    dist = cv2.distanceTransform(255 - wall_mask * 255, cv2.DIST_L2, 5)
    centerline = (dist > 1).astype(np.uint8)
    kernel = cv2.getStructuringElement(
        cv2.MORPH_ELLIPSE, (target_thickness, target_thickness)
    )
    normalized = cv2.dilate(centerline, kernel, iterations=1)
    return (normalized > 0).astype(np.uint8)


def fill_closed_regions(grid):
    """Fills closed free space regions in the grid with walls."""
    h, w = grid.shape
    mask = np.zeros((h + 2, w + 2), np.uint8)
    grid_filled = grid.copy()
    cv2.floodFill(grid_filled, mask, (0, 0), 2)
    closed_mask = grid_filled == 0
    result = grid.copy()
    result[closed_mask] = 1
    return result


def detect_doors(wall_mask, min_gap_area=20):
    """Detects doors by identifying small gaps in walls and fills them."""
    free_space = (wall_mask == 0).astype(np.uint8)
    contours, _ = cv2.findContours(
        free_space, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
    )
    door_mask = np.zeros_like(wall_mask)
    for cnt in contours:
        if cv2.contourArea(cnt) < min_gap_area:
            cv2.drawContours(wall_mask, [cnt], -1, color=0, thickness=-1)
            cv2.drawContours(door_mask, [cnt], -1, color=1, thickness=-1)
    return (door_mask > 0).astype(np.uint8), wall_mask


def raster_to_grid(occ_mask, grid_size=(200, 200)):
    """Resizes the occupancy mask to the specified grid size."""
    resized = cv2.resize(
        occ_mask.astype(np.uint8), grid_size, interpolation=cv2.INTER_NEAREST
    )
    return (resized > 0).astype(np.uint8)


def cad_to_ogm(
    input_path,
    grid_size=(200, 200),
    normalize=True,
    detect_doors_flag=True,
    fill_closed_regions_flag=False,
) -> np.ndarray:
    """
    Converts a CAD PNG image to a 2D binary occupancy grid numpy array (OGM).

    Parameters
    ----------
    input_path : str
        Path to the input PNG image.
    grid_size : tuple of int, optional
        Output grid size (height, width). Default (200, 200).
    normalize : bool, optional
        Normalize wall thickness. Default True.
    detect_doors_flag : bool, optional
        Detect and fill doors. Default True.
    fill_closed_regions_flag : bool, optional
        Fill closed free spaces. Default False.

    Returns
    -------
    numpy.ndarray
        2D binary occupancy grid (OGM)
    dict (optional)
        If return_intermediate=True, also returns a dict of intermediate results.
    """
    img_gray = load_image_gray(input_path)
    wall_mask = preprocess_classical(img_gray)
    if normalize:
        wall_mask = normalize_wall_thickness(wall_mask)
    door_mask = np.zeros_like(wall_mask)
    if detect_doors_flag:
        door_mask, wall_mask = detect_doors(wall_mask)
    ogm_grid = raster_to_grid(wall_mask, grid_size)
    if fill_closed_regions_flag:
        ogm_grid = fill_closed_regions(ogm_grid)
    
    return ogm_grid
