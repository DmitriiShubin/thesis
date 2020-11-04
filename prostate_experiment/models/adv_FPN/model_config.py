import os

hparams = {}
# training params
hparams['n_epochs'] = 2
hparams['lr'] = 0.001
hparams['batch_size'] = 2
hparams['verbose_train'] = True

# early stopping settings
hparams['min_delta'] = 0.001  # thresold of improvement
hparams['patience'] = 20  # wait for n epoches for emprovement
hparams['n_fold'] = 5  # number of folds for cross-validation
hparams['verbose'] = True  # print score or not
hparams['start_fold'] = 0
hparams['model_name'] = 'Adv FPN'

# directories
hparams['model_path'] = './data/model_weights'
hparams['model_path'] += '/adv_FPN_model'
hparams['checkpoint_path'] = hparams['model_path'] + '/checkpoint'

for path in [hparams['model_path'], hparams['checkpoint_path']]:
    os.makedirs(path, exist_ok=True)

# dictionary of hyperparameters
structure_hparams = dict()
# global dropout rate
structure_hparams['dropout'] = 0.2
structure_hparams['alpha'] = 0.1
# number of filers for the models
structure_hparams['kernel_size'] = 3  # must be odd
structure_hparams['n_filters_input'] = 128

hparams['model'] = structure_hparams