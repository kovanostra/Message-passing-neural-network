import logging
from typing import Dict, List, Tuple

import itertools
from torch.utils.data.dataloader import DataLoader

from src.domain.data_preprocessor import DataPreprocessor
from src.domain.graph import Graph
from src.domain.model_trainer import ModelTrainer
from src.repository.interface.repository import Repository


class GridSearch:
    def __init__(self,
                 training_data_repository: Repository,
                 model_trainer: ModelTrainer,
                 grid_search_dictionary: Dict) -> None:
        self.repository = training_data_repository
        self.model_trainer = model_trainer
        self.grid_search_dictionary = grid_search_dictionary

    def start(self) -> Dict:
        all_grid_search_configurations = self._get_all_grid_search_configurations()
        self.get_logger().info('Started Training')
        losses = {'training_loss': {},
                  'validation_loss': {},
                  'test_loss': {}}
        for configuration in all_grid_search_configurations:
            losses = self._search_configuration(configuration, losses)
        self.get_logger().info('Finished Training')
        return losses

    def _search_configuration(self, configuration: Tuple[Tuple], losses: Dict) -> Dict:
        configuration_dictionary = self._get_configuration_dictionary(configuration)
        training_data, validation_data, test_data, initialization_graph = self._prepare_dataset(
            configuration_dictionary)
        self.model_trainer.instantiate_attributes(initialization_graph, configuration_dictionary)
        losses = self._update_losses_with_configuration_id(configuration_dictionary, losses)
        for epoch in range(1, configuration_dictionary['epochs'] + 1):
            training_loss = self.model_trainer.do_train(training_data, epoch)
            losses['training_loss'][configuration_dictionary["configuration_id"]].update({epoch: training_loss})
            if epoch % configuration_dictionary["validation_period"] == 0:
                validation_loss = self.model_trainer.do_evaluate(validation_data, epoch)
                losses['validation_loss'][configuration_dictionary["configuration_id"]].update({epoch: validation_loss})
        test_loss = self.model_trainer.do_evaluate(test_data)
        losses['test_loss'][configuration_dictionary["configuration_id"]] = test_loss
        return losses

    @staticmethod
    def _update_losses_with_configuration_id(configuration_dictionary: Dict, losses: Dict) -> Dict:
        losses['training_loss'].update({configuration_dictionary["configuration_id"]: {}})
        losses['validation_loss'].update({configuration_dictionary["configuration_id"]: {}})
        losses['test_loss'].update({configuration_dictionary["configuration_id"]: {}})
        return losses

    @staticmethod
    def _get_configuration_dictionary(configuration: Tuple[Tuple]) -> Dict:
        configuration_dictionary = dict(((key, value) for key, value in configuration))
        configuration_id = 'configuration_id'
        for key, value in configuration_dictionary.items():
            configuration_id += "_" + str(value)
        configuration_dictionary.update({"configuration_id": configuration_id})
        return configuration_dictionary

    def _prepare_dataset(self, configuration_dictionary: Dict) -> Tuple[DataLoader, DataLoader, DataLoader, Graph]:
        raw_dataset = self.repository.get_all_features_and_labels_from_separate_files()
        training_data, validation_data, test_data = DataPreprocessor \
            .train_validation_test_split(raw_dataset,
                                         configuration_dictionary['batch_size'],
                                         configuration_dictionary['validation_split'],
                                         configuration_dictionary['test_split'])
        initialization_graph = DataPreprocessor.extract_initialization_graph(raw_dataset)
        return training_data, validation_data, test_data, initialization_graph

    def _get_all_grid_search_configurations(self) -> List[Tuple[Tuple]]:
        all_grid_search_configurations = []
        for key in self.grid_search_dictionary.keys():
            all_grid_search_configurations.append([(key, value) for value in self.grid_search_dictionary[key]])
        return list(itertools.product(*all_grid_search_configurations))

    @staticmethod
    def get_logger() -> logging.Logger:
        return logging.getLogger('message_passing_nn')