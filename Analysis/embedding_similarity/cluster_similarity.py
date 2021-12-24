import pandas as pd
import numpy as np
import random
from collections import defaultdict
from matplotlib import pyplot as plt
from sklearn.cluster import KMeans, SpectralClustering
from scipy.spatial.distance import pdist, squareform
from scipy.sparse import csgraph
from numpy import linalg as LA


def get_argmax_total_similarity(similarity_matrix, from_items=None, rank_normalization=False):
    '''
    Finds the item of a matrix (similarity_matrix) that has the maximum aggregate similarity to all other items.
    If the "from_items" is not None, then only the rows/columns of the matrix in the from_items list are taken into account.
    :param  similarity_matrix:  (pandas.DataFrame) an NxN dataframe; should be (a) symmetric and (b) values {i,j} to
                                represent the similarity between item of row i and column j
    :param  from_items:         (list/set) a subset of the items (rows/columns) from which the item with the max similiarity will be selected
    :param  rank_normalization: (boolean) whether to modify the similarity matrix giving more emphasis to most similar values per row
                                by dividing each element with the rank it appears in the sorted list of values of the row
                                e.g., a_row = [0.5, 0.3, 0.4] --> modified_row = [0.5/1, 0.3/3, 0.4/2] = [0.5, 0.1, 0.2]
                                e.g., a_row = [0.1, 0.1, 0.4] --> modified_row = [0.1/2, 0.1/3, 0.4/1] = [0.05, 0.033, 0.4]
    :return:                    (scalar, e.g., str or int) the index of the item in the dataframe that has the max total similarity
    '''
    if from_items is None:
        df = similarity_matrix.copy()
    else:
        df = similarity_matrix.loc[from_items, from_items].copy()

    np.fill_diagonal(df.values, np.nan)  # set self-similarity to nan so that it is not taken into account

    if rank_normalization:
        for p1 in df.index:
            sorted_indexes = list(df.loc[p1, :].sort_values(ascending=False).index)
            df.loc[p1, sorted_indexes] = df.loc[p1, sorted_indexes] * [1.0 / i for i in range(1, 1 + df.shape[0])]

    sum_similarities = np.nansum(df, axis=1)
    if np.max(sum_similarities) == 0:  # all similarities are nan or zero
        next_item = random.sample(from_items, 1)[0]
    else:
        next_item = df.index[np.argmax(sum_similarities)]

    return next_item


def greedy_most_similar_elimination(similarity_matrix, rank_normalization=False):
    '''
    Selects iteratively the item in the given similarity_matrix that has the maximum aggregate similarity to all other items. At each iteration,
    only the similarities among the non-selected items are taken into account. At each iteration, the selected item is placed in the beginning of
    a list. At the end, this list is returned. Example: returned_list = [item_selected_last, ..., item_selected_first]
    :param  similarity_matrix:  (pandas.DataFrame) an NxN dataframe; should be (a) symmetric and (b) values {i,j} to
                                represent the similarity between item of row i and column j
    :param  rank_normalization: (boolean) whether to modify the similarity matrix giving more emphasis to most similar values per row
    :return:                    (list) a list of ordered items (from the input's index); the first item is the least similar
    '''
    selected_items = []
    for i in range(similarity_matrix.shape[0]):
        from_items = list(set(similarity_matrix.index) - set(selected_items))
        next_item = get_argmax_total_similarity(similarity_matrix, from_items=from_items,
                                                rank_normalization=rank_normalization)
        selected_items.insert(0, next_item)

    return selected_items


