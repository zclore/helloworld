import nltk
import sys
import csv
import json
from nltk.stem import WordNetLemmatizer
from nltk.stem.porter import PorterStemmer 
from nltk.parse.stanford import StanfordDependencyParser
from stanfordcorenlp import StanfordCoreNLP
from nltk.corpus import wordnet
from nltk.tree import Tree

from match import Data_preprocessing
from adjustTree import Tree_Operator

def dep2Tree(sentence):
		path_to_jar = 'D:/myPlugin/stanford-parser-full-2018-10-17/stanford-parser.jar'
		path_to_models_jar = 'D:/myPlugin/stanford-parser-full-2018-10-17/stanford-parser-3.9.2-models.jar'
		dependency_parser = StanfordDependencyParser(path_to_jar=path_to_jar, path_to_models_jar=path_to_models_jar)
		result = dependency_parser.raw_parse(sentence)
		t = result.__next__().tree()
		return t


if __name__ == '__main__':
	
	inputText = "Return authors who have more papers than Bob in VLDB after 2000".lower()
	datasetpath = "D:/Study/dataset4vis/electricityConsumptionOfEasternChina.csv"

	tree = dep2Tree(inputText)
	tree.draw()