# 01. Text Preprocessing

This folder contains notebooks and code related to **text preprocessing** in NLP.  
It is part of the **Sudo Code Program NLP** repository.

## 📂 Contents

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
    
- **Vietnamese Diacritic Normalization**
  Fix misplaced Vietnamese tone marks and common typing variants after tokenization/cleaning.
  Example: `"hoà bình"` → `"hòa bình"`.
---

### 🆕 Basic Additional Preprocessing Methods

- **Stopword Removal**  
  Remove frequent but less informative words (*“là”*, *“của”*, *và”* …).

- **Stemming / Lemmatization**  
  Reduce words to their base or root form to avoid duplicates.  
  Example: *học*, *học tập*, *học sinh* → *học*.

- **Handling Abbreviations**  
  Normalize or expand common short forms.  
  Example: *TP.HCM* → *thành_phố_hồ_chí_minh*.

## 📒 Notebook

- [Vietnam Online News Text Processing](Vietnam_Online_News_Text_Processing.ipynb)

## 📚 References
- [NLTK Book – Chapter 3: Processing Raw Text](https://www.nltk.org/book/ch03.html)  
- [PyVi: Vietnamese Tokenizer](https://github.com/trungtv/pyvi)  
- [Underthesea Documentation](https://underthesea.readthedocs.io/en/latest/)  
- [Jurafsky & Martin – Speech and Language Processing (3rd ed. draft, Chapter 2)](https://web.stanford.edu/~jurafsky/slp3/2.pdf)  
