# Tim Nguyen
# show_matrices.py
# 01/28/18

def draw_and_export(csv_filepath):
    from os.path import join
    import matplotlib.pyplot as plt
    import numpy as np
    from mpl_toolkits.axes_grid1 import make_axes_locatable

    raw_scores_path = join(csv_filepath, 'scores.csv')
    clustered_scores_path = join(csv_filepath, 'markov_scores.csv')
    output_path = join(csv_filepath, 'raw_vs_clustered.png')

    # Read the .csv score matrices; generate numpy arrays from .csv scores
    raw_score_array = np.genfromtxt(raw_scores_path, delimiter = ',')
    clustered_score_array = np.genfromtxt(clustered_scores_path, delimiter = ',')

    # Using pyplot to plot the score arrays
    plt.subplot(121)
    raw_plot = plt.imshow(raw_score_array, interpolation = 'nearest')
    plt.axis('off')
    plt.title('pre-clustering')
    # Generate the color bar (do it manually since the colorbar that comes
    # with pyplot gives weird scale compare to actual matrices
    ax = plt.gca()
    # create an axes on the right side of ax. The width of color_bar will be 5%
    # of ax and the padding between color_bar and ax will be fixed at 0.05 inch
    divider = make_axes_locatable(ax)
    color_bar = divider.append_axes("right", size = "5%", pad = 0.05)
    plt.colorbar(raw_plot, cax = color_bar)
    plt.subplot(122)
    clustered_plot = plt.imshow(clustered_score_array, interpolation = 'nearest')
    plt.axis('off')
    plt.title('post-clustering')
    ax = plt.gca()
    divider = make_axes_locatable(ax)
    color_bar = divider.append_axes("right", size = "5%", pad = 0.05)
    plt.colorbar(clustered_plot, cax = color_bar)

    # Save the plot to file and display it
    plt.show()
    plt.savefig(output_path, dpi = 480, bbox_inches = 'tight')
