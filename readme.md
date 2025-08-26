# Auto Summarizer 📄✨

An intelligent text summarization tool that automatically generates concise summaries from long-form content using advanced NLP techniques.

## 🚀 Features

- **Automatic Text Summarization**: Generate concise summaries from lengthy documents
- **Multiple Input Formats**: Support for text files, PDFs, and direct text input
- **User-Friendly Interface**: Clean and intuitive design
- **Decoupled frontend & backend**: seperate frontend and backend for future scalling
- **API intigration**: FastAPI to connect the backend and frontend
- **Cloud intigration**: backend deployed on OCI(Oracle cloud infrastructure) and frontend on streamlit cloud
- **containorized backend**: backend is build in docker image with both Arm and linux use 

## 🛠️ Technologies Used

- **Python 3.9+**
- **Natural Language Processing**: NLTK, spaCy, or Transformers
- **Machine Learning**: TensorFlow/PyTorch
- **Web Framework**: Fast-API, Cloud(Oracle Cloud)
- **Frontend**: Python, streamlit
- **Text Processing**: BeautifulSoup, regex

## 📦 Installation

### Prerequisites
- Python 3.8 or higher
- pip package manager

### Setup

1. **Clone the repository**
```bash
git clone https://github.com/Harsh0patel/Auto_summrizer.git
cd Auto_summrizer
```

2. **Create a virtual environment**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

## To run locally

1. **clone only frontend**
```bash
git clone https://github.com/Harsh0patel/Auto_summrizer.git
cd Auto_summrizer
```

2. **Create a virtual environment**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **get docker image**
```terminal
docker pull harsh0patel/summury-api:latest
docker run -p 8000:8000 harhs0patel/summury-api
```

5. **change main.py file this line**
```python 
line no: 17 API = "http://161.118.190.255:8000"  #chang this url to http://localhost:8000
```

6. **run following command**
```terminal
python -m streamlit run frontend/main.py
```

7. **test your document**


## 🖥️ Usage

### API Image

```bash
docker pull harsh0patel/summury-api:latest
```

```link
https://hub.docker.com/repository/docker/harsh0patel/summury-api/general
```

## 📊 Example

**Input Text:**
```
The field of artificial intelligence has grown rapidly in recent years. Machine learning algorithms have become increasingly sophisticated, enabling computers to perform tasks that were once thought to be exclusively human. Deep learning, a subset of machine learning, has been particularly successful in areas such as image recognition, natural language processing, and speech recognition. These advances have led to practical applications in various industries, including healthcare, finance, and transportation.
```

**Generated Summary:**
```
The field of artificial intelligence has grown rapidly with sophisticated machine learning algorithms. Deep learning has been successful in image recognition, natural language processing, and speech recognition. These advances have practical applications in healthcare, finance, and transportation industries.
```

## 📁 Project Structure

```
Auto_summrizer/
├── backend/
│   ├── config/
|   |   |──mongodb_config.py          # mongodb call and auth
│   ├── models/
|   |   |──pydantic_models.py          # json format checkers inside api calls
│   ├── routes/
|   |   |──generatedata.py          # API route for model calls
|   |   |──home_page.py          # API homepage route calls
|   |   |──languagechnage.py          # API route for change language
|   |   |──upload_data.py          # API call for upload data to database
│   ├── utils/
|   |   |──Generate_summary.py          # model for gnerate summary
|   |   |──preprocess.py          # handle the text formatting and clean text
│   ├── .dockerignore          # file not need in docker 
│   ├── app.py         # main file for API call
│   └── requirements.txt              # required libararys for backend
├── frontend/
│   └── main.py                # full frontend
├── model/ (lstm model that was failed)
│   ├── dataloader.ipynb    # notebook for dataload from hugging face
│   ├── fine_tune.ipynb     # notebook for imporve the model
│   ├── infrenceloop.py    # test loop 
│   ├── model.ipynb    # use for modle training(lstm)
│   ├── parser.py    # for extract the text from files 
│   ├── preprocess.ipynb    # use for preprocess the extracted text
│   ├── summurizer.py    # encoder-decoder class
│   └── tokenization.py    # use for convert text into subword tokens
├── notebooks/
│   ├── a.py                # use for some test work and etc...
│   ├── b.py                # user for some try and error work...
│   └── test_whisper.py                # user for try and error work...
├── prototype/
│   ├── ai_summarization_100.jsonl                # data for prototype
│   ├── bpe.model                # tokenization model
|   |── bpe.vocab                # tokenization vocab
│   └── prototype.ipynb                # training and test notebook
├── .gitignore
├── requirements.txt          # Python dependencies
└── README.md                # This file
```

## 🔮 Future Enhancements

- [ ] Support for more file formats (DOCX, HTML, etc.)
- [ ] Real-time collaborative summarization
- [ ] Summary quality scoring
- [ ] Keyword extraction and highlighting
- [ ] GPU backend integration for faster process
- [ ] implementing self made summurizer 

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 👤 Author

**Harsh Patel**
- GitHub: [@Harsh0patel](https://github.com/Harsh0patel)
- Email: hp333854@gmail.com

## 🙏 Acknowledgments

- Thanks to the open-source NLP community
- Inspired by recent advances in transformer models
- Special thanks to contributors and testers

## 📞 Support

If you have any questions or need help, please:
- Open an issue on GitHub
- Contact the author: hp333854@gmail.com

---

⭐ **If you found this project helpful, please give it a star!** ⭐
