# ACDC experiments:

# baseline models
from experiments.segmentation.baseline.run_experiment import run as run_baseline_segmentation

# pre-training encoders
from experiments.segmentation.patch_encoder.run_experiment import run as run_pre_training_patch_segmentation
from experiments.segmentation.contrastive_loss_encoder.run_experiment import (
    run as run_pre_training_contrastive_segmentation,
)
from experiments.segmentation.rotation_encoder.run_experiment import (
    run as run_pre_training_rotation_segmentation,
)

# pre-trained models
from experiments.segmentation.pre_trained_patch.run_experiment import (
    run as run_pre_trained_patch_segmentation,
)
from experiments.segmentation.pre_trained_contrastive.run_experiment import (
    run as run_pre_trained_contrastive_segmentation,
)
from experiments.segmentation.pre_trained_rotation.run_experiment import (
    run as run_pre_trained_rotation_segmentation,
)

# adversarial models
from experiments.segmentation.adversarial_network_train_val_early.run_experiment import (
    run as run_adversarial_network_train_val_early,
)
from experiments.segmentation.adversarial_network_train_val_late.run_experiment import (
    run as run_adversarial_network_train_val_late,
)

################################################

# APTOS experiments:

# baseline models
from experiments.regression.baseline.run_experiment import run as run_efficientnet_baseline_regression

# pre-training models
from experiments.regression.contrastive_loss_encoder.run_experiment import (
    run as run_pre_training_contrastive_regression,
)
from experiments.regression.patch_encoder.run_experiment import (
    run as run_pre_training_patch_regression,
)
from experiments.regression.rotation_encoder.run_experiment import (
    run as run_pre_training_rotation_regression,
)

# adversarial models
from experiments.regression.adversarial_network_train_val_early.run_experiment import (
    run as run_efficientnet_adv_early_regression,
)
from experiments.regression.adversarial_network_train_val_late.run_experiment import (
    run as run_efficientnet_adv_late_regression,
)

# pre-trained models
from experiments.regression.pre_trained.run_experiment import run as run_pre_trained_regression

################################################


import click


@click.command()
@click.option(
    '--experiment',
    default='./experiments/detection/adversarial_network_train_val_early/config_RSNA_2_1.yml',
    help='',
)
@click.option('--gpu', default='7', help='')
def main(experiment, gpu):

    # ACDC
    #
    # baseline, without pre-train
    # run_baseline_segmentation(experiment='./experiments/baseline/config_ACDC_2.yml')
    # run_baseline_segmentation(experiment='./experiments/baseline/config_ACDC_4.yml')
    # run_baseline_segmentation(experiment='./experiments/baseline/config_ACDC_8.yml')
    # run_baseline_segmentation(experiment='./experiments/baseline/config_ACDC_UB.yml')
    #
    # pre-training
    # run_contrastive_pre_train_segmentation(experiment='./experiments/contrastive_loss_encoder/config_ACDC.yml',gpu='7')
    # run_rotation_pre_train_segmentation(experiment='./experiments/rotation_encoder/config_ACDC.yml',gpu='7')
    # run_patch_pre_train_segmentation(experiment='./experiments/patch_encoder/config_ACDC.yml',gpu='6')
    #
    # # pre-trained contrastive
    # run_pre_trained_contrastive_segmentation(experiment='./experiments/pre_trained_contrastive/config_ACDC_2.yml')
    # run_pre_trained_contrastive_segmentation(experiment='./experiments/pre_trained_contrastive/config_ACDC_4.yml')
    # run_pre_trained_contrastive_segmentation(experiment='./experiments/pre_trained_contrastive/config_ACDC_8.yml')
    #
    # # pre-trained rotation
    # run_pre_trained_rotation_segmentation(experiment='./experiments/pre_trained_rotation/config_ACDC_2.yml')
    # run_pre_trained_rotation_segmentation(experiment='./experiments/pre_trained_rotation/config_ACDC_4.yml')
    # run_pre_trained_rotation_segmentation(experiment='./experiments/pre_trained_rotation/config_ACDC_8.yml')
    #
    # # pre-trained patch
    # run_pre_trained_patch_segmentation(experiment='./experiments/pre_trained_patch/config_ACDC_2.yml')
    # run_pre_trained_patch_segmentation(experiment='./experiments/pre_trained_patch/config_ACDC_4.yml')
    # run_pre_trained_patch_segmentation(experiment='./experiments/pre_trained_patch/config_ACDC_8.yml')
    #
    # Single-stage self-supervised early flat
    # run_adversarial_network_train_val_early(
    #     experiment='./experiments/segmentation/adversarial_network_train_val_early/config_ACDC_2.yml'
    # )
    # run_adversarial_network_train_val_early(experiment='./experiments/segmentation/adversarial_network_train_val_early/config_ACDC_4.yml')
    # run_adversarial_network_train_val_early(experiment='./experiments/segmentation/adversarial_network_train_val_early/config_ACDC_8.yml')
    #
    # Single-stage self-supervised late flat
    # run_adversarial_network_train_val_late(experiment='./experiments/adversarial_network_train_val_late/config_ACDC_2.yml')
    # run_adversarial_network_train_val_late(experiment='./experiments/adversarial_network_train_val_late/config_ACDC_4.yml')
    # run_adversarial_network_train_val_late(experiment='./experiments/adversarial_network_train_val_late/config_ACDC_8.yml')

    ###########################################################################
    # APTOS

    # baseline models

    run_efficientnet_baseline_regression(experiment='./experiments/regression/baseline/config_aptos_8.yml', gpu='7')




    ###########################################################################

    return None


if __name__ == "__main__":
    main()
