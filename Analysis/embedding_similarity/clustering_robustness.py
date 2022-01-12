import pandas as pd
import numpy as np
import os, statistics
import json
import random
from sklearn.cluster import KMeans, SpectralClustering
from matplotlib import pyplot as plt
from tqdm import tqdm
from collections import defaultdict


MAX_LENGTH = 20
INITIAL_PROXIMITY = 1443060
ASN2ASN_DIST_FNAME = '../../Datasets/RIPE_RIS_peers/asn2asn__only_peers_pfx.json'
SIMILARITY_MATRIX = 'calculate_distance_and_similarity/ALL_RIPE_RIS_similarity_embeddings_BGP2VEC_20210107.csv'
PROXIMITY_FNAME = 'proximity_selected_monitors_ripe_ris_pathlens_100k.json'


def calculate_proximity(next_item, asn2asn, proximity):
    for o_asn, dict_o_asn in asn2asn.items():
        if (next_item in dict_o_asn.keys()) and (dict_o_asn[next_item] < proximity[o_asn]):
            proximity[o_asn] = dict_o_asn[next_item]
    return proximity


def get_proximity_vector(selected_items, asn2asn):
    proximity = {o_asn: MAX_LENGTH for o_asn in asn2asn.keys()}
    proximity_vector = []
    for i, item in tqdm(enumerate(selected_items)):
        proximity = calculate_proximity(item, asn2asn, proximity)
        proximity_vector.append(sum(proximity.values()))
    proximity_vector = [(i - 1) / INITIAL_PROXIMITY for i in proximity_vector]  # normalize proximity to [0,1]
    return proximity_vector


def sample_from_clusters(cluster_members_dict, nb_items=None):
    '''
    Samples items from the clusters, starting from a random item in the largest cluster, then a random item in the second largest cluster, and so on.
    When elements of all clusters are selected, then starts again from the largest cluster, until all items (or up to nb_items) are selected.
    :param  cluster_members_dict:   (dict of lists) dict of the form {cluster label: list of members of the cluster}
    :param  nb_items:               (int) number of items to be selected; if None all items are selected in the returned list
    :return:                        (list) a list of ordered items that are the samples from clusters
    '''

    nb_clusters = len(cluster_members_dict.keys())
    nb_all_items = sum([len(v) for v in cluster_members_dict.values()])
    if (nb_items is None) or (nb_items > nb_all_items):
        nb_items = nb_all_items

    sorted_clusters = sorted(cluster_members_dict, key=lambda k: len(cluster_members_dict.get(k)), reverse=True)

    selected_items = []
    for i in range(nb_items):
        ind = i % nb_clusters  # iterate over the sorted_clusters by getting the index of the current cluster
        current_cluster = sorted_clusters[ind]
        len_current_cluster = len(cluster_members_dict[current_cluster])
        if len_current_cluster > 0:
            next_item_ind = random.sample(range(len_current_cluster), 1)[0]
            next_item = cluster_members_dict[current_cluster].pop(next_item_ind)
            selected_items.append(next_item)
        i += 1

    return selected_items


def clustering_based_selection(similarity_matrix, clustering_method, nb_clusters, nb_items=None, **kwargs):
    '''
    Applies a clustering algorithm to the similarity matrix to cluster items, and then selects samples from the classes.
    :param  similarity_matrix:  (pandas.DataFrame) an NxN dataframe; should be (a) symmetric and (b) values {i,j} to
                                represent the similarity between item of row i and column j
    :param  nb_clusters:        (int) number of clusters
    :return:                    (list) a list of ordered items that are the samples from clusters
    '''
    sim = similarity_matrix.to_numpy()
    sim = np.nan_to_num(sim, nan=0)
    if clustering_method == 'SpectralClustering':
        clustering = SpectralClustering(n_clusters=nb_clusters, affinity='precomputed', **kwargs).fit(sim)
    elif clustering_method == 'Kmeans':
        clustering = KMeans(n_clusters=nb_clusters, **kwargs).fit(sim)
    else:
        raise ValueError
    cluster_members_dict = defaultdict(list)
    for i, label in enumerate(clustering.labels_):
        cluster_members_dict[label].append(similarity_matrix.index[i])

    return sample_from_clusters(cluster_members_dict, nb_items=nb_items)


