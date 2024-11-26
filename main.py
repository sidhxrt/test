import spacy
from textacy import text_stats
from spacytextblob.spacytextblob import SpacyTextBlob

"""
pip install spacy textacy
python -m spacy download en_core_web_sm
python -m spacy download en_core_web_md (use this)
python -m spacy download en_core_web_lg

pip install spacytextblob
python -m textblob.download_corpora
"""

nlp = spacy.load("en_core_web_lg")

if "spacytextblob" not in nlp.pipe_names:
    nlp.add_pipe("spacytextblob")

def evaluate_response(question, response):
    question_doc = nlp(question)
    response_doc = nlp(response)

    # grammar & syntax
    def grammar_syntax_score(doc):
        grammar_errors = sum(1 for token in doc if token.is_alpha and token.tag_ == "XX")
        grammar_syntax_score = 0
        if len(doc) > 0:
            grammar_syntax_score = round((1 - grammar_errors / len(doc)) * 10, 2)
            return grammar_syntax_score
        return grammar_syntax_score

    # tone & professionalism
    def tone_professionalism_score(question_text, response_text):
        # OpenAI function call to calculate the tone and professionalism score
        tone = 0
        return tone

    # relevance to question
    def relevance_to_question_score(q_doc, r_doc):
        relevance_score = round(q_doc.similarity(r_doc) * 10, 2)
        return relevance_score

    # clarity and engagement
    def clarity_engagement_score(doc):
        readability = text_stats.readability.flesch_reading_ease(doc)
        return round(readability / 10, 2)  # FRE is originally 0 to 100, we bring it to 0 to 10

    # sentiment
    def sentiment_score(doc):
        polarity = doc._.blob.polarity  # polarity lies between -1 and 1
        sentiment_score = round((polarity + 1) * 5, 2)  # we will bring it to 0 to 10
        return sentiment_score

    # final score
    grammar = grammar_syntax_score(response_doc)
    tone = tone_professionalism_score(question, response)
    relevance = relevance_to_question_score(question_doc, response_doc)
    clarity = clarity_engagement_score(response_doc)
    sentiment = sentiment_score(response_doc)
    overall_score = round((grammar + sentiment + relevance + clarity)/4, 2)
    
    final_score = {
        "Grammar & Syntax": grammar,
        "Tone & Professionalism": tone,
        "Relevance to Question": relevance,
        "Clarity & Engagement": clarity,
        "Sentiment": sentiment,
        "Overall Score": overall_score
    }
    return final_score

def overall_report(data):
    """
    this function will have input like this:
    data = [
        {
            question: str
            candidate_response: str
            final_score: dict
            # comment: dict
        }
    ]
    """
    # OpenAI function call to calculate overall report based on individual question reports

# example
question_text = "What strategies would you use to handle a difficult customer?"
response_text = "I would stay calm, listen carefully, and offer a solution that meets their needs."
result = evaluate_response(question_text, response_text)

print(result)