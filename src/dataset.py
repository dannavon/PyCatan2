import torch
from torch.utils.data import TensorDataset
from torch.utils.data import DataLoader


class Dataset:
    def __init__(self, batch_size, validation_ratio, test_ratio):
        self.samples_groups = [[]]
        self.labels_of_groups = []
        self.batch_size = batch_size
        self.validation_ratio = validation_ratio
        self.test_ratio = test_ratio

    def add_sample(self, sample):
        """
        :param sample: a game's state
        """
        self.samples_groups[-1].append(sample)

    def set_label(self, label):
        """
        should be called once after each game
        :param label: the label of the end of the game
        """

        self.labels_of_groups.append(label)
        self.samples_groups.append([])

    def get_datasets(self):
        x = torch.stack([val for group in self.samples_groups[:-1] for val in group])
        y = [[self.labels_of_groups[i]] * len(self.samples_groups[i]) for i in range(len(self.labels_of_groups))]
        y = torch.stack([val for group in y for val in group]).reshape((x.shape[0], -1))

        test_size = int(len(x) * self.test_ratio)
        valid_size = int(len(x) * self.validation_ratio)
        train_size = len(x) - test_size - valid_size

        x_train, y_train = x[:train_size, :], y[:train_size, :]

        x_valid, y_valid = x[train_size: train_size + valid_size, :], y[train_size: train_size + valid_size, :]

        x_test, y_test = x[len(x) - test_size:, :], y[len(x) - test_size:, :]

        return x_train, y_train, x_valid, y_valid, x_test, y_test

    def get_data_loaders(self):
        """
        :param batch_size: the size of the batch
        :return dl_train, dl_valid, dl_test:
        """
        X_train, y_train, X_valid, y_valid, X_test, y_test = self.get_datasets()

        dl_train, dl_valid, dl_test = [
            DataLoader(
                dataset=TensorDataset(
                    X_.to(torch.float32),
                    y_.to(torch.float32)
                ),
                shuffle=True,
                num_workers=0,
                batch_size=self.batch_size
            )
            for X_, y_ in [(X_train, y_train), (X_valid, y_valid), (X_test, y_test)]
        ]

        print(f'{len(dl_train.dataset)=}, {len(dl_valid.dataset)=}, {len(dl_test.dataset)=}')

        return dl_train, dl_valid, dl_test
