import os
import pickle
import pandas as pd
from processing import preprocess

print("Starting pickle generation...")

files_to_remove = [
    'Files/movies_dict.pkl',
    'Files/movies2_dict.pkl',
    'Files/new_df_dict.pkl',
    'Files/similarity_tags_genres.pkl',
    'Files/similarity_tags_keywords.pkl',
    'Files/similarity_tags_tags.pkl',
    'Files/similarity_tags_tcast.pkl',
    'Files/similarity_tags_tcrew.pkl',
    'Files/similarity_tags_tprduction_comp.pkl'
]

# Remove LFS files if they exist and are small (LFS pointers)
for path in files_to_remove:
    if os.path.exists(path):
        size = os.path.getsize(path)
        if size < 500:  # LFS pointers are around 130 bytes
            print(f"Removing Git LFS pointer: {path} ({size} bytes)")
            os.remove(path)

# Generate movies, new_df, movies2 dataframes
print("Reading CSVs and preprocessing...")
movies, new_df, movies2 = preprocess.read_csv_to_df()

print("Saving movies_dict.pkl...")
with open('Files/movies_dict.pkl', 'wb') as f:
    pickle.dump(movies.to_dict(), f)

print("Saving movies2_dict.pkl...")
with open('Files/movies2_dict.pkl', 'wb') as f:
    pickle.dump(movies2.to_dict(), f)

print("Saving new_df_dict.pkl...")
with open('Files/new_df_dict.pkl', 'wb') as f:
    pickle.dump(new_df.to_dict(), f)

print("Generation complete!")
