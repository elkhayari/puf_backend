import io
from matplotlib import colors
from mpl_toolkits.axes_grid1 import make_axes_locatable
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')


class PUFPlots:
    def __init__(self):
        pass

    @staticmethod
    def create_heatmap_array(matrix, title=None, label=None, bar_description=['zero', 'one']):
        fig, ax = plt.subplots(figsize=(10, 6))
        # Using imshow from matplotlib to create the heatmap

        cmap = colors.ListedColormap(['white', 'black'])
        # norm = colors.BoundaryNorm(bounds, cmap.N)
        img = ax.imshow(matrix, cmap=cmap, aspect='auto')
        # plt.colorbar(label='Value')

        # Create an axes divider to place the colorbar neatly
        divider = make_axes_locatable(ax)
        cax = divider.append_axes('right', size='5%', pad=0.05)
        bounds = [0, 0.5, 1]
        cbar = plt.colorbar(img, boundaries=bounds, ticks=bounds,
                            cax=cax, orientation='vertical')
        if bar_description:
            cbar.ax.set_yticklabels(
                [bar_description[0], '', bar_description[1]])
        if title:
            ax.set_title(title)
        if label:
            # Get the number of rows and columns from the matrix
            num_rows = len(matrix)
            num_cols = len(matrix[0]) if num_rows > 0 else 0

            # Place the label at the bottom center of the heatmap
            ax.text(num_cols/2, num_rows + 0.5, label,
                    horizontalalignment='center', verticalalignment='center')

        buf = io.BytesIO()

        plt.savefig(buf, format='png')
        buf_value = buf.getvalue()
        # print(buf_value)
        buf.seek(0)
        plt.close()

        # returns binary data
        return buf_value
