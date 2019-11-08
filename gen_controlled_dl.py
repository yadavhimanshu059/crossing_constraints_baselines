#!/usr/bin/env python3
import sys
import copy
import operator
import itertools
import random
from collections import Counter

import networkx as nx
import rfutils
import treegen
import cliqs.corpora as corpora
import cliqs.depgraph as depgraph

CUTOFF = 23

random.seed(0)

def dl_sequence(edges):
    return tuple(sorted(abs(h-d) for h, d in edges))

def filter_trees(ts, f, value):
    i = 0
    for edges in ts:
        i += 1
        if f(edges) == value:
            print("Considered %s trees" % str(i), file=sys.stderr)
            yield edges
            i = 0

def sample_forever(f):
    return iter(f, object())

def random_tree(f, value, n):
    ts = sample_forever(lambda: list(treegen.random_undirected_tree_edges(n)))
    for good_tree in filter_trees(ts, f, value):
        return good_tree

def rla_dl_seq(edges):
    """ Return a mapping from old nodes to new nodes """
    # Assumes no virtual root
    dl_seq = dl_sequence(edges)
    nodes = list(range(len(edges) + 1))
    N = len(nodes)
    old_t = nx.DiGraph(edges)

    def possible_edges_from(h, dl):
        yield h, h + dl
        yield h, h - dl
        
    def edge_conditions(t, h, d):
        yield 0 <= d < N
        #yield (h, d) not in t.edges()
        #yield (d, h) not in t.edges()
        test_t = copy.deepcopy(t)
        test_t.add_edge(h, d)
        yield nx.is_forest(test_t)

    def attempt():
        dls = list(dl_seq)
        new_t = nx.DiGraph()
        new_t.add_nodes_from(nodes)
    
        old_root = depgraph.root_of(old_t)
        new_root = random.choice(nodes)
        old_to_new = {old_root: new_root}
        
        for old_h in nx.depth_first_search.dfs_preorder_nodes(old_t, old_root):
            outs = list(old_t.edge[old_h])
            new_h = old_to_new[old_h]
            for old_d in outs:
                possibles = {
                    (dl, new_d)
                    for dl in dls
                    for _, new_d in possible_edges_from(new_h, dl)
                    if all(edge_conditions(new_t, new_h, new_d))
                }
                if not possibles:
                    #print('dead end', file=sys.stderr)
                    return None
                dl, new_d = random.choice(list(possibles))
                new_t.add_edge(new_h, new_d)
                #if not nx.is_forest(new_t):
                #    print("not a tree", file=sys.stderr)
                #    return None
                old_to_new[old_d] = new_d
                dls.remove(dl)                 
        return old_to_new

    num_rejected = 0
    while True:
        result = attempt()
        if result:
            print("Rejected: ", num_rejected, file=sys.stderr)
            return tuple(result[k] for k in sorted(result.keys()))
        else:
            num_rejected += 1

def test_rla_dl_seq():
    d = (1, 1, 1, 2, 2)
    edges = [(2, 0), (2, 1), (3, 2), (3, 5), (5, 4)]
    correct = {(0, 1, 2, 3, 4, 5),
               (0, 2, 1, 3, 4, 5),
               (0, 3, 1, 2, 5, 4),
               (1, 0, 2, 3, 4, 5),
               (2, 0, 1, 3, 4, 5),
               (2, 5, 4, 3, 0, 1),
               (3, 0, 1, 2, 5, 4),
               (3, 5, 4, 2, 1, 0),
               (4, 5, 3, 2, 1, 0),
               (5, 2, 4, 3, 0, 1),
               (5, 3, 4, 2, 1, 0),
               (5, 4, 3, 2, 1, 0)}
    
               

        
def random_undirected_tree_dl_seq(dl_seq):
    dl_counter = Counter(dl_seq)
    def attempt():
        result = nx.Graph()
        result.add_nodes_from(range(len(dl_seq) + 1))
        for dl, k in dl_counter.items():
            possibles = possible_edges_with_dl(result, dl)
            if not possibles:
                return None
            else:
                possible_sets = itertools.combinations(possibles, k)
                edge_set = random.choice(list(possible_sets))
                result.add_edges_from(edge_set)
                if not nx.is_forest(result):
                    return None
        return result

    num_rejected = 0
    while True:
        result = attempt()
        if result:
            print("Rejected: ", num_rejected, file=sys.stderr)
            return frozenset(map(frozenset, result.edges()))
        else:
            num_rejected += 1

def random_directed_tree_dl_seq(dl_seq):
    edges = frozenset(random_undirected_tree_dl_seq(dl_seq))
    nodes = frozenset.union(*edges)
    root = random.choice(list(nodes))
    return list(treegen.rooted_at(edges, root))

def possible_edges_with_dl(t, dl):
    def possible_edges():
        for d in t.nodes():
            yield d + dl, d
            yield d - dl, d

    def edge_conditions(h, d):
        yield 0 <= h < N
        yield 0 <= d < N
        yield not t.has_edge(h, d)
        
    N = len(t.nodes())
    return {
        frozenset(edge) for edge in possible_edges()
        if all(edge_conditions(*edge))
    }

