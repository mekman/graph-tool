#! /usr/bin/env python
# -*- coding: utf-8 -*-
#
# graph_tool -- a general graph manipulation python module
#
# Copyright (C) 2006-2013 Tiago de Paula Peixoto <tiago@skewed.de>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

"""
``graph_tool.spectral`` - Spectral properties
---------------------------------------------

Summary
+++++++

.. autosummary::
   :nosignatures:

   adjacency
   laplacian
   incidence

Contents
++++++++
"""

from __future__ import division, absolute_import, print_function

from .. import _degree, _prop, Graph, _limit_args
from numpy import *
import scipy.sparse


__all__ = ["adjacency", "laplacian", "incidence"]


def adjacency(g, sparse=True, weight=None):
    r"""Return the adjacency matrix of the graph.

    Parameters
    ----------
    g : Graph
        Graph to be used.
    sparse : bool (optional, default: True)
        Build a :mod:`~scipy.sparse` matrix.
    weight : PropertyMap (optional, default: True)
        Edge property map with the edge weights.

    Returns
    -------
    a : matrix
        The adjacency matrix.

    Notes
    -----
    The adjacency matrix is defined as

    .. math::

        a_{i,j} =
        \begin{cases}
            1 & \text{if } v_i \text{ is adjacent to } v_j, \\
            0 & \text{otherwise}
        \end{cases}

    In the case of weighted edges, the value 1 is replaced the weight of the
    respective edge.

    In the case of networks with parallel edges, the entries in the matrix
    become simply the edge multiplicities.

    Examples
    --------
    .. testsetup::

      gt.seed_rng(42)

    >>> g = gt.random_graph(100, lambda: (10, 10))
    >>> m = gt.adjacency(g)
    >>> print(m.todense())
    [[ 0.  0.  0. ...,  0.  1.  0.]
     [ 0.  0.  0. ...,  0.  0.  0.]
     [ 0.  0.  0. ...,  0.  0.  1.]
     ..., 
     [ 0.  0.  0. ...,  0.  0.  0.]
     [ 0.  0.  0. ...,  0.  0.  0.]
     [ 0.  0.  1. ...,  0.  0.  0.]]

    References
    ----------
    .. [wikipedia-adjacency] http://en.wikipedia.org/wiki/Adjacency_matrix
    """

    if g.get_vertex_filter()[0] != None:
        index = g.new_vertex_property("int64_t")
        for i, v in enumerate(g.vertices()):
            index[v] = i
    else:
        index = g.vertex_index
    N = g.num_vertices()
    if sparse:
        m = scipy.sparse.lil_matrix((N, N))
    else:
        m = matrix(zeros((N, N)))
    for v in g.vertices():
        for e in v.out_edges():
            m[index[v], index[e.target()]] += 1 if weight is None else weight[e]
    if sparse:
        m = m.tocsr()
    return m


def _get_deg(v, deg, weight):
    if deg == "total":
        if weight == None:
            d = v.in_degree() + v.out_degree()
        else:
            d = sum(weight[e] for e in v.all_edges())
    elif deg == "in":
        if weight == None:
            d = v.in_degree()
        else:
            d = sum(weight[e] for e in v.in_edges())
    else:
        if weight == None:
            d = v.out_degree()
        else:
            d = sum(weight[e] for e in v.out_edges())
    return d


