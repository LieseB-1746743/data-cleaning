from sklearn.cluster import AgglomerativeClustering
import numpy as np
import pandas as pd
import string
import hashlib
from unidecode import unidecode
from operator import itemgetter
import warnings


class Cluster:
    def __init__(self, id, distance, original_values, strings):
        self.id = id
        self.original_values = original_values
        self.distance = distance
        self.content = []  # list of dictionaries: [{"value":..,"duplicates":..},...,{}]
        self.replaceby = None
        self.max_occurrences_percentage = 0
        self.initialise_content(original_values, strings)
        self.selected = True

    def recalculate_max_occurences_percentage(self):
        value_counts = self.original_values.value_counts(sort=False)
        max_occurrences = 0
        total_occurrences = 0

        for item in self.content:
            s = item["value"]
            n_duplicates = value_counts.loc[s]
            total_occurrences += int(n_duplicates)
            if int(n_duplicates) > max_occurrences:
                max_occurrences = int(n_duplicates)
        self.max_occurrences_percentage = max_occurrences / total_occurrences * 100

    def remove_strings(self, list_of_strings):
        new_content_for_this_cluster = []
        for item in self.content:
            if item["value"] not in list_of_strings:
                new_content_for_this_cluster.append(item)

        self.content = new_content_for_this_cluster

    def initialise_content(self, original_values, strings):
        value_counts = original_values.value_counts(sort=False)
        max_occurrences = 0
        total_occurrences = 0

        for s in strings:
            n_duplicates = value_counts.loc[s]
            self.content.append({
                "value": s,
                "duplicates": int(n_duplicates)
            })
            total_occurrences += int(n_duplicates)
            if int(n_duplicates) > max_occurrences:
                max_occurrences = int(n_duplicates)
        self.max_occurrences_percentage = max_occurrences / total_occurrences * 100
        self.sort()

    def sort(self):
        self.content = sorted(self.content, key=itemgetter("duplicates"), reverse=True)
        self.replaceby = self.content[0]['value']

    def get_cluster_as_dict(self):
        cluster = {
            "id": self.id,
            "replaceby": self.replaceby,
            "content": self.content,
            "max_occurrences_percentage": self.max_occurrences_percentage,
            "selected": self.selected,
            "distance": self.distance
        }
        return cluster

    def get_strings_in_cluster(self):
        return [dict["value"] for dict in self.content]


