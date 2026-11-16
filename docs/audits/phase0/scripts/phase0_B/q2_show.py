import pandas as pd
pd.set_option('display.width',250); pd.set_option('display.max_columns',80); pd.set_option('display.max_rows',500)
K=['P','S1','S3a','S3b','S3c','S4a','S4b','S5a','S5b','S5c']
w = pd.read_csv('family_cells.csv', low_memory=False)
w = w[['file','cell','counted','base','label']+K]
w.to_csv('family_cells_small.csv', index=False)
print(w.round(3).to_string())
dw = pd.read_csv('design_table_wide.csv')
print(dw[['subject','family','base','label']+K].round(3).to_string())
