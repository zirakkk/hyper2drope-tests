import os
import argparse
import torch
import numpy as np
import json
from data.data_loader import MultiFileHSIDataLoader
from utils.visualization import save_classification_maps
from utils.trainer import get_trainer
from torch.utils.data import DataLoader, Dataset
from configs.config import DEFAULT_RES_SAVE_PATH_PREFIX
from configs.config import CHECKPOINT_PATH_PREFIX
from configs.config import CONFIG_PATH_PREFIX

def load_config(config_file):
    with open(os.path.join(CONFIG_PATH_PREFIX, config_file), 'r') as fin:
        return json.load(fin)
    

def run_inference(config_file: str, dataset_name: str, model_name: str, checkpoint_path: str):
    """Run inference using existing model checkpoint and generate classification maps."""
    # Load configuration (reusing from main.py)
    org_params = load_config(config_file)
    param = {
        'data': {
            **org_params['datasets'][dataset_name],
            **org_params['common']   
        },
        'net': org_params['net'],
        'train': org_params['train']
    }

    # Initialize data loader using existing MultiFileHSIDataLoader
    data_loader = MultiFileHSIDataLoader(param)
    train_loader, valid_loader, test_loader = data_loader.generate_torch_dataset()
    
    # Combine train and test datasets
    combined_dataset = torch.utils.data.ConcatDataset([
        train_loader.dataset,
        test_loader.dataset
    ])
    
    # Create combined loader
    combined_loader = DataLoader(
        combined_dataset,
        batch_size=param['data']['batch_size'],
        shuffle=False  # Keep False to maintain index order
    )
    
    trainer = get_trainer(param)
    eval_res, gt_labels, pred_labels = trainer.final_eval(combined_loader, checkpoint_path)
    
    # Generate and save classification maps
    save_dir = os.path.join('classification_maps', dataset_name)
    os.makedirs(save_dir, exist_ok=True)

    # Get original image shape from the first image
    original_shape = data_loader.images[0].shape[:2]  # (height, width)
    
    # Create empty classification maps
    pred_map = np.zeros(original_shape, dtype=np.int32)
    gt_map = np.zeros(original_shape, dtype=np.int32)
    
    # Map predictions back to their spatial positions using train & test indices
    all_indices = {}
    # First add training indices
    for idx, pos in data_loader.index2pos_train[0].items():
        all_indices[idx] = pos
    # Then add test indices with adjusted index
    offset = len(data_loader.index2pos_train[0])
    for idx, pos in data_loader.index2pos_test[0].items():
        all_indices[idx + offset] = pos
        
    for idx, (i, j) in all_indices.items():
        if idx < len(pred_labels):  # Ensure we don't exceed predictions array
            pred_map[i, j] = pred_labels[idx] + 1  # Add 1 since predictions are 0-based
            gt_map[i, j] = gt_labels[idx] + 1
    
    save_classification_maps(dataset_name, model_name, pred_map, gt_map, save_dir='classification_maps')


def main():
    parser = argparse.ArgumentParser(description="Generate classification maps for HSI datasets")
    parser.add_argument("--config", type=str, default="hyper2Drope.json", 
                      choices=["hyper2Drope.json", "lsga_vit.json", "hit.json", "spectralformer.json", "sqsformer.json"])
    parser.add_argument("--dataset", type=str, default="IndianPine",
                      choices=["IndianPine", "Pavia", "Houston"])
    parser.add_argument("--model", type=str, default="Hyper2DRoPE",
                      choices=["Hyper2DRoPE", "LSGA_ViT", "HiT", "SpectralFormer", "SQSFormer"])
    parser.add_argument("--mode", choices=['single', 'all'], default='all',
                      help="Run for a single model/dataset or all combinations")
    args = parser.parse_args()

    if args.mode == 'single':
        # Get checkpoint path
        checkpoint_path = os.path.join(CHECKPOINT_PATH_PREFIX, f"{args.dataset}_{args.model}__best.pth")
        if not os.path.exists(checkpoint_path):
            raise FileNotFoundError(f"Checkpoint not found: {checkpoint_path}")
        
        # Run inference and generate maps
        run_inference(args.config, args.dataset, args.model, checkpoint_path)
    
    else:  # all mode
        datasets = ["IndianPine", "Pavia", "Houston"]
        models = ["Hyper2DRoPE", "LSGA_ViT", "HiT", "SpectralFormer", "SQSFormer"]
        configs = {
            "Hyper2DRoPE": "hyper2Drope.json",
            "LSGA_ViT": "lsga_vit.json",
            "HiT": "hit.json",
            "SpectralFormer": "spectralformer.json",
            "SQSFormer": "sqsformer.json"
        }

        for dataset in datasets:
            for model in models:
                checkpoint_path = os.path.join(CHECKPOINT_PATH_PREFIX, f"{dataset}_{model}_best.pth")
                if os.path.exists(checkpoint_path):
                    try:
                        print(f"\nProcessing {dataset} with {model}...")
                        run_inference(configs[model], dataset, model, checkpoint_path)
                        print(f"Completed {dataset} with {model}")
                    except Exception as e:
                        print(f"Error processing {dataset} with {model}: {str(e)}")

if __name__ == "__main__":
    main()