#!/usr/bin/env python3
# -*- coding:utf-8 -*-

import os
import asyncio

import networkx as nx
from flexx import flx, config, event, ui


ASSETS = os.path.join(os.path.dirname(__file__), "assets")
flx.assets.associate_asset(__name__, "vis.js",  open(os.path.join(ASSETS, "vis.js")).read())
flx.assets.associate_asset(__name__, "vis.css", open(os.path.join(ASSETS, "vis.css")).read())


config.hostname = "0.0.0.0"
config.port = 9670
config.tornado_debug = True


class VisJS(flx.Widget):
    def init(self):
        window.igraph = self

    @event.action
    def update_viz(self, data):
        if data["nodes"]["add"]:
            self.nodes.add(data["nodes"]["add"])
        if data["nodes"]["remove"]:
            self.nodes.remove(data["nodes"]["remove"])
        if data["nodes"]["update"]:
            updated_nodes = [
                {
                    "id": node["id"],
                    "color": "yellow",
                }
                for node in data["nodes"]["update"]
            ]
            self.nodes.update(data["nodes"]["update"])
            original_nodes = [
                {
                    "id": node["id"],
                    "color": self.nodes.get(node["id"])["color"] or None
                }
                for node in data["nodes"]["update"]
            ]
            self.nodes.update(updated_nodes)
            def restore_nodes(original):
                self.nodes.update(original)
            window.setTimeout(restore_nodes, 2000, original_nodes)
        if data["edges"]["add"]:
            self.edges.add(data["edges"]["add"])
        if data["edges"]["remove"]:
            self.edges.remove(data["edges"]["remove"])
        if data["edges"]["update"]:
            updated_edges = [
                {
                    "id": edge["id"],
                    "color": {"color": "yellow"},
                }
                for edge in data["edges"]["update"]
            ]
            self.edges.update(data["edges"]["update"])
            original_edges = [
                {
                    "id": edge["id"],
                    "color": self.edges.get(edge["id"])["color"] or None
                }
                for edge in data["edges"]["update"]
            ]
            self.edges.update(updated_edges)
            def restore_edges(original):
                self.edges.update(original)
            window.setTimeout(restore_edges, 2000, original_edges)
        if data["options"]:
            self.network.setOptions(data["options"])
            self.network.redraw()

    @event.action
    def load_viz(self, data):
        window.setTimeout(self._load_viz, 500, data)

    def _load_viz(self, data):
        # data = vis.network.convertDot('dirnetwork { truc=machin        1 [label="trucee", a="b", color="green"];        1 -> 1 -> 2;        2 -> 3;        2 -- 4[label="truc"];        2 -> 1}')
        self.data = data
        self.nodes = vis.DataSet(data["nodes"])
        self.edges = vis.DataSet(data["edges"])

        options = data["options"]

        options.nodes = options.nodes or {}
        options.nodes.shape = options.nodes.shape or "dot"
        options.nodes.scaling = options.nodes.scaling or {}
        #options.nodes.scaling["customScalingFunction"] = lambda min, max, total, value: value/total

        options.edges = options.edges or {}
        options.edges.scaling = options.edges.scaling or {}
        #options.edges.scaling["customScalingFunction"] = lambda min, max, total, value: value/total

        options.configure = options.configure or {}
        options.configure.container = options.configure.container or document.getElementsByClassName("configure")[0]

        self.options = options
        self.network = vis.Network(
            self.node,
            {
                "nodes": self.nodes,
                "edges": self.edges
            },
            options
        )
        self.network.stabilize()

    def add_node(self, **kwargs):
        self.nodes.add(**kwargs)


