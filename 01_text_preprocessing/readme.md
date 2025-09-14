# 01. Text Preprocessing

This folder contains notebooks and code related to **text preprocessing** in NLP.  
It is part of the **Sudo Code Program NLP** repository.

## 📂 Contents

- **Unicode & Diacritic Normalization**  
  Ensure consistent text representation by normalizing Unicode forms (NFC/NFKC).  
  Example: `"Hoà"` and `"Hoà"` → `"Hoà"`.

- **Removing Noise (HTML tags, URLs, emails, numbers, emojis)**  
  Clean the text by removing unnecessary elements such as:  
  - HTML tags (`<div>`, `<p>`, …)  
  - URLs (http://, https://)  
  - Email addresses (e.g., `abc@gmail.com`)  
  - Numbers (e.g., `2025`, `12345`)  
  - Emojis (😊😂🔥)

- **Vietnamese Tokenization – PyVi**  
  Segment sentences into meaningful words, preserving multi-syllable words.  
  Example:  
  - Input: `Tôi sống ở Hà Nội`  
  - Output: `["Tôi", "sống", "ở", "Hà_Nội"]`

- **Smart Lowercasing with POS Tagging**  
  Convert text to lowercase while keeping **proper nouns (PROPN)** intact.  
  - Example: `"Việt Nam"` should remain `"Việt_Nam"`,  
    while `"Trường học rất đẹp"` → `"trường_học rất đẹp"`.

---

### 🆕 More Preprocessing Methods (to be added)

- **Stopword Removal**  
  Eliminate common words (*“là”*, *“và”*, *“của”*) that do not add semantic value.  

- **Stemming & Lemmatization**  
  Reduce words to their root form.  
  - *học*, *học tập*, *học sinh* → *học*  

- **Handling Abbreviations & Acronyms**  
  Expand or standardize abbreviations.  
  - *TP.HCM* → *Thành_phố_Hồ_Chí_Minh*  
  - *UN* → *United_Nations*  

- **Synonym Normalization**  
  Map different words with the same meaning to one form.  
  - *xe hơi* = *ô tô*  

- **Spelling Correction**  
  Fix common typos or OCR errors.  
  - *ngôn ngữ anh* → *ngôn_ngữ_anh*  

- **Handling Negations**  
  Mark or transform negative phrases to preserve meaning.  
  - *không vui* → *không_vui*  

- **Part-of-Speech Filtering**  
  Keep only relevant word types (e.g., nouns, verbs, adjectives).  

- **Lemmatization with Dictionaries**  
  Use Vietnamese lexicons to convert inflected forms to their canonical form.  

- **Handling Rare Words / Class Balancing**  
  Replace low-frequency terms with `<UNK>` or group rare labels into `"other"`.  

## 📒 Notebook

- [Vietnam Online News Text Processing](Vietnam_Online_News_Text_Processing.ipynb)

## 📚 References
- [NLTK Book – Chapter 3: Processing Raw Text](https://www.nltk.org/book/ch03.html)  
- [PyVi: Vietnamese Tokenizer](https://github.com/trungtv/pyvi)  
- [Underthesea Documentation](https://underthesea.readthedocs.io/en/latest/)  
- [Jurafsky & Martin – Speech and Language Processing (3rd ed. draft, Chapter 2)](https://web.stanford.edu/~jurafsky/slp3/2.pdf)  
