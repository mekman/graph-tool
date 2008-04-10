// graph-tool -- a general graph modification and manipulation thingy
//
// Copyright (C) 2007  Tiago de Paula Peixoto <tiago@forked.de>
//
// This program is free software; you can redistribute it and/or
// modify it under the terms of the GNU General Public License
// as published by the Free Software Foundation; either version 3
// of the License, or (at your option) any later version.
//
// This program is distributed in the hope that it will be useful,
// but WITHOUT ANY WARRANTY; without even the implied warranty of
// MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
// GNU General Public License for more details.
//
// You should have received a copy of the GNU General Public License
// along with this program. If not, see <http://www.gnu.org/licenses/>.

#include "graph_filtering.hh"

#include <boost/lambda/bind.hpp>
#include <boost/python.hpp>

#include "graph.hh"
#include "histogram.hh"
#include "graph_selectors.hh"
#include "graph_properties.hh"

#include "graph_correlations.hh"

#include <iostream>

using namespace std;
using namespace boost;
using namespace boost::lambda;
using namespace graph_tool;

// implementations spread across different compile units to minimize memory
// usage during compilation
void graph_correlations_imp1(const GraphInterface& g, python::object& hist,
                             python::object& ret_bins,
                             boost::any deg1, boost::any deg2,
                             boost::any weight,
                             const array<vector<long double>,2>& bins);


typedef ConstantPropertyMap<int,GraphInterface::edge_t> cweight_map_t;

python::object
get_vertex_correlation_histogram(const GraphInterface& gi,
                                 GraphInterface::deg_t deg1,
                                 GraphInterface::deg_t deg2,
                                 string weight,
                                 const vector<long double>& xbin,
                                 const vector<long double>& ybin)
{
    python::object hist;
    python::object ret_bins;

    array<vector<long double>,2> bins;
    bins[0] = xbin;
    bins[1] = ybin;

    any weight_prop;
    typedef DynamicPropertyMapWrap<long double, GraphInterface::edge_t>
        wrapped_weight_t;

    if (weight != "")
    {
        dynamic_property_map* map =
            any_cast<dynamic_property_map*>(edge_prop(weight, gi, true));
        weight_prop = wrapped_weight_t(*map);
    }
    else
        weight_prop = cweight_map_t(1);

    try
    {
        run_action<>()(gi, get_correlation_histogram<GetNeighboursPairs>
                       (hist, bins, ret_bins),
                       all_selectors(), all_selectors(),
                       mpl::vector<cweight_map_t>())
            (degree_selector(deg1, gi), degree_selector(deg2, gi), weight_prop);
    }
    catch (ActionNotFound&)
    {
        graph_correlations_imp1(gi, hist, ret_bins, degree_selector(deg1, gi),
                                degree_selector(deg2, gi), weight_prop, bins);
    }

    return python::make_tuple(hist, ret_bins);
}

using namespace boost::python;

void export_vertex_correlations()
{
    def("vertex_correlation_histogram", &get_vertex_correlation_histogram);
}