class IGraph(flx.PyComponent):
    CSS = """
.flx-main-widget{
overflow:scroll;
}
.configure{
overflow:scroll;
}
"""
    graph = flx.AnyProp(None, settable=True)
    graph_options = {
#        "height": "90%",
    }
    graph_list = flx.ListProp([])
    current_graph = flx.IntProp(0, settable=True)

    def init(self):

        with ui.VSplit():
            with ui.HFix(flex=0):
                self.previous = ui.Button(text="<-", disabled=True, flex=1)
                self.content = ui.Label(flex=0)
                self.next = ui.Button(text="->", disabled=True, flex=1)
            with ui.HSplit(flex=1):
                self.configure = flx.Widget(css_class="configure", flex=0)
                with ui.HFix(flex=1):
                    self.visjs = VisJS(
                        style="background-color: #dddddd;", flex=1,
                    )
        self.refresh()

    @event.reaction("graph")
    def update_viz(self, *events):
        ev = events[-1]
        graph = ev["new_value"]
        old_graph = ev["old_value"]
        if old_graph is None:
            self.visjs.load_viz(graph)
        else:
            def find_by_id(id, iterable):
                try:
                    return [
                        elem
                        for elem in iterable
                        if elem["id"] == id
                    ][0]
                except IndexError:
                    return None
            self.visjs.update_viz(
                {
                    "nodes": {
                        "add": [
                            node
                            for node in graph["nodes"]
                            if not find_by_id(node["id"], old_graph["nodes"])
                        ],
                        "remove": [
                            node["id"]
                            for node in old_graph["nodes"]
                            if not find_by_id(node["id"], graph["nodes"])
                        ],
                        "update": [
                            node
                            for node in graph["nodes"]
                            if find_by_id(node["id"], old_graph["nodes"])
                            and find_by_id(node["id"], old_graph["nodes"]) != node
                        ]
                    },
                    "edges": {
                        "add": [
                            edge
                            for edge in graph["edges"]
                            if not find_by_id(edge["id"], old_graph["edges"])
                        ],
                        "remove": [
                            edge["id"]
                            for edge in old_graph["edges"]
                            if not find_by_id(edge["id"], graph["edges"])
                        ],
                        "update": [
                            edge
                            for edge in graph["edges"]
                            if find_by_id(edge["id"], old_graph["edges"])
                            and find_by_id(edge["id"], old_graph["edges"]) != edge
                        ],
                    },
                    "options": graph["options"],
                }
            )

    @flx.action
    def refresh(self):
        try:
            graph = nx.nx_agraph.read_dot(self.file)
        except ImportError:
            graph = nx.nx_pydot.read_dot(self.file)

        def uniq_id():
            i = 0
            while True:
                yield i
                i = i + 1
        genid = uniq_id()
        for src in graph.nodes():
            for dst in graph[src]:
                for number in graph[src][dst]:
                    if "smooth.type" not in graph[src][dst][number]:
                        graph[src][dst][number]["smooth.type"] = "curvedCW"
                    if "smooth.roundness" not in graph[src][dst][number]:
                        graph[src][dst][number]["smooth.roundness"] = float(number) / 5.

        graph_desc = {
            "nodes": [
                {
                    "id": node_id,
                    **dotted_dict_to_nested_dict({
                        k: cast_it(v)
                        for k, v in graph.node[node_id].items()
                    }),
                }
                for node_id in graph.nodes()
            ],
            "edges": [
                {
                    "id": next(genid),
                    "arrows": "to",
                    "from": src,
                    "to": dst,
                    "number": number,
                    **dotted_dict_to_nested_dict({
                        k: cast_it(v)
                        for k, v in graph[src][dst][number].items()
                    }),
                }
                for src in graph.nodes()
                for dst in graph[src]
                for number in graph[src][dst]
            ],
            "options": dotted_dict_to_nested_dict(
                {
                    **self.graph_options,
                    **dict_cast(graph.graph.get("graph", {})),
                }
            )
        }
        gl = len(self.graph_list)
        cg = self.current_graph
        last_graph = (gl != 0 and self.graph_list[-1]) or None
        if graph_desc != last_graph:
            self._mutate_graph_list(
                [graph_desc], 'insert', gl
            )
            if cg == (gl - 1):
                self.set_current_graph(cg + 1)

        asyncio.get_event_loop().call_later(0.1, self.refresh)

    @flx.reaction("graph_list", "current_graph")
    def _update_buttons(self, *evs):
        self.previous.set_disabled(
            len(self.graph_list) == 1 or self.current_graph == 0
        )
        self.previous.set_text(
            "{} <-".format(self.current_graph - 1) if self.current_graph else "|"
        )
        self.content.set_text("{}".format(self.current_graph))
        self.next.set_disabled(
            self.current_graph == len(self.graph_list) - 1
        )
        self.next.set_text(
            "-> {}".format(self.current_graph + 1) if self.current_graph < len(self.graph_list) - 1  else "|" )

    @flx.reaction("current_graph")
    def _update_graph(self, *evs):
        self.set_graph(self.graph_list[self.current_graph])

    @event.reaction("previous.pointer_click")
    def _previous(self, *evs):
        self.set_current_graph(self.current_graph - 1)

    @event.reaction("next.pointer_click")
    def _next(self, *evs):
        self.set_current_graph(self.current_graph + 1)


def dotted_dict_to_nested_dict(d):
    res = {}
    recursed_keys = set()
    for key, value in d.items():
        if "." in key:
            short_key = key.split(".")[0]
            recursed_keys.add(short_key)
            remaining_key = ".".join(key.split(".")[1:])
            if short_key not in res:
                res[short_key] = {}
            res[short_key][remaining_key] = value
        else:
            res[key] = value
    for key in recursed_keys:
        res[key] = dotted_dict_to_nested_dict(res[key])
    return res


def hardcoded_cast(elem):
    hardcoded = {
        str(e): e
        for e in [True, False, None]
    }
    if elem in hardcoded:
        return hardcoded[elem]
    else:
        raise ValueError(elem)


def fix_string_cast(elem):
    if isinstance(elem, str) and elem.startswith('"') and elem.endswith('"'):
        return elem[1:-1]
    else:
        raise ValueError(elem)


def cast_it(elem):
    for caster in [hardcoded_cast, float, fix_string_cast]:
        try:
            return caster(elem)
        except ValueError:
            pass
    return elem


def dict_cast(d):
    return {
        k: cast_it(v)
        for k, v in d.items()
    }


def main(file, open):
    IGraph.file = file
    app = flx.App(IGraph)
    app.serve()
    if open:
        app.launch()
    flx.start()
