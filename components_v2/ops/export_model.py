from typing import NamedTuple


def export_model(data_base_path: str) -> NamedTuple(
    'export_model_outputs',
    [
        ('model_version', str)
    ]
):
    import datetime
    import json
    import os
    import shutil
    import subprocess
    from pathlib import Path


    configs = {
        'fs2_data_path': './fs2-data',
        'model_base_path': './models',
        'model_export_path': './model-store',
        'model_name': 'fastspeech2',
        'model_handler': './app/model_handler.py',
        'lexicon_path': './common/lexicons/librispeech-lexicon.txt',
        'metadata_path': './metadata',
        'global_optimal_checkpoint_stat_path': './global-optimal-checkpoint-status.json'
    }

    fs2_base_path = Path(data_base_path) / configs['fs2_data_path']
    model_base_path = fs2_base_path / configs['model_base_path']

    model_export_tmp_path = model_base_path / 'tmp'
    os.makedirs(model_export_tmp_path, exist_ok=True)

    model_export_path = model_base_path / configs['model_export_path']
    os.makedirs(model_export_path, exist_ok=True)
    # if not model_export_path.exists():
    #     os.makedirs(model_export_path)

    global_optimal_checkpoint_stat_path = fs2_base_path / configs['metadata_path'] / configs['global_optimal_checkpoint_stat_path']
    with open(f'{global_optimal_checkpoint_stat_path}', 'r') as f:
        global_optimal_checkpoint_stat = json.load(f)

    target_checkpoint_path = Path(global_optimal_checkpoint_stat['base_path']) \
        / global_optimal_checkpoint_stat['deployed_checkpoint']['path'] \

    lexicon_path = fs2_base_path / configs['lexicon_path']

    model_version = datetime.datetime.now().strftime("%y%m%d-%H%M")

    print(f'INFO: Export model from checkpoint "{target_checkpoint_path}".')
    subprocess.run(['torch-model-archiver',
                    '--model-name', configs["model_name"],
                    '--version', model_version,
                    '--serialized-file', str(target_checkpoint_path),
                    '--export-path', str(model_export_tmp_path),
                    '--handler', configs["model_handler"],
                    '--extra-files', lexicon_path])
    print(f'INFO: Successfully exported model as archive file.')

    shutil.move(model_export_tmp_path / (configs["model_name"] + ".mar"), 
                model_export_path / (configs["model_name"] + "-" + model_version + ".mar"))
    print(f'INFO: Successfully moved model archive file to model export path')

    shutil.rmtree(model_export_tmp_path)

    # subprocess.run(['torch-model-archiver',
    #             '--model-name', configs["model_name"] + '-' + model_version,
    #             '--version', model_version,
    #             '--serialized-file', str(target_checkpoint_path),
    #             '--export-path', str(model_export_path),
    #             '--handler', configs["model_handler"],
    #             '--extra-files', lexicon_path])

    from collections import namedtuple
    
    export_model_outputs = namedtuple(
        'export_model_outputs',
        ['model_version']
    )

    return export_model_outputs(model_version)


if __name__ == '__main__':
    export_model('/local-storage')
