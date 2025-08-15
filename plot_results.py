import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import scienceplots

# Apply the IEEE plotting style
plt.style.use(['science', 'ieee'])

def create_plot(sheet_name, x_column, save_name):
    # Read data from Excel
    df = pd.read_excel(r'C:\Users\Zirak.Khan\Projects\Plastic Segmentation\Remote Sensing Paper\Remote Sensing Figures\HyperRoPE-SST_Results.xlsx', 
                      sheet_name=sheet_name)
    
    # Get unique datasets
    datasets = df['Dataset'].unique()
    
    # Setup figure
    fig, ax = plt.subplots(figsize=(3.5, 2.5))
    
    # Add a sparse, faded grid
    ax.grid(True, which='both', linestyle='--', linewidth=0.5, color='gray', alpha=0.3)
    
    # Different line styles for different datasets
    linestyles = ['-', '--', '-.']
    markers = ['o', 's', '^']
    
    # Plot each dataset
    for i, dataset in enumerate(datasets):
        dataset_df = df[df['Dataset'] == dataset].sort_values(by=x_column)
        ax.plot(dataset_df[x_column], dataset_df['OA'], 
                marker=markers[i],
                linestyle=linestyles[i],
                linewidth=1,
                markersize=3)
    
    # Set x-axis
    ax.set_xlabel(save_name, fontsize=8, labelpad=1, fontweight='bold')
    ax.tick_params(axis='x', labelsize=8)
    
    # Set y-axis with reduced labelpad to move label closer to the axis
    ax.set_ylabel('OA(%)', fontsize=8, labelpad=0, fontweight='bold')
    # Uncomment the following to fine-tune label position manually:
    # ax.yaxis.set_label_coords(-0.1, 0.5)
    
    ax.set_ylim(65, 100)
    ax.set_yticks(np.arange(65, 101, 5))
    ax.tick_params(axis='y', labelsize=8)
    
    # Adjust layout
    plt.tight_layout()
    
    # Save figure as an SVG file
    save_path = r'C:\Users\Zirak.Khan\Projects\Plastic Segmentation\Remote Sensing Paper'
    plt.savefig(f'{save_path}/{save_name}.svg', format='svg', bbox_inches='tight')
    plt.close()

# Create plots for different sheets
plot_configs = [
    ('Patch_Size', '2D_Patchsize', 'Patch Size'),
    # Add other sheets and their configurations here
    # ('Sheet_Name', 'Column_Name', 'Save_Name')
]

for sheet, column, save_name in plot_configs:
    create_plot(sheet, column, save_name)
