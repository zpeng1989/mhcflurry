# Copyright (c) 2015. Mount Sinai School of Medicine
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

from collections import OrderedDict

import numpy as np
from sklearn.metrics import roc_auc_score

import mhcflurry
from mhcflurry.common import normalize_allele_name
from mhcflurry.data_helpers import indices_to_hotshot_encoding


def encode_allele_dataset(
        allele_dataset,
        max_ic50,
        binary_encoding=False):
    """
    Parameters
    ----------
    allele_dataset : AlleleDataset
        Named tuple with fields "X" and "ic50"
    max_ic50 : float
        Largest IC50 value predictor should return
    binary_encoding : bool (default = False)
        If True, use a binary 1-of-k encoding of amino acids, otherwise
        expect a vector embedding to use integer indices.

    Returns (X, Y_log_ic50, binder_label)
    """
    X_allele = allele_dataset.X
    ic50_allele = allele_dataset.ic50
    if binary_encoding:
        X_allele = indices_to_hotshot_encoding(X_allele, n_indices=20)
    Y_allele = 1.0 - np.minimum(1.0, np.log(ic50_allele) / np.log(max_ic50))
    return (X_allele, Y_allele, ic50_allele)


def encode_allele_datasets(
        allele_datasets,
        max_ic50,
        binary_encoding=False):
    """
    Parameters
    ----------
    allele_dataset : AlleleDataset
        Named tuple with fields "X" and "ic50"
    max_ic50 : float
        Largest IC50 value predictor should return
    binary_encoding : bool (default = False)
        If True, use a binary 1-of-k encoding of amino acids, otherwise
        expect a vector embedding to use integer indices.

    Returns three dictionarys
        - mapping from allele name to X (features)
        - mapping from allele name to Y_log_ic50 (continuous outputs)
        - mapping from allele name to binder_label (binary outputs)
    """
    X_dict = OrderedDict()
    Y_log_ic50_dict = OrderedDict([])
    ic50_dict = OrderedDict([])
    for (allele_name, dataset) in allele_datasets.items():
        allele_name = normalize_allele_name(allele_name)
        (X, Y_log_ic50, Y_ic50) = encode_allele_dataset(
            dataset,
            max_ic50=max_ic50,
            binary_encoding=binary_encoding)
        X_dict[allele_name] = X
        Y_log_ic50_dict[allele_name] = Y_log_ic50
        ic50_dict[allele_name] = Y_ic50
    return (X_dict, Y_log_ic50_dict, ic50_dict)


def f1_score(true_label, label_pred):
    tp = (true_label & label_pred).sum()
    fp = ((~true_label) & label_pred).sum()
    fn = (true_label & (~label_pred)).sum()
    recall = (tp / float(tp + fn)) if (tp + fn) > 0 else 0.0
    precision = (tp / float(tp + fp)) if (tp + fp) > 0 else 0.0
    if (precision + recall) > 0:
        return (2 * precision * recall) / (precision + recall)
    else:
        return 0.0


def score_predictions(predicted_log_ic50, true_label, max_ic50):
    """Computes accuracy, AUC, and F1 score of predictions"""
    auc = roc_auc_score(true_label, predicted_log_ic50)
    ic50_pred = max_ic50 ** (1.0 - predicted_log_ic50)
    label_pred = (ic50_pred <= 500)
    same_mask = true_label == label_pred
    accuracy = np.mean(same_mask)
    f1 = f1_score(true_label, label_pred)
    return accuracy, auc, f1


def train_model_and_return_scores(
        model,
        X_train,
        log_ic50_train,
        X_test,
        binder_label_test,
        n_training_epochs,
        minibatch_size,
        max_ic50):
    model.fit(
        X_train,
        log_ic50_train,
        nb_epoch=n_training_epochs,
        verbose=0,
        batch_size=minibatch_size)
    pred = model.predict(X_test).flatten()
    accuracy, auc, f1_score = score_predictions(
        predicted_log_ic50=pred,
        true_label=binder_label_test,
        max_ic50=max_ic50)
    return (accuracy, auc, f1_score)


def create_and_evaluate_model_with_synthetic_data(
        X,
        Y,
        weights_synth,
        weights_actual,
        n_training_epochs,
        dropout,
        embedding_dim_size,
        hidden_layer_size):
    model = mhcflurry.feedforward.make_embedding_network(
        peptide_length=9,
        embedding_input_dim=20,
        embedding_output_dim=4,
        layer_sizes=[4],
        activation="tanh",
        init="lecun_uniform",
        loss="mse",
        output_activation="sigmoid",
        dropout_probability=0.0,
        optimizer=None,
        learning_rate=0.001)
    total_synth_weights = weights_synth.sum()
    total_actual_weights = weights_actual.sum()
    for epoch in range(n_training_epochs):
        # weights for synthetic points can be shrunk as:
        #  ~ 1 / (1+epoch)**2
        # or
        # 2.0 ** -epoch
        decay_factor = 2.0 ** -epoch
        # if the contribution of synthetic samples is less than a
        # thousandth of the actual data, then stop using it
        synth_contribution = total_synth_weights * decay_factor
        if synth_contribution < total_actual_weights / 1000:
            print("Epoch %d, using only actual data" % (epoch + 1,))
            model.fit(
                X_actual,
                Y_actual,
                sample_weight=weights_actual,
                nb_epoch=1)
        else:
            print("Epoch %d, synth decay factor = %f" % (
                epoch + 1, decay_factor))
            weights[n_actual_samples:] = weights_synth * decay_factor
            model.fit(X, Y, sample_weight=weights, nb_epoch=1)
        Y_pred = model.predict(X_actual)
        print("Training MSE %0.4f" % ((Y_actual - Y_pred) ** 2).mean())



