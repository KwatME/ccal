from numpy import absolute, apply_along_axis, argmax, linspace, meshgrid, rot90
from pandas import DataFrame

from .compute_joint_probability import compute_joint_probability
from .compute_posterior_probability import compute_posterior_probability
from .plot_and_save import plot_and_save
from .plot_heat_map import plot_heat_map


def _get_target_grid_indices(nd_array, function):

    return tuple(
        meshgrid_.astype(int).ravel()
        for meshgrid_ in meshgrid(
            *(
                linspace(0, nd_array.shape[i] - 1, nd_array.shape[i])
                for i in range(nd_array.ndim - 1)
            ),
            indexing="ij",
        )
    ) + (apply_along_axis(function, nd_array.ndim - 1, nd_array).ravel(),)


def infer(variables, n_grid=64, target="max", plot=True, names=None):

    n_dimension = len(variables)

    p_vs = compute_joint_probability(variables, n_grid=n_grid, plot=plot, names=names)

    p_tv__ntvs = compute_posterior_probability(p_vs, plot=plot, names=names)

    if target is "max":

        t_grid_coordinates = _get_target_grid_indices(p_tv__ntvs, argmax)

    else:

        t_grid = linspace(variables[-1].min(), variables[-1].max(), n_grid)

        t_i = absolute(t_grid - target).argmin()

        t_grid_coordinates = _get_target_grid_indices(p_tv__ntvs, lambda _: t_i)

    p_tvt__ntvs = p_tv__ntvs[t_grid_coordinates].reshape((n_grid,) * (n_dimension - 1))

    if plot:

        if names is None:

            names = tuple("Variable {}".format(i) for i in range(n_dimension))

        if n_dimension == 2:

            plot_and_save(
                {
                    "layout": {
                        "title": {
                            "text": "P({} = {} | {})".format(
                                names[-1], target, names[0]
                            )
                        },
                        "xaxis": {"title": names[0]},
                        "yaxis": {"title": "Probability"},
                    },
                    "data": [
                        {
                            "type": "scatter",
                            "x": tuple(range(n_grid)),
                            "y": p_tvt__ntvs,
                            "marker": {"color": "#20d9ba"},
                        }
                    ],
                },
                None,
            )

        elif n_dimension == 3:

            plot_heat_map(
                DataFrame(rot90(p_tvt__ntvs)),
                title="P({} = {} | {}, {})".format(
                    names[-1], target, names[0], names[1]
                ),
                xaxis_title=names[0],
                yaxis_title=names[1],
            )

    return p_tv__ntvs, p_tvt__ntvs
