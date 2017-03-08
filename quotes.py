"""
Heuristics-based quote extraction tool, based on "Automatic Detection of Quotations
in Multilingual News," European Commission, Joint Research Venture.

RULES:
(1) quote-mark QUOTE quote-mark [,] verb [modifier][determiner] [title] name 
	e.g. "blah blah", said again the journalist John Smith.

(2) quote-mark QUOTE quote-mark [; or ,] [title] name[modifier] verb 
e.g. "blah blah", Mr John Smith said.

(3) name [, up to 60 characters ,] verb [:|that] quote-mark QUOTE quote-mark 
e.g. John Smith, supporting AFG, said: "blah blah".

SOURCE:
[1] https://www.quora.com/What-is-the-best-approach-to-extract-quotations-from-text-and-their-speakers-using-the-following-rules
[2] https://pdfs.semanticscholar.org/3979/b0125f77499de215fb29e1c5d8feae5cf476.pdf

TODO:
- Use Semi-CFG to enforce rules
- Resolve anaphoric expressions (i.e., he said, the President said)

"""
import io
import re
from collections import namedtuple

#from nltk import RegexpTagger
from textblob import TextBlob
from nltk import ne_chunk
from nltk.stem import WordNetLemmatizer

SINGLE_QUOTE_MAP = {
    0x2018: 39, 
    0x2019: 39,
    0x201A: 39,
    0x201B: 39,
    0x2039: 39,
    0x203A: 39,
}

DOUBLE_QUOTE_MAP = {
    0x00AB: 34,
    0x00BB: 34,
    0x201C: 34,
    0x201D: 34,
    0x201E: 34,
    0x201F: 34,
}

QUOTE_PATTERN = re.compile('(\")')

ATTRIBUTION_VERBS_LEMMATIZED = [
	'accuse',
	'add',
	'assure'
	'call',
	'comment',
	'confirm',
	'continue',
	'declare',
	'report',
	'say',
	'sum',
	'tell',
]

PRONOUNS = [
	'he',
	'she',
]

lemmatizer = WordNetLemmatizer()

Attribution = namedtuple('Attribution', [
	'entity',
	'entity_position',
	'verb',
	'verb_position'
])


def init():
	nltk.download('maxent_ne_chunker')
	nltk.download('words')


def get_named_entities(tagged_words):
	"""
	@param chunk is a tokenized, pos-tagged list of words, or TextBlob.WordList
	"""
	for chunk in ne_chunk(tagged_words):
		if hasattr(chunk, 'node'):
			value = ' '.join(c[0] for c in chunk.leaves())
			yield value,chunk.node


def get_pronouns(tagged_words):
	"""
	@param chunk is a tokenized, pos-tagged list of words, or TextBlob.WordList
	"""
	for word, tag in tagged_words:
		if tag == 'PRP' and word.lower() in PRONOUNS:
			yield word, tag

def get_attribution_verbs(tagged_words):
	"""
	@param chunk is a tokenized, pos-tagged list of words, or TextBlob.WordList
	"""
	for word, tag in tagged_words:
		if tag.startswith('VB') and lemmatizer.lemmatize(word.lower(), pos='v')\
				in ATTRIBUTION_VERBS_LEMMATIZED:
			yield word, tag


def is_attribution_verb(tagged_words):
	"""
	@param chunk is a tokenized, pos-tagged list of words, or TextBlob.WordList
	"""
	return len(list(get_attribution_verbs(tagged_words))) > 0


def get_attribution(chunk, seek_backwards=False):
	"""
	@param sentence is a tokenized, pos-tagged list of words, or TextBlob.WordList
	"""
	seek_index = -1 if seek_backwards else 0
	tagged_chunk = chunk.pos_tags
	verbs = list(get_attribution_verbs(tagged_chunk))
	if not len(verbs):
		return
	entities = list(get_named_entities(tagged_chunk))
	if not len(entities):
		entities = list(get_pronouns(tagged_chunk))
		if not len(entities):
			return
	return Attribution(
		entities[seek_index][0],
		chunk.find(entities[seek_index][0]) + seek_index * len(chunk),
		verbs[seek_index][0],
		chunk.find(verbs[seek_index][0]) + seek_index * len(chunk))


def quotes(text):
	entities = get_named_entities(TextBlob(text).pos_tags)
	paragraphs = text.split('\n')
	for paragraph in paragraphs:
		parts = QUOTE_PATTERN.split(paragraph)
		is_quote = False
		for index, part in enumerate(parts):
			if QUOTE_PATTERN.match(part):
				is_quote = not is_quote
			elif is_quote:
				if len(parts) >= index + 2:
					next_sentence = TextBlob(parts[index + 2]).sentences[0]
					attribution = get_attribution(next_sentence)
					if attribution:
						yield part, attribution
				if index >= 2:
					last_sentence = TextBlob(parts[index - 2]).sentences[-1]
					attribution = get_attribution(last_sentence, seek_backwards=True)
					if attribution and\
							0 <= attribution.verb_position - attribution.entity_position <= 60:
						yield part, attribution


if __name__ == '__main__':
	with io.open('corpus/1.txt') as t:
		text = t.read()

	text = text.translate(SINGLE_QUOTE_MAP).translate(DOUBLE_QUOTE_MAP)
	#blob = TextBlob(text)

	#topics = blob.noun_phrases
	print list(quotes(text))

	test_cases = [
		'''"What is all this?" Tony Blair's spokesman said.''',
		'''"What is all this?" Mr. Tony Blair's spokesman said.''',
		'''"What is all this?" Mr Tony Blair's spokesman said.''',
		'''"What is all this?" Mr. Blair's spokesman said.''',
		'''"What is all this?" Mr Blair's spokesman said.''',
	]
 