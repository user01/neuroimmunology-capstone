
from functools import reduce
import pandas as pd


def rbind(df_a, df_b):
    return pd.DataFrame.append(df_a, df_b) \
        .reset_index(drop=True)


def rbind_all(lst):
    return reduce(rbind, lst)


def set_contained_in_sets(pair, gene_sets):
    """Pair is contained in any of the gene sets"""
    for gene_set in gene_sets:
        if set_contained_in_set(pair, gene_set):
            return True
    return False


def set_contained_in_set(pair, gene_set):
    """Either of the pair exist in this gene set"""
    return len(pair & gene_set) > 0


def add_pair_to_sets(pair, gene_sets):
    """If a pair is contained in a gene set, union the sets"""
    gene_sets_new = []
    for gene_set in gene_sets:
        if set_contained_in_set(pair, gene_set):
            gene_sets_new.append(gene_set | pair)
    return gene_sets_new


def collapse_sets(gene_sets):
    """Collapse gene sets that can be unioned"""
    return collapse_sets_(gene_sets, [])


def collapse_sets_(unfinished_sets, known_sets):
    """Private - Collapse gene sets that can be unioned"""
    if len(unfinished_sets) < 1:
        return known_sets
    gene_set, *remaining_sets = unfinished_sets

    if set_contained_in_sets(gene_set, remaining_sets):
        # then this set collides with at least one of the
        # remaining_sets
        known_clean = known_sets
        untested_sets = list(map(
            lambda gs: gs | gene_set if set_contained_in_set(
                gs, gene_set) else gs,
            remaining_sets))
    else:
        # this set stands alone
        known_clean = known_sets + [gene_set]
        untested_sets = remaining_sets

    return collapse_sets_(untested_sets, known_clean)


def pairs_to_sets(pairs):
    """Turn a low/high pandas dataframe into a list of sets"""
    return pairs_to_sets_(pairs[['low', 'high']], [])


def pairs_to_sets_(pairs, gene_sets):
    """Private - turn a pandas df into a list of sets"""
    if pairs.shape[0] < 1:
        return gene_sets

    pair = set([pairs.iloc[0][0], pairs.iloc[0][1]])

    if set_contained_in_sets(pair, gene_sets):
        gene_sets = add_pair_to_sets(pair, gene_sets)
    else:
        gene_sets.append(pair)

    gene_sets = collapse_sets(gene_sets)

    pairs_tail = pairs.tail(-1)
    return pairs_to_sets_(pairs_tail, gene_sets)