@_limit_args({"deg": ["total", "in", "out"]})
def laplacian(g, deg="total", normalized=True, sparse=True, weight=None):
    r"""Return the Laplacian matrix of the graph.

    Parameters
    ----------
    g : Graph
        Graph to be used.
    deg : str (optional, default: "total")
        Degree to be used, in case of a directed graph.
    normalized : bool (optional, default: True)
        Whether to compute the normalized Laplacian.
    sparse : bool (optional, default: True)
        Build a :mod:`~scipy.sparse` matrix.
    weight : PropertyMap (optional, default: True)
        Edge property map with the edge weights.

    Returns
    -------
    l : matrix
        The Laplacian matrix.

    Notes
    -----
    The weighted Laplacian matrix is defined as

    .. math::

        \ell_{ij} =
        \begin{cases}
        \Gamma(v_i) & \text{if } i = j \\
        -w_{ij}     & \text{if } i \neq j \text{ and } v_i \text{ is adjacent to } v_j \\
        0           & \text{otherwise}.
        \end{cases}

    Where :math:`\Gamma(v_i)=\sum_j A_{ij}w_{ij}` is sum of the weights of
    vertex :math:`v_i`. The normalized version is

    .. math::

        \ell_{ij} =
        \begin{cases}
        1         & \text{ if } i = j \text{ and } \Gamma(v_i) \neq 0 \\
        -\frac{w_{ij}}{\sqrt{\Gamma(v_i)\Gamma(v_j)}} & \text{ if } i \neq j \text{ and } v_i \text{ is adjacent to } v_j \\
        0         & \text{otherwise}.
        \end{cases}

    In the case of unweighted edges, it is assumed :math:`w_{ij} = 1`.

    For directed graphs, it is assumed :math:`\Gamma(v_i)=\sum_j A_{ij}w_{ij} +
    \sum_j A_{ji}w_{ji}` if ``deg=="total"``, :math:`\Gamma(v_i)=\sum_j A_{ij}w_{ij}`
    if ``deg=="out"`` or :math:`\Gamma(v_i)=\sum_j A_{ji}w_{ji}` ``deg=="in"``.

    Examples
    --------
    .. testsetup::

      gt.seed_rng(42)

    >>> g = gt.random_graph(100, lambda: (10,10))
    >>> m = gt.laplacian(g)
    >>> print(m.todense())
    [[ 1.   -0.05  0.   ...,  0.    0.    0.  ]
     [ 0.    1.    0.   ...,  0.    0.   -0.05]
     [ 0.    0.    1.   ...,  0.   -0.05  0.  ]
     ..., 
     [ 0.    0.    0.   ...,  1.    0.    0.  ]
     [-0.05  0.    0.   ...,  0.    1.    0.  ]
     [ 0.    0.    0.   ..., -0.05  0.    1.  ]]

    References
    ----------
    .. [wikipedia-laplacian] http://en.wikipedia.org/wiki/Laplacian_matrix
    """

    if g.get_vertex_filter()[0] != None:
        index = g.new_vertex_property("int64_t")
        for i, v in enumerate(g.vertices()):
            index[v] = i
    else:
        index = g.vertex_index
    N = g.num_vertices()
    if sparse:
        m = scipy.sparse.lil_matrix((N, N))
    else:
        m = matrix(zeros((N, N)))
    for v in g.vertices():
        d = _get_deg(v, deg, weight)
        for e in v.out_edges():
            if not normalized:
                if weight is None:
                    val = -1
                else:
                    val = -weight[e]
                # increment in case of parallel edges
                m[index[v], index[e.target()]] += val
            else:
                d2 = _get_deg(e.target(), deg, weight)
                if weight is None:
                    w = 1
                else:
                    w = weight[e]
                # increment in case of parallel edges
                m[index[v], index[e.target()]] += - w / sqrt(d * d2)
        if not normalized:
            m[index[v], index[v]] = d
        elif d > 0:
            m[index[v], index[v]] = 1 if d != 0 else 0
    if sparse:
        m = m.tocsr()
    return m


def incidence(g, sparse=True):
    r"""Return the incidence matrix of the graph.

    Parameters
    ----------
    g : Graph
        Graph to be used.
    sparse : bool (optional, default: True)
        Build a :mod:`~scipy.sparse` matrix.

    Returns
    -------
    a : matrix
        The adjacency matrix.

    Notes
    -----
    For undirected graphs, the incidence matrix is defined as

    .. math::

        b_{i,j} =
        \begin{cases}
            1 & \text{if vertex } v_i \text{and edge } e_j \text{ are incident}, \\
            0 & \text{otherwise}
        \end{cases}

    For directed graphs, the definition is

    .. math::

        b_{i,j} =
        \begin{cases}
            1 & \text{if edge } e_j \text{ enters vertex } v_i, \\
            -1 & \text{if edge } e_j \text{ leaves vertex } v_i, \\
            0 & \text{otherwise}
        \end{cases}

    Examples
    --------
    .. testsetup::

      gt.seed_rng(42)

    >>> g = gt.random_graph(100, lambda: (2,2))
    >>> m = gt.incidence(g)
    >>> print(m.todense())
    [[-1. -1.  0. ...,  0.  0.  0.]
     [ 0.  0. -1. ...,  0.  0.  0.]
     [ 0.  0.  0. ...,  0.  0.  0.]
     ..., 
     [ 0.  0.  0. ...,  0.  0.  0.]
     [ 0.  0.  0. ..., -1.  0.  0.]
     [ 0.  0.  0. ...,  0. -1. -1.]]

    References
    ----------
    .. [wikipedia-incidence] http://en.wikipedia.org/wiki/Incidence_matrix
    """

    if g.get_vertex_filter()[0] != None:
        index = g.new_vertex_property("int64_t")
        for i, v in enumerate(g.vertices()):
            index[v] = i
    else:
        index = g.vertex_index

    eindex = g.new_edge_property("int64_t")
    for i, e in enumerate(g.edges()):
        eindex[e] = i

    N = g.num_vertices()
    E = g.num_edges()
    if sparse:
        m = scipy.sparse.lil_matrix((N, E))
    else:
        m = matrix(zeros((N, E)))
    for v in g.vertices():
        if g.is_directed():
            for e in v.out_edges():
                m[index[v], eindex[e]] += -1
            for e in v.in_edges():
                m[index[v], eindex[e]] += 1
        else:
            for e in v.out_edges():
                m[index[v], eindex[e]] += 1
    if sparse:
        m = m.tocsr()
    return m