def plot_proximity_score_for_different_values_of_k(proximity_vector):
    fontsize = 15
    linewidth = 2
    colors = ['g', '--g', 'r', '--r', 'b', '--b', 'k', '--k', 'm', '--m']
    leg_str = []
    keep_len_set = set()
    for i, k in enumerate(proximity_vector.keys()):
        keep_len_set.add(len(proximity_vector[k]))
    for j in keep_len_set:
        print(j)
    print('----------')

    min_monitors_number = min(keep_len_set)
    print(min_monitors_number)
    max_monitors_number = max(keep_len_set)
    print(max_monitors_number)
    median_monitors_number = int(statistics.median(keep_len_set))
    new_list = list(keep_len_set)
    # If the median is not in the list, take the most similar to it.
    new_median = new_list[min(range(len(new_list)), key=lambda i: abs(new_list[i] - median_monitors_number))]
    print(median_monitors_number)
    min_flag = True
    max_flag = True
    median_flag = True
    for i, k in enumerate(proximity_vector.keys()):
        if len(proximity_vector[k]) == min_monitors_number and min_flag:
            print('Min ' + str(len(proximity_vector[k])))
            X = list(range(1, 1 + len(proximity_vector[k])))
            plt.plot(X, proximity_vector[k], colors[i], linewidth=linewidth)
            k_new = 'SpectralClustering k7 min'
            leg_str.append(k_new)
            min_flag = False
        if len(proximity_vector[k]) == max_monitors_number and max_flag:
            print('Max ' + str(len(proximity_vector[k])))
            X = list(range(1, 1 + len(proximity_vector[k])))
            plt.plot(X, proximity_vector[k], colors[i], linewidth=linewidth)
            k_new = 'SpectralClustering k7 max'
            leg_str.append(k_new)
            max_flag = False
        if len(proximity_vector[k]) == new_median and median_flag:
            print('Median ' + str(len(proximity_vector[k])))
            X = list(range(1, 1 + len(proximity_vector[k])))
            plt.plot(X, proximity_vector[k], colors[i], linewidth=linewidth)
            k_new = 'SpectralClustering k7 median'
            leg_str.append(k_new)
            median_flag = False

    plt.xscale('log')
    plt.xlabel('#monitors', fontsize=fontsize)
    plt.ylabel('Proximity (normalized)', fontsize=fontsize)
    plt.xticks(fontsize=fontsize)
    plt.yticks(fontsize=fontsize)
    plt.tight_layout()
    plt.axis([1, 1500, 0.1, 0.35])
    plt.legend(leg_str)
    plt.grid(True)
    # plt.savefig('fig_ripe_ris_subset_selection_vs_proximity.png')
    plt.show()


with open(ASN2ASN_DIST_FNAME, 'r') as f:
    asn2asn = json.load(f)

similarity_matrix = pd.read_csv(SIMILARITY_MATRIX, header=0, index_col=0)
similarity_matrix.replace(np.nan, 0, inplace=True)

method_param_dict = {
    'Clustering1 spectral k7': {'method': 'Clustering', 'sim_matrix': similarity_matrix, 'args': {'clustering_method': 'SpectralClustering', 'nb_clusters': 7}},
    'Clustering2 spectral k7': {'method': 'Clustering', 'sim_matrix': similarity_matrix, 'args': {'clustering_method': 'SpectralClustering', 'nb_clusters': 7}},
    'Clustering3 spectral k7': {'method': 'Clustering', 'sim_matrix': similarity_matrix, 'args': {'clustering_method': 'SpectralClustering', 'nb_clusters': 7}},
    'Clustering4 spectral k7': {'method': 'Clustering', 'sim_matrix': similarity_matrix, 'args': {'clustering_method': 'SpectralClustering', 'nb_clusters': 7}},
    'Clustering5 spectral k7': {'method': 'Clustering', 'sim_matrix': similarity_matrix, 'args': {'clustering_method': 'SpectralClustering', 'nb_clusters': 7}},
    'Clustering6 spectral k7': {'method': 'Clustering', 'sim_matrix': similarity_matrix, 'args': {'clustering_method': 'SpectralClustering', 'nb_clusters': 7}},
    'Clustering7 spectral k7': {'method': 'Clustering', 'sim_matrix': similarity_matrix, 'args': {'clustering_method': 'SpectralClustering', 'nb_clusters': 7}},
    'Clustering8 spectral k7': {'method': 'Clustering', 'sim_matrix': similarity_matrix, 'args': {'clustering_method': 'SpectralClustering', 'nb_clusters': 7}},
    'Clustering9 spectral k7': {'method': 'Clustering', 'sim_matrix': similarity_matrix, 'args': {'clustering_method': 'SpectralClustering', 'nb_clusters': 7}},
    'Clustering10 spectral k7': {'method': 'Clustering', 'sim_matrix': similarity_matrix, 'args': {'clustering_method': 'SpectralClustering', 'nb_clusters': 7}}}

print('### Selected monitors by method ###')
for m, params in method_param_dict.items():
    selected_items = clustering_based_selection(params['sim_matrix'], **params['args'])
    print('\t{} [DONE]'.format(m))
    with open('dataset_selected_monitors_ripe_ris_pathlens_100k_{}.json'.format(
            '_'.join(m.lower().translate('()').split(' '))), 'w') as f:
        json.dump(selected_items, f)

# calculating the proximity vector takes ~20sec per method
if os.path.exists(PROXIMITY_FNAME):
    print('Loading proximities from existing file')
    with open(PROXIMITY_FNAME, 'r') as f:
        proximity_vector = json.load(f)
else:
    print('Calculating proximities')
    proximity_vector = dict()
    for m, params in method_param_dict.items():
        with open('dataset_selected_monitors_ripe_ris_pathlens_100k_{}.json'.format('_'.join(m.lower().split(' '))),
                  'r') as f:
            selected_items = json.load(f)
        proximity_vector[m] = get_proximity_vector(selected_items, asn2asn)
        print('\t{} [DONE]'.format(m))
    with open(PROXIMITY_FNAME, 'w') as f:
        json.dump(proximity_vector, f)

plot_proximity_score_for_different_values_of_k(proximity_vector)