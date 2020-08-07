
"""
Olivia immunization functions.

Immunization analyzes in which packages it is better to invest to protect the network as a whole.
"""

import random

from olivia.lib.graphs import removed
from olivia.model import OliviaNetwork
from olivia.networkmetrics import failure_vulnerability
from olivia.packagemetrics import Reach, DependentsCount, Impact, Surface


def immunization_delta(net, n, cost_metric=Reach):
    """
    Compute the improvement in network Phi vulnerability by immunizing a certain set of packages.

    Parameters
    ----------
    net: OliviaNetwork
        Input network.
    n: container
        Container of packages to be immunized.
    cost_metric: class, optional
        Metric to measure cost.

    Returns
    -------
    result: float, float, float
        Initial vulnerability, vulnerability after immunization, difference.

    Notes
    -----
    Implements the naive algorithm of removing immunized nodes and rebuilding model from scratch, so it is
    really slow for big networks. Some obvious improvements could be made, but whether or not there is a
    much better alternative is an open question.

    """
    f1 = failure_vulnerability(net, metric=cost_metric)
    with removed(net.network, n):
        immunized_net = OliviaNetwork()
        immunized_net.build_model(net.network)
        f2 = failure_vulnerability(immunized_net, metric=cost_metric)
    return f1, f2, f1 - f2


def iset_naive_ranking(olivia_model, set_size, metric=Reach):
    """
    Compute an immunization set by selecting top elements according to a metric.

    Parameters
    ----------
    olivia_model: OliviaNetwork
        Input network
    set_size: int
        Number of packages in the immunization set.
    metric: class, optional
        Metric to measure cost.

    Returns
    -------
    immunization_set: set
        Set of packages to be immunized.

    """
    return {p[0] for p in olivia_model.get_metric(metric).top(set_size)}


def iset_delta_frame_reach(olivia_model):
    """
    Compute an immunization set using the DELTA FRAME algorithm with the Reach metric.

    DELTA FRAME computes upper and lower bounds for the vulnerability reduction associated to the immunization of
    each package in the network and returns a set that is guaranteed to contain the single optimum package for
    immunization.

    The resulting set size is a product of the algorithm and cannot be selected.

    Parameters
    ----------
    olivia_model: OliviaNetwork
        Input network

    Returns
    -------
    immunization_set: set
        Set of packages to be immunized.

    """
    delta_upper = olivia_model.get_metric(Reach) * olivia_model.get_metric(Surface)
    delta_lower = olivia_model.get_metric(Reach) + olivia_model.get_metric(Surface) - 1
    max_lower = delta_lower.top()[0][1]
    return {p for p in olivia_model if delta_upper[p] > max_lower}


def iset_delta_frame_impact(olivia_model):
    """
    Compute an immunization set using the DELTA FRAME algorithm with the Impact metric.

    DELTA FRAME computes upper and lower bounds for the vulnerability reduction associated to the immunization of
    each package in the network and returns a set that is guaranteed to contain the single optimum package for
    immunization.

    The resulting set size is a product of the algorithm and cannot be selected.

    Parameters
    ----------
    olivia_model: OliviaNetwork
        Input network

    Returns
    -------
    immunization_set: set
        Set of packages to be immunized.

    """
    delta_upper = olivia_model.get_metric(Impact) * olivia_model.get_metric(Surface)
    delta_lower = olivia_model.get_metric(DependentsCount) * olivia_model.get_metric(Surface)
    max_lower = delta_lower.top()[0][1]
    return {p for p in olivia_model if delta_upper[p] > max_lower}


def iset_random(olivia_model, set_size, indirect=False, seed=None):
    """
    Compute an immunization set by randomly selecting packages.

    This method is useful for understanding the nature of a network's vulnerability and/or for
    establishing baseline immunization cases.

    Parameters
    ----------
    olivia_model: OliviaNetwork
        Input network
    set_size: int
        Number of packages in the immunization set.
    indirect: bool, optional
        Whether to use indirect selection or not. Using indirect selection the immunization set is constructed
        by randomly choosing a dependency of a randomly selected package.
    seed: int, optional
        Seed for the random number generator.

    Returns
    -------
    immunization_set: set
        Set of packages to be immunized.

    """
    packages = tuple(olivia_model)
    if seed:
        random.seed(seed)
    if indirect:
        result = set()
        while len(result) != set_size:
            dependencies = []
            while len(dependencies) == 0:
                current = random.choice(packages)
                dependencies = olivia_model[current].direct_dependencies()
            result.add(random.choice(tuple(dependencies)))
        return result
    else:
        return set(random.sample(packages, k=set_size))