import random
import numpy as np
import torch
from torch import nn


if __name__ == '__main__':
    loss = nn.MSELoss()
    input = torch.randn(3, 5, requires_grad=True)
    target = torch.randn(3, 5)
    output = loss(input, target)
    output.backward()
    print('aviv')