def get_argmin_total_similarity(similarity_matrix, from_items=None):
    '''
    Finds the item of a matrix (similarity_matrix) that has the minimum aggregate similarity to all other items.
    If the "from_items" is not None, then only the (a) rows of the matrix in the from_items list and (b) the columns
    of the matrix NOT in the from_items list are taken into account.
    :param  similarity_matrix:  (pandas.DataFrame) an NxN dataframe; should be (a) symmetric and (b) values {i,j} to
                                represent the similarity between item of row i and column j
    :param  from_items:         (list/set) a subset of the items (rows/columns) from which the item with the min similiarity will be selected
    :return:                    (scalar, e.g., str or int) the index of the item in the dataframe that has the min total similarity
    '''
    df = similarity_matrix.copy()
    np.fill_diagonal(df.values, np.nan)  # set self-similarity to nan so that it is not taken into account
    if from_items is not None:
        other_items = list(set(df.index) - set(from_items))
        df = df.loc[from_items, other_items]

    sum_similarities = np.nansum(df, axis=1)
    if np.max(sum_similarities) == 0:  # all similarities are nan or zero
        next_item = random.sample(from_items, 1)[0]
    else:
        next_item = df.index[np.argmin(sum_similarities)]

    return next_item


def greedy_least_similar_selection(similarity_matrix, nb_items=None):
    '''
    Selects iteratively the item in the given similarity_matrix that has the minimum aggregate similarity to all other items. At each iteration,
    only the similarities among the non-selected items and the already selected items are taken into account. At each iteration, the selected item is
    placed in the end of a list. At the end, this list is returned. Example: returned_list = [item_selected_first, ..., item_selected_last]
    :param  similarity_matrix:  (pandas.DataFrame) an NxN dataframe; should be (a) symmetric and (b) values {i,j} to
                                represent the similarity between item of row i and column j
    :param  nb_items:           (int) number of items to be selected; if None all items are selected in the returned list
    :return:                    (list) a list of ordered items (from the input's index); the first item is the least similar
    '''
    selected_items = []

    nb_total_items = similarity_matrix.shape[0]
    if (nb_items is None) or (nb_items > nb_total_items):
        nb_items = nb_total_items

    for i in range(nb_items):
        if len(selected_items) == 0:
            from_items = None
        else:
            from_items = list(set(similarity_matrix.index) - set(selected_items))
        next_item = get_argmin_total_similarity(similarity_matrix, from_items=from_items)
        selected_items.append(next_item)

    return selected_items


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


def getAffinityMatrix(coordinates, k=7):
    """
    Calculate affinity matrix based on input coordinates matrix and the numeber
    of nearest neighbours.

    Apply local scaling based on the k nearest neighbour
        References:
    https://papers.nips.cc/paper/2619-self-tuning-spectral-clustering.pdf
    """
    # calculate euclidian distance matrix
    dists = squareform(pdist(coordinates))

    # for each row, sort the distances ascendingly and take the index of the
    # k-th position (nearest neighbour)
    knn_distances = np.sort(dists, axis=0)[k]
    knn_distances = knn_distances[np.newaxis].T

    # calculate sigma_i * sigma_j
    local_scale = knn_distances.dot(knn_distances.T)

    affinity_matrix = dists * dists
    affinity_matrix = -affinity_matrix / local_scale
    # divide square distance matrix by local scale
    affinity_matrix[np.where(np.isnan(affinity_matrix))] = 0.0
    # apply exponential
    affinity_matrix = np.exp(affinity_matrix)
    np.fill_diagonal(affinity_matrix, 0)
    return affinity_matrix


def eigenDecomposition(A, topK=5):
    """
    :param A: Affinity matrix
    :param topK: Top k
    :return A tuple containing:
    - the optimal number of clusters by eigengap heuristic
    - all eigen values
    - all eigen vectors

    This method performs the eigen decomposition on a given affinity matrix,
    following the steps recommended in the paper:
    1. Construct the normalized affinity matrix: L = D−1/2ADˆ −1/2.
    2. Find the eigenvalues and their associated eigen vectors
    3. Identify the maximum gap which corresponds to the number of clusters
    by eigengap heuristic

    References:
    https://papers.nips.cc/paper/2619-self-tuning-spectral-clustering.pdf
    http://www.kyb.mpg.de/fileadmin/user_upload/files/publications/attachments/Luxburg07_tutorial_4488%5b0%5d.pdf
    """
    L = csgraph.laplacian(A, normed=True)
    n_components = A.shape[0]

    # LM parameter : Eigenvalues with largest magnitude (eigs, eigsh), that is, largest eigenvalues in
    # the euclidean norm of complex numbers.
    # eigenvalues, eigenvectors = eigsh(L, k=n_components, which="LM", sigma=1.0, maxiter=5000)
    eigenvalues, eigenvectors = LA.eig(L)

    plt.title('Largest eigen values of input matrix')
    plt.scatter(np.arange(len(eigenvalues)), eigenvalues)
    plt.grid()

    # Identify the optimal number of clusters as the index corresponding
    # to the larger gap between eigen values
    index_largest_gap = np.argsort(np.diff(eigenvalues))[::-1][:topK]
    nb_clusters = index_largest_gap + 1

    return nb_clusters, eigenvalues, eigenvectors


