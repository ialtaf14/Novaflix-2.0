## 📸 Project Preview

Below is a preview of the Novaflix Movie Recommendation System interface.

<img width="1919" height="880" alt="Novaflix (20)" src="https://github.com/user-attachments/assets/d8d7f274-bde5-4439-b02e-3dbd562a50d0" />
<img width="1828" height="916" alt="Novaflix (19)" src="https://github.com/user-attachments/assets/0d67d10d-5ce6-48a6-8df6-37b068df2dd9" />
<img width="1876" height="823" alt="Novaflix (18)" src="https://github.com/user-attachments/assets/b82d93e0-e6fe-452e-9311-ba326aac8d63" />
<img width="1826" height="461" alt="Novaflix (17)" src="https://github.com/user-attachments/assets/46607294-e576-49dc-85b1-c95d1e6918cd" />
<img width="1886" height="833" alt="Novaflix (16)" src="https://github.com/user-attachments/assets/3cd3b23d-0e96-4dbd-8039-6a4e58c43212" />
<img width="1737" height="967" alt="Novaflix (15)" src="https://github.com/user-attachments/assets/76a30731-d8d4-41bc-ab39-f5de1e4d1b35" />
<img width="1733" height="949" alt="Novaflix (14)" src="https://github.com/user-attachments/assets/eedaf187-0d1a-49ca-aae7-339b57b900f4" />
<img width="1856" height="918" alt="Novaflix (13)" src="https://github.com/user-attachments/assets/e73ac56e-a83b-4156-8a28-31bcab58649f" />
<img width="1910" height="779" alt="Novaflix (12)" src="https://github.com/user-attachments/assets/51ecd4c6-2f3f-4dcc-b1ea-d85c8465d31e" />
<img width="1839" height="749" alt="Novaflix (11)" src="https://github.com/user-attachments/assets/132fc674-28dc-4a60-82f7-ffd34b4f8cd8" />
<img width="1828" height="450" alt="Novaflix (10)" src="https://github.com/user-attachments/assets/40f2be7f-fafa-4531-9b9f-2ade5e24f597" />
<img width="1869" height="930" alt="Novaflix (9)" src="https://github.com/user-attachments/assets/c68af0e4-66ac-4b09-9b76-b11b0d2e70ed" />
<img width="1899" height="737" alt="Novaflix (8)" src="https://github.com/user-attachments/assets/c4e83c33-7ebf-471f-98a7-c803c84a359a" />
<img width="1899" height="357" alt="Novaflix (7)" src="https://github.com/user-attachments/assets/22a37e30-9dae-45d7-9398-cc055316dfc6" />
<img width="1878" height="881" alt="Novaflix (6)" src="https://github.com/user-attachments/assets/3831935c-d506-47aa-a463-9e81550d2f09" />
<img width="1832" height="724" alt="Novaflix (5)" src="https://github.com/user-attachments/assets/0bbf92c9-ac52-4ef1-ab01-dbb6d938f65d" />
<img width="1864" height="657" alt="Novaflix (4)" src="https://github.com/user-attachments/assets/ad224794-8675-46fd-a1b4-09a776e2383f" />
<img width="1814" height="653" alt="Novaflix (3)" src="https://github.com/user-attachments/assets/d6143b3a-8bb6-4d2c-a7ee-9c9c18ada6c4" />
<img width="1904" height="929" alt="Novaflix (2)" src="https://github.com/user-attachments/assets/b1f7b680-83a2-4bfa-bcf2-81995f89f6da" />
<img width="1903" height="875" alt="Novaflix (1)" src="https://github.com/user-attachments/assets/5dd8205c-f78e-4cd5-b07a-52ea39c9a0c6" />


# 🎬 Movie Recommendation System by Altaf Khan

A content-based movie recommendation web application built using Python, Machine Learning, and Streamlit.
The system suggests movies based on similarity and provides detailed information including posters, ratings, cast, and trailers.

---

## 🚀 Features

* 🔍 Recommend movies based on similarity
* 🎯 Three types of recommendations:

  * Recommended Movies (most accurate)
  * Based on Genre
  * Based on Cast / Director
* ⭐ IMDb rating and release year
* 🖼️ Movie posters using OMDb API
* 📖 Full movie description (detailed plot)
* 👨‍🎬 Cast information
* ▶ Watch trailer option (YouTube integration)
* 📊 Browse all movies with pagination

---

## 🧠 How It Works

* Uses **content-based filtering**
* Combines features like:

  * Genres
  * Keywords
  * Cast
  * Director
* Converts text data into vectors using **CountVectorizer**
* Computes similarity using **cosine similarity**
* Recommends top similar movies based on selected input

---

## 🛠️ Tech Stack

* Python
* Pandas
* Scikit-learn
* Streamlit
* OMDb API

---

## 📂 Project Structure

```bash
Movie-Recommender-System/
│
├── Files/                  # Dataset and required .pkl files
├── processing/             # Core logic (preprocessing & recommendation)
├── main.py                 # Streamlit app
├── requirements.txt
└── README.md
```

---

## ⚙️ Installation Guide

1. Clone the repository:

```bash
git clone https://github.com/ialtaf14/Novaflix.git
```

1. Navigate to the project:

```bash
cd Movie-Recommender-System
```

1. Install dependencies:

```bash
pip install -r requirements.txt
```

1. generate your omdb api key and paste in preprocess.py in line 204:
 url = f"<http://www.omdbapi.com/?t={selected_movie_name}&plot=full&apikey=OMDBAPIKEY>"

2. Run the application:

```bash
streamlit run main.py 

# or 
python -m streamlit run main.py
```

---

## ⚠️ Important Note

Large similarity `.pkl` files are not included due to GitHub size limits.

They will be automatically generated when you run the project for the first time.
👉 The first run may take a few seconds.

## 📜 License

This project is for educational purposes.