class Clustering:
    def __init__(self, table, column):
        df = table.get_dataframe()
        self.original_values = df[column]
        self.treatments = None
        self.bigrams = None
        self.signatures = None
        self.index_buckets = None
        self.clusters = None
        self.counter = 0

    def strip(self, s):
        """
        Remove all whitespace and punctuation. Change characters to lowercase and remove accents.
        :param s: a string
        :return: Stripped string.
        """
        s = s.lower()
        s = s.replace(" ", "")
        translation = str.maketrans("", "", string.punctuation)
        s = s.translate(translation)
        s = unidecode(s)  # remove accents
        return s

    def getNgrams(self, string, n):
        """
        Generate all n-grams of a string.
        :param string: a string
        :param n: length of n-grams
        :return: Set of n-grams.
        """
        if len(string) < n:
            print("len(string) < n", [string])
            return set([])
        elif len(string) == n:
            return set([string])
        rv = []
        for i in range(len(string) - n + 1):
            s = ''
            for j in range(n):
                s += string[i + j]
            rv.append(s)
        return set(rv)

    def getBiGrams(self, string):
        return self.getNgrams(string, 2)

    def h2(self, nGram):
        return oct(int(nGram.encode('utf-8').hex(), 16))[2:]

    def h3(self, nGram):
        return int(hashlib.sha1(nGram.encode()).hexdigest(), 16)

    def h4(self, nGram):
        return int(hashlib.sha224(nGram.encode()).hexdigest(), 16)

    def h5(self, nGram):
        return int(hashlib.sha256(nGram.encode()).hexdigest(), 16)

    def h6(self, nGram):
        return int(hashlib.sha384(nGram.encode()).hexdigest(), 16)

    def h7(self, nGram):
        return int(hashlib.blake2b(nGram.encode()).hexdigest(), 16)

    def h8(self, nGram):
        return int(hashlib.sha3_224(nGram.encode()).hexdigest(), 16)

    def h9(self, nGram):
        return int(hashlib.sha3_256(nGram.encode()).hexdigest(), 16)

    def h10(self, nGram):
        return int(hashlib.sha3_384(nGram.encode()).hexdigest(), 16)

    def h11(self, nGram):
        return int(hashlib.sha3_512(nGram.encode()).hexdigest(), 16)

    def h12(self, nGram):
        return int(hashlib.md5(nGram.encode()).hexdigest(), 16)

    def min_hash_signature(self, nGrams):
        """ Generate a MinHash signature for a set of n-grams. """
        hashes = [hash, self.h2, self.h3, self.h4, self.h5, self.h6, self.h7, self.h8, self.h9, self.h10, self.h11, self.h12]
        signature = []
        for h in hashes:
            hashed_values = list(map(h, nGrams))
            signature.append(min(hashed_values))
        return signature

    def prepare_data(self):
        """
        Prepare data for being clustered: drop duplicates and NaNs, strip, calculate bigrams and min-hash signatures.
        """
        s = self.original_values.copy()
        original_name = s.name
        s = s.drop_duplicates(keep='first')
        s = s.dropna()
        s = s.rename("original_values")
        stripped = s.apply(self.strip)
        stripped = stripped.rename("stripped")
        df = pd.concat([s, stripped], axis=1)
        df = df.loc[df["stripped"].str.len() >= 2]
        s = df["original_values"]
        stripped = df["stripped"]
        s = s.rename(original_name)
        self.treatments = s.copy()
        s = stripped.apply(self.getBiGrams)
        self.bigrams = s.copy()
        s = s.apply(self.min_hash_signature)
        self.signatures = s.copy()

    def jaccard_similarity(self, set1, set2):
        """
        Calculate the jaccard similarity between two sets.
        :param set1: First set
        :param set2: Second set
        :return: Jaccard similarity: a number between 0 and 1, from not similar to very similar.
        """
        #union = set1.union(set2)
        intersect = set1.intersection(set2)
        #similarity = float(len(intersect) / len(union))
        similarity = float(len(intersect) / (len(set1) + len(set2) - len(intersect)))
        return similarity

    def create_buckets(self):
        """Divide data in buckets based on their similarity."""
        index_buckets = []  # buckets containing indices (keys) of strings
        bigrams = self.bigrams
        signatures = self.signatures

        for i in range(len(signatures.index)):
            signature = signatures.iloc[i]
            added = False
            highest_sim = 0
            highest_sim_at_index = None
            highest_sim_at_bucket = None

            for j in range(len(index_buckets)):  # for every bucket
                for k in index_buckets[j]:  # for every index in the bucket
                    signature_in_bucket = signatures.iloc[k]
                    jaccard_sim = len(list(set(signature).intersection(set(signature_in_bucket))))
                    if jaccard_sim >= 6:
                        real_jaccard_sim = self.jaccard_similarity(bigrams.iloc[i], bigrams.iloc[k]) * 12
                        if real_jaccard_sim >= 6:
                            index_buckets[j].append(i)
                            added = True
                            break
                    elif jaccard_sim >= 1 and jaccard_sim > highest_sim:
                        highest_sim = jaccard_sim
                        highest_sim_at_index = k
                        highest_sim_at_bucket = j

                if added:
                    break
            if not added:
                if highest_sim_at_index and highest_sim_at_bucket:
                    real_jaccard_sim = self.jaccard_similarity(bigrams.iloc[i], bigrams.iloc[highest_sim_at_index]) * 12
                    if real_jaccard_sim >= 2:
                        index_buckets[highest_sim_at_bucket].append(i)
                else:
                    index_buckets.append([i])

        filtered_index_buckets = []
        for bucket in index_buckets:
            if len(bucket) > 1:
                filtered_index_buckets.append(bucket)
        self.index_buckets = filtered_index_buckets

    def cluster_bucket(self, index_bucket):
        """
        Cluster a bucket of data.
        :param index_bucket: A list of indices in self.treatments.
        :return: All clusters of length > 1.
        """
        distance_matrix = np.empty(shape=(len(index_bucket), len(index_bucket)))

        for row in range(len(index_bucket)):
            for col in range(row, len(index_bucket)):
                if row == col:
                    distance_matrix[row, col] = 0
                else:
                    s1_ngrams = self.bigrams.iloc[index_bucket[row]]
                    s2_ngrams = self.bigrams.iloc[index_bucket[col]]
                    distance_matrix[row, col] = float(1 - self.jaccard_similarity(s1_ngrams, s2_ngrams))

        for col in range(len(index_bucket)):
            for row in range(col + 1, len(index_bucket)):
                distance_matrix[row, col] = distance_matrix[col, row]
        result = AgglomerativeClustering(n_clusters=None, affinity='precomputed', linkage='average',
                                         compute_full_tree=True, distance_threshold=0.35).fit(distance_matrix)

        clusters = []
        value_counts = self.original_values.value_counts(sort=False)
        for clusterindex in range(result.n_clusters_):
            indices = []
            strings = []
            for i, x in enumerate(result.labels_):
                if x == clusterindex:
                    indices.append(i)
                    strings.append(self.treatments.iloc[index_bucket[i]])
            if len(strings) > 1:
                # calculate average pairwise distance
                distances = []
                for i in range(len(indices)):
                    for j in range(i, len(indices)):
                        distances.append(distance_matrix[i, j])
                distances = np.array(distances)
                avg_distance = np.average(distances)

                # add cluster to list of clusters
                new_cluster = Cluster(self.counter, avg_distance, self.original_values, strings)
                clusters.append(new_cluster)
                self.counter += 1

        return clusters

    def cluster(self):
        """
        Cluster data by first creating buckets and then clustering every bucket. Results will be sorted.
        """
        warnings.filterwarnings("ignore", message="numpy.ufunc size changed")
        self.prepare_data()

        if len(self.treatments.index) > 100:
            self.create_buckets()
            self.clusters = []
            for bucket in self.index_buckets:
                new_clusters = self.cluster_bucket(bucket)
                self.clusters += new_clusters
        else:
            bucket = list(range(0, len(self.treatments.index)))
            self.clusters = self.cluster_bucket(bucket)

        self.clusters = sorted(self.clusters, key=lambda c: (round(c.distance, 1), -c.max_occurrences_percentage), reverse=True)

    def get_clusters_as_dictionaries(self):
        return list(map(lambda c: c.get_cluster_as_dict(), self.clusters))

    def get_selected_clusters(self):
        return [cluster for cluster in self.clusters if cluster.selected]

    def select_cluster_with_id(self, id, select_as_bool):
        for cluster in self.clusters:
            if cluster.id == id:
                cluster.selected = select_as_bool
                return

    def change_replaceby(self, cluster_id, new_value):
        for cluster in self.clusters:
            if cluster.id == cluster_id:
                old_value = cluster.replaceby
                cluster.replaceby = new_value
                print("Cluster", cluster.id, "replaceby changed from", old_value, "to", new_value)

    def split_cluster(self, id, strings_to_move):
        new_id = self.counter
        self.counter += 1
        for cluster in self.clusters:
            if cluster.id == id:
                cluster.remove_strings(strings_to_move)
                index = self.clusters.index(cluster)
                new_cluster = Cluster(new_id, cluster.distance, self.original_values, strings_to_move)
                self.clusters.insert(index+1, new_cluster)
                cluster.recalculate_max_occurences_percentage()
                return new_cluster.get_cluster_as_dict()