def test_random_tree_dl_seq():
    d = [1, 2, 2, 2] # has 20 solutions
    # Correct set of random trees for that dl sequence:
    correct = frozenset({frozenset({(0, 2), (1, 3), (2, 1), (2, 4)}),
                         frozenset({(0, 2), (1, 0), (2, 4), (3, 1)}),
                         frozenset({(1, 2), (1, 3), (2, 0), (2, 4)}),
                         frozenset({(2, 0), (2, 3), (2, 4), (3, 1)}),
                         frozenset({(1, 2), (2, 0), (2, 4), (3, 1)}),
                         frozenset({(2, 0), (3, 1), (4, 2), (4, 3)}),
                         frozenset({(2, 0), (2, 3), (3, 1), (4, 2)}),
                         frozenset({(2, 0), (2, 4), (3, 1), (4, 3)}),
                         frozenset({(0, 1), (1, 3), (2, 0), (4, 2)}),
                         frozenset({(0, 1), (0, 2), (1, 3), (2, 4)}),
                         frozenset({(0, 2), (1, 0), (1, 3), (2, 4)}),
                         frozenset({(2, 0), (3, 1), (3, 4), (4, 2)}),
                         frozenset({(1, 3), (2, 0), (3, 4), (4, 2)}),
                         frozenset({(0, 1), (1, 3), (2, 0), (2, 4)}),
                         frozenset({(2, 0), (2, 4), (3, 1), (3, 2)}),
                         frozenset({(0, 2), (2, 4), (3, 1), (4, 3)}),
                         frozenset({(0, 2), (2, 3), (2, 4), (3, 1)}),
                         frozenset({(1, 3), (2, 0), (2, 1), (2, 4)}),
                         frozenset({(1, 3), (2, 0), (2, 4), (3, 2)}),
                         frozenset({(1, 3), (2, 0), (2, 1), (4, 2)})})
    lots_of_samples = Counter(
        frozenset(random_directed_tree_dl_seq(d))
        for _ in range(10000)
    )
    # need to subtract 1 from samples before testing...
    assert frozenset(lots_of_samples) == correct

    d = [1, 1, 2, 3] # has 90 solutions, listed below
    # 18 undirected solutions

def randomly_reorder_tree(edges, verbose=False):
    edges = list(edges)
    nodes = set(n for edge in edges for n in edge)
    ordered_nodes = sorted(nodes)
    reordered_nodes = ordered_nodes[:]
    random.shuffle(ordered_nodes)
    mapping = dict(zip(ordered_nodes, reordered_nodes))
    if verbose:
        print(mapping, file=sys.stderr)
    return [(mapping[n1], mapping[n2]) for n1, n2 in edges]

def random_order(f, value, tree, verbose=False):
    ts = sample_forever(lambda: randomly_reorder_tree(tree, verbose=verbose))
    for good_tree in filter_trees(ts, f, value):
        return good_tree

def add_virtual_root(t):
    root = depgraph.root_of(t)
    edges = [(h+1, d+1) for h, d in t.edges()]
    edges.append((0, root+1))
    return nx.DiGraph(edges)

def run(lang, **opts):
    sentences = sorted(corpora.sud_corpora[lang].sentences(**opts), key=len)
    for i, tree in enumerate(sentences):
        if len(tree) <= 3: # no crossings possible: not interesting
            continue
        if len(tree) > CUTOFF:
            continue

        real_tree_code = sorted(tree.edges())
        
        edges = [(h-1, d-1) for h, d in real_tree_code if h != 0] # remove the root
        d = dl_sequence(edges)
        print("Finding random tree for %s sentence of length %s with dl sequence %s" % (lang, str(len(tree)-1), str(d)), file=sys.stderr)
        a_random_tree = nx.DiGraph(random_directed_tree_dl_seq(d))
        assert dl_sequence(a_random_tree.edges()) == d
        a_random_tree = add_virtual_root(a_random_tree)
        random_tree_code = sorted(a_random_tree.edges())

        #print("Finding random order for sentence of length %s with dl sequence %s" % (str(len(tree)-1), str(d)), file=sys.stderr)
        #random_order_code = rla_dl_seq(edges)
        #random_order_tree = nx.relabel_nodes(nx.DiGraph(edges), dict(enumerate(random_order_code)))
        #assert d == dl_sequence(random_order_tree.edges())        
        #a_random_order_edges = random_order(dl_sequence, d, edges)
        #a_random_order = nx.DiGraph([(h+1, d+1) for h, d in a_random_order_edges]) # move everything up 1
        #a_random_order.add_edge(0, depgraph.root_of(a_random_order)) # add the root back in
        #random_order_code = sorted(a_random_order.edges())

        yield {            
            'lang': lang,
            'n': len(tree) - 1,
            'start_line': tree.start_line,
            'real_tree': str(real_tree_code),
            'random_tree': str(random_tree_code),
            #'random_order': str(random_order_code)
        }

def main():
    langs = sorted(corpora.sud_langs)
    rfutils.write_dicts(sys.stdout, rfutils.flatmap(run, langs))

if __name__ == '__main__':
    main()
