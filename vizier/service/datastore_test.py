"""Tests for vizier.service.datastore."""

from vizier.service import datastore
from vizier.service import resources
from vizier.service import test_util

from absl.testing import absltest


class DatastoreTest(absltest.TestCase):

  def setUp(self):
    self.owner_id = 'my_username'
    self.study_id = '123123123'
    self.client_id = 'client_0'
    self.datastore = datastore.NestedDictRAMDataStore()
    self.example_study = test_util.generate_study(self.owner_id, self.study_id)
    self.example_trials = test_util.generate_trials([1, 2],
                                                    owner_id=self.owner_id,
                                                    study_id=self.study_id)
    self.example_suggestion_operations = test_util.generate_suggestion_operations(
        [1, 2, 3, 4], self.owner_id, self.client_id)
    self.example_early_stopping_operations = test_util.generate_early_stopping_operations(
        [1, 2], self.owner_id, self.study_id)
    super().setUp()

  def test_study(self):
    self.datastore.create_study(self.example_study)
    output_study = self.datastore.load_study(self.example_study.name)
    self.assertEqual(output_study, self.example_study)

    owner_name = resources.StudyResource.from_name(
        self.example_study.name).owner_resource.name
    list_of_one_study = self.datastore.list_studies(owner_name)
    self.assertLen(list_of_one_study, 1)
    self.assertEqual(list_of_one_study[0], self.example_study)

    self.datastore.delete_study(self.example_study.name)
    empty_list = self.datastore.list_studies(owner_name)
    self.assertEmpty(empty_list)

  def test_trial(self):
    self.datastore.create_study(self.example_study)
    for trial in self.example_trials:
      self.datastore.create_trial(trial)

    self.assertLen(
        self.example_trials,
        self.datastore.max_trial_id(
            resources.StudyResource(self.owner_id, self.study_id).name))

    list_of_trials = self.datastore.list_trials(self.example_study.name)
    self.assertLen(list_of_trials, len(self.example_trials))
    self.assertEqual(list_of_trials, self.example_trials)

    output_trial = self.datastore.get_trial(self.example_trials[0].name)
    self.assertEqual(output_trial, self.example_trials[0])

    self.datastore.delete_trial(self.example_trials[0].name)
    leftover_trials = self.datastore.list_trials(self.example_study.name)
    self.assertEqual(leftover_trials, self.example_trials[1:])

  def test_suggestion_operation(self):
    self.datastore.create_study(self.example_study)
    for operation in self.example_suggestion_operations:
      self.datastore.create_suggestion_operation(operation)

    self.assertLen(
        self.example_suggestion_operations,
        self.datastore.max_suggestion_operation_number(
            resources.OwnerResource(self.owner_id).name, self.client_id))

    list_of_operations = self.datastore.list_suggestion_operations(
        resources.OwnerResource(self.owner_id).name, self.client_id)
    self.assertEqual(list_of_operations, self.example_suggestion_operations)

    output_operation = self.datastore.get_suggestion_operation(
        resources.SuggestionOperationResource(
            self.owner_id, self.client_id, operation_number=1).name)
    self.assertEqual(output_operation, self.example_suggestion_operations[0])

  def test_early_stopping_operation(self):
    self.datastore.create_study(self.example_study)

    for trial in self.example_trials:
      self.datastore.create_trial(trial)

    for operation in self.example_early_stopping_operations:
      self.datastore.create_early_stopping_operation(operation)

    output_operation = self.datastore.get_early_stopping_operation(
        resources.EarlyStoppingOperationResource(self.owner_id, self.study_id,
                                                 1).name)
    self.assertEqual(output_operation,
                     self.example_early_stopping_operations[0])


if __name__ == '__main__':
  absltest.main()
