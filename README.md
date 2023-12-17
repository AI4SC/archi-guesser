# Introduction
ArchiGuesser is an educational game that teaches our diverse architectural history across the globe using generative AI. Generative AIs are opening new possibilities to create content from text, speech, and images based on simple input prompts. Users use this to improve their productivity when summarizing knowledge, templating communication, and inspiring their creativity. But, can it also be used to teach, e.g. about our architectural history?

With this demo we are exploring this question. We created an educational game that combines various AI technologies from large language models and image generation to computer vision, in order to serve a single purpose: Teach users about architecture in an entertaining way. We wanted to enable students to explore and learn the diversity of our architectural history in a playful and exploratory way and at the same time experience and understand what current AI technologies can achieve.

# Run
ArchiGuesser is a webpage build on Python Dash. 

To run it we recommend to first create a python environment, e.g. with conda and then install all required packages via
```bash
pip install -r requirements.txt
```

Then the webpage can be run via:
```bash
python app.py
```

The application can also be build as docker/podman
```bash
docker build . -t ai4sc/archiguesser
docker run ai4sc/archiguesser
```

# Recreate and extend



```bash
jupyter collect_data.ipynb
```


# Data

ArchiGuesser requires different datasets consisting of images generated with Midjourney. We published the dataset separately here


# Cite

We published and showed the game at NeurIPS and BuildSys in 2013.

```bibtex
@inproceedings{ploennigs2023archiguesser,
  title={ArchiGuesser - AI Art Architecture Educational Game},
  author={Ploennigs, Joern and Berger, Markus},
  booktitle={NeurIPS - Conf. on Neural Information Processing Systems, Creative AI Track},
  year={2023}
}
```

```bibtex
@inproceedings{berger2023archiguesser,
  title={ArchiGuesser--Teaching Architecture Styles using Generative AI},
  author={Berger, Markus and Ploennigs, Joern},
  booktitle={BuildSys - ACM Int. Conf. on Systems for Energy-Efficient Buildings, Cities, and Transportation},
  pages={284--285},
  year={2023}
}
```