def get_optimal_number_of_clusters(similarity):
    '''
    A function that help us identify which is the optimal number of cluster for Kmeans
    :param similarity: The similarity matrix from graph embeddings
    '''
    distortions = []
    for i in range(1, 11):
        clustering = KMeans(n_clusters=i, init='random', n_init=10, max_iter=300, tol=1e-04, random_state=0).fit(
            similarity)
        distortions.append(clustering.inertia_)
    plt.plot(range(1, 11), distortions, marker='o')
    plt.xlabel('Number of clusters')
    plt.ylabel('Sum of squared distance')
    plt.show()


def clustering_based_selection(similarity_matrix, clustering_method, nb_clusters, nb_items=None, **kwargs):
    '''
    Applies a clustering algorithm to the similarity matrix to cluster items, and then selects samples from the classes.
    :param  similarity_matrix:  (pandas.DataFrame) an NxN dataframe; should be (a) symmetric and (b) values {i,j} to
                                represent the similarity between item of row i and column j
    :param  clustering_method:  (str) 'SpectralClustering' or 'Kmeans'
    :param  nb_clusters:        (int) number of clusters
    :param  nb_items:           (int) number of items to be selected; if None all items are selected in the returned list
    :param  **kwargs:           (dict) optional kwargs for the clustering algorithms
    :return:                    (list) a list of ordered items that are the samples from clusters
    '''
    sim = similarity_matrix.to_numpy()
    sim = np.nan_to_num(sim, nan=0)
    if clustering_method == 'SpectralClustering':
        clustering = getAffinityMatrix(sim, k=10)
        k, _, _ = eigenDecomposition(clustering)
        clustering = SpectralClustering(n_clusters=nb_clusters, affinity='precomputed', **kwargs).fit(sim)
        print(f'Optimal number of clusters {k}')
    elif clustering_method == 'Kmeans':
        get_optimal_number_of_clusters(sim)
        clustering = KMeans(n_clusters=nb_clusters, **kwargs).fit(sim)
    else:
        raise ValueError

    cluster_members_dict = defaultdict(list)
    for i, label in enumerate(clustering.labels_):
        cluster_members_dict[label].append(similarity_matrix.index[i])

    return sample_from_clusters(cluster_members_dict, nb_items=nb_items)


def select_from_similarity_matrix(similarity_matrix, method, **kwargs):
    if method == 'Greedy min':
        selected_items = greedy_most_similar_elimination(similarity_matrix, **kwargs)
    elif method == 'Greedy max':
        selected_items = greedy_least_similar_selection(similarity_matrix, **kwargs)
    elif method == 'Clustering':
        selected_items = clustering_based_selection(similarity_matrix, **kwargs)
    else:
        raise ValueError
    return selected_items


similarity_matrix = pd.read_csv('calculate_distance_and_similarity/RIPE_RIS_similarity_embeddings_20211221.csv',
                                header=0, index_col=0)
similarity_matrix.columns = similarity_matrix.columns.astype(float)

# example 1: select based on method 'Greedy min'
selected_items1 = select_from_similarity_matrix(similarity_matrix, 'Greedy max')
print('Greedy min: first 4 selected items')
print(selected_items1[0:4])
print()

nb_clusters = 6
kwargs = {'clustering_method': 'SpectralClustering', 'nb_clusters': nb_clusters}
selected_items2 = select_from_similarity_matrix(similarity_matrix, 'Clustering', **kwargs)
print('Clustering: first 4 selected items')
print(selected_items2[0:nb_clusters])
print()
