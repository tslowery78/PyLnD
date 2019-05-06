import matplotlib.pyplot as plt


def matrix_plot(**kwargs):
    """Function to plot an series.
            Minimal Ex:
                matrix_plot(y=y_array)
            Full Ex:
                matrix_plot(y=y_array, x=x_array, xlabel='time', ylabel='moment', y2=y2_array,
                    y2label='temperature', ylegend=[list of y series names], y2legend=[list of y2 series names])
                        title='load and temperature xvv')
                save file an ddo not plot:
                matrix_plot(y=y_array, x=x_array, xlabel='time', ylabel='moment', y2=y2_array,
                    y2label='temperature', ylegend=[list of y series names], y2legend=[list of y2 series names])
                        title='load and temperature xvv', save='myplot.png')

    """

    # Get the kwargs
    if 'y' in kwargs.keys():
        y = kwargs['y']
        # Make any 1-d arrays a 2d
        if y.ndim == 1:
            y.shape = (-1, 1)
    else:
        raise Exception('You must provide at least a y-array')
    x = None
    if 'x' in kwargs.keys():
        x = kwargs['x']
    y2 = None
    if 'y2' in kwargs.keys():
        y2 = kwargs['y2']
    xlabel = None
    if 'xlabel' in kwargs.keys():
        xlabel = kwargs['xlabel']
    ylabel = None
    if 'ylabel' in kwargs.keys():
        ylabel = kwargs['ylabel']
    y2label = None
    if 'y2label' in kwargs.keys():
        y2label = kwargs['y2label']
    ylegend = None
    if 'ylegend' in kwargs.keys():
        ylegend = kwargs['ylegend']
        if type(ylegend) is not list:
            ylegend = [ylegend]
    y2legend = None
    if 'y2legend' in kwargs.keys():
        y2legend = kwargs['y2legend']
        if type(y2legend) is not list:
            y2legend = [y2legend]
    title = None
    if 'title' in kwargs.keys():
        title = kwargs['title']
    savefile = None
    if 'save' in kwargs.keys():
        savefile = kwargs['save']

    # Plot the y data
    fig, ax1 = plt.subplots()
    fig.patch.set_facecolor('white')
    [num_rows, num_cols] = y.shape
    if x is None:
        x = range(0, num_rows)
    for c in range(0, num_cols):
        if ylegend:
            ax1.plot(x, y[:, c], label=ylegend[c])
            plt.legend()
        else:
            ax1.plot(x, y[:, c])
    ax2 = None
    # Plot the y2 data
    if y2 is not None:
        ax2 = ax1.twinx()
        [_, num_cols] = y2.shape
        for c in range(0, num_cols):
            if y2legend:
                ax2.plot(x, y2[0:num_rows, c], label=y2legend[c], linestyle='--')
                plt.legend(loc='lower right')
            else:
                ax2.plot(x, y2[:, c])
    if xlabel is not None:
        ax1.set_xlabel(xlabel)
    if ylabel is not None:
        ax1.set_ylabel(ylabel)
    if y2label is not None:
        ax2.set_ylabel(y2label)
    if title is not None:
        plt.title(title)
    if savefile is not None:
        plt.savefig(savefile)
    else:
        plt.grid()
        plt.show()


if __name__ == '__main__':
    import numpy as np
    time = np.linspace(0, 10, 100)
    rand = np.random.rand(100, 3)
    rand2 = np.random.rand(100, 1)
    # matrix_plot(y=rand, y2=rand2, xlabel='time', ylabel='moment', y2label='temperature', ylegend=['a', 'b', 'c'],
    #             y2legend=['d'], x=time)
    matrix_plot(y=rand, ylabel='moment', ylegend=['a', 'b', 'c'])
    # matrix_plot(y=rand, ylabel='moment', x=time, xlabel='time', y2=rand2, y2label='temp', y2legend=['mytemp'],
    #             title='load and temperature xvv', save='myplot.png')
