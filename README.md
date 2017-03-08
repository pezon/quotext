# Quotext

Heuristics-based quote extraction tool, based on "Automatic Detection of Quotations in Multilingual News," European Commission, Joint Research Venture.

## Rules

1. 	quote-mark QUOTE quote-mark [,] verb [modifier][determiner] [title] name 
	e.g. "blah blah", said again the journalist John Smith.

2.	quote-mark QUOTE quote-mark [; or ,] [title] name[modifier] verb 
	e.g. "blah blah", Mr John Smith said.

3.	name [, up to 60 characters ,] verb [:|that] quote-mark QUOTE quote-mark 
	e.g. John Smith, supporting AFG, said: "blah blah".

## References

[1] https://www.quora.com/What-is-the-best-approach-to-extract-quotations-from-text-and-their-speakers-using-the-following-rules

[2] https://pdfs.semanticscholar.org/3979/b0125f77499de215fb29e1c5d8feae5cf476.pdf

## Todo

- Use Semi-CFG to enforce rules
- Resolve anaphoric expressions (i.e., he said, the President said)
