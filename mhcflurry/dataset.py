# Copyright (c) 2016. Mount Sinai School of Medicine
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from __future__ import (
    print_function,
    division,
    absolute_import,
)
from collections import OrderedDict
from itertools import groupby

import numpy as np
from six import string_types, integer_types
from typechecks import require_iterable_of, require_instance

from .dataset_helpers import (
    prepare_peptides_array,
    prepare_alleles_array,
    prepare_ic50_values_array,
    transform_ic50_values_into_regression_outputs,
    infer_csv_separator
    combine_multiple_peptide_ic50_measurements,
    load_dataframe,
)
from .class1_allele_specific_hyperparameters import MAX_IC50
from .common import normalize_allele_name


class SingleAlleleDataset(object):
    """

AlleleData = namedtuple(
    "AlleleData",
    [
        "X_index",    # index-based featue encoding of fixed length peptides
        "X_binary",  # binary encoding of fixed length peptides
        "Y",     # regression encoding of IC50 (log scaled between 0..1)
        "peptides",  # list of fixed length peptide string
        "ic50",      # IC50 value associated with each entry
        "original_peptides",  # original peptides may be of different lengths
        "original_lengths",   # len(original_peptide)
        "substring_counts",   # how many substrings were extracted from
                              # each original peptide string
        "weights",    # 1.0 / count
    ])
    """
    def __init__(
            self,
            allele_name,
            peptides,
            ic50_values,
            weights=None,
            max_ic50=50000,
            kmer_size=9,
            combine_redundant_measurements=False):
        """
        Parameters
        ----------
        allele_name : str
            Name of the allele for which these pMHC affinity measurements
            were made.

        peptides : sequence of str
            Sequences of peptides evaluated.

        ic50_values : sequence of float
            Affinities between peptides and this allele.

        max_ic50 : float
            Used for converting to rescaled values between 0 and 1
            (everything greater than the max IC50 value gets mapped to 0)

        kmer_size : int
            When building fixed length representations of the peptides,
            which length encoding to use.

        combine_redundant_measurements : bool
            If the same peptide has two measured values, should they
            both be included in the dataset or should they be combined
            into the geometric mean of their IC50 values?
        """
        self.allele_name = normalize_allele_name(allele_name)
        self.max_ic50 = max_ic50
        self.kmer_size = kmer_size
        self.original_peptides = prepare_peptides_array(peptides=peptides)
        self.original_ic50_values = prepare_ic50_values_array(
            ic50_values=ic50_values,
            required_count=len(self.peptides))
        # since data may contain multiple measurements for the same pMHC,
        # combine them using the geometric mean of the measured IC50 values
        self.peptides, self.ic50_values = \
            combine_multiple_peptide_ic50_measurements(
                peptides=self.original_peptides,
                ic50_values=self.original_ic50_values)

    def __len__(self):
        """
        Returns number of distinct peptides in this dataset
        (not k-mers extracted from peptides)
        """
        return len(self.peptides)

    @property
    def peptide_to_ic50_dict(self):
        """
        Returns dictionary mapping each peptide to an IC50 value.
        """
        return OrderedDict([
            (p, ic50) for (p, ic50) in zip(self.peptides, self.ic50_values)])

    @property
    def peptide_to_rescaled_affinity_dict(self):
        """
        Returns dictionary mapping each
    @property
    def kmers(self):


class MultipleAlleleDataset(object):
    """
    Dataset consisting with pMHC affinities for multiple alleles.
    """
    def __init__(self, single_allele_datasets):
        """
        Parameters
        ----------
        single_allele_datasets : dict
            Dictionary mapping allele names to SingleAlleleDataset objects.
        """
        self.single_allele_datasets = {
            normalize_allele_name(k): v
            for (k, v) in single_allele_datasets.items()
        }


    def allele_names(self):
        return list(sorted(single_allele_datasets.keys()))

    def __getitem__(self, allele_name):
        """
        Use this object as a dict by looking up a SingleAlleleDataset from
        its allele name.
        """
        allele_name = normalize_allele_name(allele_name)
        return self.single_allele_datasets[allele_name]

    def items(self):
        """
        Generates sequence of pair containing (allele_name, SingleAlleleDataset)
        """
        for allele_name in self.allele_names():
            yield (allele_name, self[allele_name])

    def counts(self):
        """
        Returns the number of pMHC binding values for each allele.
        """
        return OrderedDict( (k, len(v)) for (k, v) in self.items())

    def to_dataframe(self):
        columns = [
            ("allele", []),
            ("peptide", []),
            ("ic50", []),
        ]
        columns_dict = OrderedDict(columns)
        for i, kmer in self.kmers:
            original_peptide =
        df["allele"] = []
        df["peptide"] = self.peptides
        df["ic50"] = self.ic50_values

        return pd.DataFrame(columns_dict)
        return df

    def to_dense_matrix(self):
        pass

    def impute_missing_values(self):
        pass

    def missing_mask_array(self):
        pass


    def missing_mask_dict(self):
        """
        Returns dictionary from allele names to boolean masks of missing values.
        """
        pass

    def filter_by_allele_dict(self):


    @classmethod
    def from_csv(cls):
        df = load_
        return cls(peptides=None, alleles=None, ic50_values=None)

    @classmethpd
    def from_iedb_csv(cls):
        return cls(peptides=None, alleles=None, ic50_values=None)

