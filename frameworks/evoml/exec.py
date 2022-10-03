import logging
import math
import os

# from amlb import __version__
from amlb.benchmark import TaskConfig
from amlb.data import Dataset
from amlb.datautils import reorder_dataset
from amlb.results import NoResultError, save_predictions
from amlb.utils import dir_of, path_from_split, run_cmd, split_path, Timer
from frameworks.shared.callee import call_run, output_subdir, result
from frameworks.shared.utils import Timer, is_sparse
import pprint
import evoml_client as ec
from evoml_client.trial_conf_models import BudgetMode
import time

log = logging.getLogger(__name__)


def run(dataset, config):
    log.info(f"\n**** EVOML [v1.0]****\n")

    is_classification = config.type == 'classification'
    # Mapping of benchmark metrics to TPOT metrics
    metrics_mapping = dict(
        acc='accuracy',
        auc='roc_auc',
        f1='f1',
        logloss='neg_log_loss',
        mae='neg_mean_absolute_error',
        mse='neg_mean_squared_error',
        msle='neg_mean_squared_log_error',
        r2='r2',
        rmse='neg_mean_squared_error',  # TPOT can score on mse, as app computes rmse independently on predictions
    )
    scoring_metric = metrics_mapping[config.metric] if config.metric in metrics_mapping else None
    if scoring_metric is None:
        raise ValueError("Performance metric {} not supported.".format(config.metric))

    X_train = dataset.train.X
    y_train = dataset.train.y
    y_train = y_train.flatten()

    # training_params = {k: v for k, v in config.framework_params.items() if not k.startswith('_')}
    n_jobs = config.framework_params.get('_n_jobs', config.cores)  # useful to disable multicore, regardless of the dataset config
    # config_dict = config.framework_params.get('_config_dict', "TPOT sparse" if is_sparse(X_train) else None)

    log.info('Running evoml with a maximum time of %ss on %s cores, optimizing %s.',
             config.max_runtime_seconds, n_jobs, scoring_metric)
    # runtime_min = (config.max_runtime_seconds/60)

    ec.init(username="admintest@turintech.ai", password="admintestadmintest", env="dev",
            pypi_username="evomlcl", pypi_password="x4v7MPMKyZ6JF32")

    log.info("Evoml_client: Logged in.")
    if is_classification:
        log.info("Creating config for classification.")
        trial_conf = ec.TrialConfig.with_default(
            task=ec.MlTask.classification, loss_funcs=["Accuracy"], budget_mode=BudgetMode.fast
        )
    else:
        log.info("Creating config for regression.")
        trial_conf = ec.TrialConfig.with_default(
            task=ec.MlTask.regression, loss_funcs=["regression-mse"], budget_mode=BudgetMode.fast
        )

    trial, _ = ec.Trial.from_numpy_xy(
        data_x=X_train,
        data_y=y_train,
        data_name="evoml benchmark test",
        trial_name="digits classification",
        config=trial_conf,
    )
    log.info("Trial is successfully created and the status is {}. Upload will start immediately.".format(trial.get_state()))
    #
    # log.info("Trial has started. Status is {}".format(trial.get_state()))

    trial.run(timeout=1200)

    # TODO: will add this when evoml_client fix for oversamplig is done
    # for i in range(0, 10):
    #     while True:
    #         try:
    #             print("TRY number: {}..........".format(i))
    #             clf = trial.get_best()
    #         except Exception as e:
    #             time.sleep(10)
    #             if (i == 10):
    #                 raise e
    #             continue
    #         break

    clf = trial.get_best()
    log.info("Best model is now found. Starting build immediately.")
    clf.build_model()

    log.info('Predicting on the test set.')

    X_test = dataset.test.X
    y_test = dataset.test.y
    with Timer() as predict:
        predictions = clf.predict(X_test)
    try:
        probabilities = clf.predict_proba(X_test) if is_classification else None
    except RuntimeError:
        # RuntimeError if the optimized pipeline does not support `predict_proba`.
        probabilities = "predictions"  # encoding is handled by caller in `__init__.py`

    # save_artifacts(tpot, config)

    return result(output_file=config.output_predictions_file,
                  predictions=predictions,
                  truth=y_test,
                  probabilities=probabilities,
                  target_is_encoded=is_classification,
                  # models_count=len(tpot.evaluated_individuals_),
                  # models_count=1,
                  # training_duration=training.duration,
                  predict_duration=predict.duration)


def save_artifacts(estimator, config):
    try:
        log.debug("All individuals :\n%s", list(estimator.evaluated_individuals_.items()))
        models = estimator.pareto_front_fitted_pipelines_
        hall_of_fame = list(zip(reversed(estimator._pareto_front.keys), estimator._pareto_front.items))
        artifacts = config.framework_params.get('_save_artifacts', False)
        if 'models' in artifacts:
            models_file = os.path.join(output_subdir('models', config), 'models.txt')
            with open(models_file, 'w') as f:
                for m in hall_of_fame:
                    pprint.pprint(dict(
                        fitness=str(m[0]),
                        model=str(m[1]),
                        pipeline=models[str(m[1])],
                    ), stream=f)
    except Exception:
        log.debug("Error when saving artifacts.", exc_info=True)


if __name__ == '__main__':
    call_run(run)

