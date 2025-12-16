import numpy as np
from cad_ogm import cad_to_ogm
import matplotlib.pyplot as plt


if __name__ == "__main__":
    # image_path = "./AA/real-room/png/0a1a5807d65749c1194ce1840354be39.png"
    image_path = "cad_sample.png"  # Replace with your image path
    ogm = cad_to_ogm(
        image_path,
        grid_size=(500, 500),
        normalize=True,
        detect_doors_flag=True,
    )
    print(ogm)
    print("OGM unique values:", np.unique(ogm))
    plt.imshow(ogm, cmap="gray")
    plt.title("OGM Output")
    plt.show()
