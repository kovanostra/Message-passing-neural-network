#!/usr/bin/env bash
export DATASET_NAME='direct_neighbour_full_labels'
export DATA_DIRECTORY='data/'
export MODEL_DIRECTORY='model_checkpoints'
export RESULTS_DIRECTORY='results_grid_search'
export MODEL='RNN'
export DEVICE='cpu'
export EPOCHS='100'
export LOSS_FUNCTION='MSE'
export OPTIMIZER='Adagrad'
export BATCH_SIZE='100'
export VALIDATION_SPLIT='0.2'
export TEST_SPLIT='0.1'
export TIME_STEPS='1'
export VALIDATION_PERIOD='5'
