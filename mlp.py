from torch import Tensor, nn
from typing import Union, Sequence


ACTIVATIONS = {
    "relu": nn.ReLU,
    "tanh": nn.Tanh,
    "sigmoid": nn.Sigmoid,
    "lrelu": nn.LeakyReLU,
    "none": nn.Identity,
    None: nn.Identity,
}


class MLP(nn.Module):
    """
    A general-purpose MLP.
    """

    def __init__(
        self, in_dim: int, dims: Sequence[int], nonlins: Sequence[Union[str, nn.Module]]
    ):
        """
        :param in_dim: Input dimension.
        :param dims: Hidden dimensions, including output dimension.
        :param nonlins: Non-linearities to apply after each one of the hidden
            dimensions.
            Can be either a sequence of strings which are keys in the ACTIVATIONS
            dict, or instances of nn.Module (e.g. an instance of nn.ReLU()).
            Length should match 'dims'.
        """
        super().__init__()
        assert len(nonlins) == len(dims)
        self.in_dim = in_dim
        self.out_dim = dims[-1]

        layers = []
        all_d = [in_dim, *dims]
        for i in range(len(dims)):
            layers += [nn.Linear(all_d[i], all_d[i+1])]
            if type(nonlins[i]) == str or nonlins[i] is None:
                act = ACTIVATIONS[nonlins[i]]
                actl = act()
            else:
                actl = nonlins[i]
            layers += [actl]
        self.mlp_layers = nn.Sequential(*layers[:])

    def forward(self, x: Tensor) -> Tensor:
        """
        :param x: An input tensor, of shape (N, D) containing N samples with D features.
        :return: An output tensor of shape (N, D_out) where D_out is the output dim.
        """

        y_pred = self.mlp_layers(x)
        return y_pred
