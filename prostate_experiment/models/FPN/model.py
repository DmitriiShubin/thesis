# basic libs
import numpy as np
from tqdm import tqdm
import os
import pandas as pd

# pytorch
import torch
import torch.nn as nn
from torch.optim.lr_scheduler import ReduceLROnPlateau, CosineAnnealingLR
from torch.utils.tensorboard import SummaryWriter
from torch.utils.data import DataLoader

# custom modules
from metrics import Metric
from utils.torchsummary import summary
from loss_functions import Dice_loss
from utils.pytorchtools import EarlyStopping
from torch.nn.parallel import DataParallel as DP


# model
from models.FPN.structure import FPN


class Model:
    """
    This class handles basic methods for handling the model:
    1. Fit the model
    2. Make predictions
    3. Save
    4. Load
    """

    def __init__(self, n_channels, hparams, gpu, inference=False):

        self.hparams = hparams

        if inference:
            self.device = torch.device('cpu')
            self.model = FPN(hparams=self.hparams, n_channels=n_channels, n_classes=4).to(self.device)
        else:
            if torch.cuda.device_count() > 1:
                if len(gpu) > 0:
                    print("Number of GPUs will be used: ", len(gpu))
                    self.device = torch.device(f"cuda:{gpu[0]}" if torch.cuda.is_available() else "cpu")
                    self.model = FPN(hparams=self.hparams, n_channels=n_channels, n_classes=4).to(
                        self.device
                    )
                    self.model = DP(self.model, device_ids=gpu, output_device=gpu[0])
                else:
                    print("Number of GPUs will be used: ", torch.cuda.device_count() - 5)
                    self.device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
                    self.model = FPN(hparams=self.hparams, n_channels=n_channels, n_classes=4).to(
                        self.device
                    )
                    self.model = DP(self.model, device_ids=list(range(torch.cuda.device_count() - 5)))
            else:
                self.device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
                self.model = FPN(hparams=self.hparams, n_channels=n_channels, n_classes=4).to(self.device)
                print('Only one GPU is available')

        self.metric = Metric()
        self.num_workers = 32

        ########################## compile the model ###############################

        # define optimizer
        self.optimizer = torch.optim.Adam(params=self.model.parameters(), lr=self.hparams['lr'])

        self.loss = Dice_loss()  # nn.BCELoss(weight=None) #nn.NLLLoss()

        self.loss_s = nn.BCELoss(weight=None)
        self.alpha = self.hparams['model']['alpha']

        # define early stopping
        self.early_stopping = EarlyStopping(
            checkpoint_path=self.hparams['checkpoint_path']
            + '/checkpoint'
            + str(self.hparams['start_fold'])
            + '.pt',
            patience=self.hparams['patience'],
            delta=self.hparams['min_delta'],
            is_maximize=True,
        )

        # lr scheduler
        # self.scheduler = ReduceLROnPlateau(
        #     optimizer=self.optimizer,
        #     mode='max',
        #     factor=0.2,
        #     patience=3,
        #     verbose=True,
        #     threshold=self.hparams['min_delta'],
        #     threshold_mode='abs',
        #     cooldown=0,
        #     eps=0,
        # )
        self.scheduler = CosineAnnealingLR(self.optimizer, T_max=5, eta_min=1e-9, last_epoch=-1)

        self.seed_everything(42)

        self.scaler = torch.cuda.amp.GradScaler()

    def seed_everything(self, seed):
        np.random.seed(seed)
        os.environ['PYTHONHASHSEED'] = str(seed)
        torch.manual_seed(seed)

    def fit(self, train, valid):

        train_loader = DataLoader(
            train, batch_size=self.hparams['batch_size'], shuffle=True, num_workers=self.num_workers
        )
        valid_loader = DataLoader(
            valid, batch_size=self.hparams['batch_size'], shuffle=False, num_workers=self.num_workers
        )

        # tensorboard object
        writer = SummaryWriter()

        for epoch in range(self.hparams['n_epochs']):

            # trian the model
            self.model.train()
            avg_loss = 0.0
            avg_loss_adv = 0.0

            train_preds, train_true = torch.Tensor([]), torch.Tensor([])
            for (X_batch, y_batch, _, _) in tqdm(train_loader):
                y_batch = y_batch.float().to(self.device)
                X_batch = X_batch.float().to(self.device)

                self.optimizer.zero_grad()
                # get model predictions
                # TODO:
                pred = self.model(X_batch)

                X_batch = X_batch.float().cpu().detach()

                # process loss_1
                pred = pred.permute(0, 2, 3, 1)
                pred = pred.reshape(-1, pred.shape[-1])

                y_batch = y_batch.permute(0, 2, 3, 1)
                y_batch = y_batch.reshape(-1, y_batch.shape[-1])

                train_loss = self.loss(pred, y_batch)

                y_batch = y_batch.float().cpu().detach()
                pred = pred.float().cpu().detach()

                # calc loss
                avg_loss += train_loss.item() / len(train_loader)

                self.scaler.scale(train_loss).backward()  # train_loss.backward()
                # torch.nn.utils.clip_grad_norm_(self.model.parameters(), 1)
                # torch.nn.utils.clip_grad_norm_(self.model.parameters(), 1)
                # torch.nn.utils.clip_grad_value_(self.model.parameters(), 0.5)
                self.scaler.step(self.optimizer)  # self.optimizer.step()
                self.scaler.update()

                # train_true = torch.cat([train_true, y_batch], 0)
                # train_preds = torch.cat([train_preds, pred], 0)

            # calc triaing metric
            # train_preds = train_preds.numpy()
            # train_true = train_true.numpy()
            #
            # train_preds = np.argmax(train_preds, axis=1)
            # metric_train = self.metric.compute(labels=train_true, outputs=train_preds)

            # evaluate the model
            print('Model evaluation...')
            self.model.eval()
            val_preds, val_true = torch.Tensor([]), torch.Tensor([])
            avg_val_loss = 0.0
            with torch.no_grad():
                for X_batch, y_batch, _, _ in tqdm(valid_loader):
                    y_batch = y_batch.float().to(self.device)
                    X_batch = X_batch.float().to(self.device)

                    # TODO:
                    pred = self.model(X_batch)

                    X_batch = X_batch.float().cpu().detach()

                    pred = pred.permute(0, 2, 3, 1)
                    pred = pred.reshape(-1, pred.shape[-1])

                    y_batch = y_batch.permute(0, 2, 3, 1)
                    y_batch = y_batch.reshape(-1, y_batch.shape[-1])

                    avg_val_loss += self.loss(pred, y_batch).item() / len(valid_loader)

                    y_batch = y_batch.float().cpu().detach()
                    pred = pred.float().cpu().detach()

                    val_true = torch.cat([val_true, y_batch], 0)
                    val_preds = torch.cat([val_preds, pred], 0)

            # evalueate metric
            val_preds = val_preds.numpy()
            val_true = val_true.numpy()

            # val_preds = np.argmax(val_preds, axis=1)
            # val_true = np.argmax(val_true, axis=1)
            val_preds = np.argmax(val_preds, axis=1)
            val_true = np.argmax(val_true, axis=1)
            # val_preds = np.eye(4, dtype=np.float32)[val_preds.astype(np.int8)]
            # val_true = np.eye(4, dtype=np.float32)[val_true.astype(np.int8)]

            metric_val = self.metric.compute(labels=val_true, outputs=val_preds)

            self.scheduler.step(metric_val)  # avg_val_loss)
            res = self.early_stopping(score=metric_val, model=self.model)

            # print statistics
            if self.hparams['verbose_train']:
                print(
                    '| Epoch: ',
                    epoch + 1,
                    '| Train_loss main: ',
                    avg_loss,
                    '| Val_loss main: ',
                    avg_val_loss,
                    '| Metric_val: ',
                    metric_val,
                    '| Current LR: ',
                    self.__get_lr(self.optimizer),
                )

            # # add history to tensorboard
            writer.add_scalars(
                'Loss',
                {'Train_loss': avg_loss, 'Val_loss': avg_val_loss},
                epoch,
            )

            # writer.add_scalars('Metric', {'Metric_train': metric_train, 'Metric_val': metric_val}, epoch)
            writer.add_scalars('Metric', {'Metric_val': metric_val}, epoch)

            if res == 2:
                print("Early Stopping")
                print(f'global best max val_loss model score {self.early_stopping.best_score}')
                break
            elif res == 1:
                print(f'save global val_loss model score {metric_val}')

        writer.close()

        self.model = self.early_stopping.load_best_weights()

        return True

    def predict(self, X_test):

        # evaluate the model
        self.model.eval()

        test_loader = torch.utils.data.DataLoader(
            X_test, batch_size=self.hparams['batch_size'], shuffle=False, num_workers=self.num_workers
        )  # ,collate_fn=train.my_collate

        test_preds = torch.Tensor([])
        test_val = torch.Tensor([])
        print('Start generation of predictions')
        with torch.no_grad():
            for i, (X_batch, y_batch, _, _) in enumerate(tqdm(test_loader)):
                X_batch = X_batch.float().to(self.device)

                # TODO:
                # pred = self.model([X_batch, X_s_batch])
                pred = self.model(X_batch)
                X_batch = X_batch.float().cpu().detach()

                test_preds = torch.cat([test_preds, pred.cpu().detach()], 0)
                test_val = torch.cat([test_val, y_batch.cpu().detach()], 0)

        return test_val.numpy(), test_preds.numpy()

    def model_save(self, model_path):
        torch.save(self.model.state_dict(), model_path)
        # self.model.module.state_dict(), PATH
        # torch.save(self.model, model_path)
        return True

    def model_load(self, model_path):
        self.model.load_state_dict(torch.load(model_path, map_location=self.device))
        return True

    def model_load_old(self, model_path):
        self.model = torch.load(model_path, map_location=self.device)
        return True

    ################## Utils #####################

    def __get_lr(self, optimizer):
        for param_group in optimizer.param_groups:
            return param_group['lr']
