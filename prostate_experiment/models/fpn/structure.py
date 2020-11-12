import torch
import torch.nn as nn
from time import time
import numpy as np
from segmentation_models_pytorch import FPN as smp_FPN



class OutConv(nn.Module):
    def __init__(self, in_channels, out_channels):
        super(OutConv, self).__init__()
        self.conv = nn.Conv2d(in_channels, out_channels, kernel_size=1)

    def forward(self, x):
        return self.conv(x)


class FPN(smp_FPN):
    def __init__(self, hparams, n_channels, n_classes):
        super(FPN, self).__init__(
            encoder_name='resnet18',
            encoder_depth=3,
            encoder_weights=None,
            decoder_segmentation_channels=hparams['model']['n_filters_input'],
            decoder_dropout=hparams['model']['dropout'],
            in_channels=1,
            classes=1
        )

        self.conv2d = nn.Conv2d(
            hparams['model']['n_filters_input'],
            hparams['model']['n_filters_input'],
            kernel_size=1,
            padding=0,
        )
        self.upsampling = nn.UpsamplingBilinear2d(scale_factor=2)

        self.hparams = hparams['model']
        self.n_channels = n_channels
        self.n_classes = n_classes

        self.outc = OutConv(self.hparams['n_filters_input'], n_classes)



    def forward(self, x):
        """Sequentially pass `x` trough model`s encoder, decoder and heads"""

        features = self.encoder(x)
        x = self.decoder(*features)

        x = self.conv2d(x)
        #x = self.upsampling(x)

        x = self.outc(x)

        x = torch.softmax(x, dim=1)

        return x