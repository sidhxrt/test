import nltk
from typing import Dict
from spacy.lang.en import English
from nltk.sentiment import SentimentIntensityAnalyzer

# nltk.download('vader_lexicon')

# spacy and vader 
nlp = English()
nlp.add_pipe('sentencizer')
sentiment_analyzer = SentimentIntensityAnalyzer()

def individual_report_generator(question: str, answer: str):
    grammar_weight = 0.3
    relevance_weight = 0.5
    tone_weight = 0.2

    formal_words = {"therefore", "hence", "furthermore", "however", "please", "thank you"}
    slang_words = {"gonna", "wanna", "ain't", "y'all", "dude"}
    
    doc = nlp(answer)

    # grammar & syntax score(spacy)
    grammar_errors = sum(1 for token in doc if not token.is_alpha)
    grammar_score = max(0, 10 - grammar_errors)  

    # tone & professionalism score(spacy)
    formal_count = sum(1 for word in doc if word.text.lower() in formal_words)
    slang_count = sum(1 for word in doc if word.text.lower() in slang_words)
    professionalism_score = max(0, 10 + formal_count - slang_count)

    # relevance to question score(spacy)
    question_doc = nlp(question)
    shared_words = set(token.text.lower() for token in doc if token.is_alpha) & \
                   set(token.text.lower() for token in question_doc if token.is_alpha)
    relevance_score = min(10, len(shared_words))  

    # clarity & engagement score(spacy)
    sentence_count = len(list(doc.sents))
    clarity_score = min(10, len(doc) / (sentence_count + 1))  

    # sentiment score(vader)
    sentiment_scores = sentiment_analyzer.polarity_scores(answer)
    sentiment_score = sentiment_scores['compound']  # 'compound' represents overall sentiment
    sentiment_score = round((sentiment_score + 1) * 5, 2)  # Convert from [-1, 1] to [0, 10]

    # weighted overall score
    overall_score = (
        grammar_weight * grammar_score +
        relevance_weight * relevance_score +
        tone_weight * professionalism_score
    )

    # individual question report
    report = {
        "Grammar & Syntax": round(grammar_score, 2),
        "Tone & Professionalism": round(professionalism_score, 2),
        "Relevance to Question": round(relevance_score, 2),
        "Clarity & Engagement": round(clarity_score, 2),
        "Sentiment": round(sentiment_score, 2),
        "Overall Score": round(overall_score, 2),
    }
    return report

question = "Write an email apologizing to a customer for a delayed shipment and explain how the issue is being resolved."
answer = "Subject: Sorry for the Delay in Your Shipment Hi [Customer's Name], I'm really sorry about the delay with your shipment. I know how frustrating it must be to wait longer than expected, and I completely understand if this has been an inconvenience for you. The delay happened because [briefly explain the reason, e.g., there was an unexpected issue at our shipping center]. We're already working to fix this by [explain the solution, e.g., expediting your package and ensuring it reaches you as soon as possible]. Your updated delivery date is [insert new delivery date], and Ill keep you posted if there are any more changes (but I dont expect there to be). Again, Im really sorry for this. Thanks so much for being patient with us, and if theres anything else I can help with, just let me know! Take care, [Your Name]"

report = individual_report_generator(question, answer)
print(report)