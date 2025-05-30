"""
NLP-based scoring service for interview responses
"""
import re
import json
from typing import Dict, List, Tuple, Optional
import openai
from collections import Counter

from app.config import settings
from app.utils.validators import validate_score_range

# Simple fallback for textstat functions
def simple_flesch_reading_ease(text: str) -> float:
    """Simple approximation of Flesch reading ease"""
    words = len(text.split())
    sentences = len(re.split(r'[.!?]+', text))
    if sentences == 0 or words == 0:
        return 50.0
    avg_sentence_length = words / sentences
    return max(0, min(100, 206.835 - (1.015 * avg_sentence_length)))

def simple_flesch_kincaid_grade(text: str) -> float:
    """Simple approximation of Flesch-Kincaid grade level"""
    words = len(text.split())
    sentences = len(re.split(r'[.!?]+', text))
    if sentences == 0 or words == 0:
        return 8.0
    avg_sentence_length = words / sentences
    return max(0, (0.39 * avg_sentence_length) + 11.8 - 15.59)


class NLPScorer:
    """Service for scoring interview responses using NLP techniques"""

    def __init__(self):
        """Initialize the NLP scorer with required models"""
        if not settings.openai_api_key:
            raise ValueError("OpenAI API key is required for NLP scoring")

        self.client = openai.OpenAI(api_key=settings.openai_api_key)

        # Note: spaCy disabled for compatibility
        self.nlp = None

        # Common filler words to detect
        self.filler_words = {
            'um', 'uh', 'like', 'you know', 'so', 'well', 'actually',
            'basically', 'literally', 'obviously', 'definitely', 'totally',
            'really', 'very', 'quite', 'sort of', 'kind of'
        }

        # Confidence indicators
        self.confidence_indicators = {
            'positive': ['confident', 'certain', 'sure', 'definitely', 'absolutely',
                        'clearly', 'obviously', 'undoubtedly', 'precisely'],
            'negative': ['maybe', 'perhaps', 'possibly', 'might', 'could be',
                        'not sure', 'uncertain', 'unclear', 'confused']
        }

    async def score_response(self, text: str, question: str, question_type: str) -> Dict:
        """
        Comprehensive scoring of interview response

        Args:
            text: The response text to score
            question: The original interview question
            question_type: Type of question (behavioral, technical, situational)

        Returns:
            Dictionary containing detailed scores and analysis
        """
        if not text or not text.strip():
            return self._create_empty_score()

        # Clean and preprocess text
        processed_text = self._preprocess_text(text)

        # Perform various analyses
        basic_metrics = self._analyze_basic_metrics(processed_text)
        sentiment_analysis = self._analyze_sentiment(processed_text)
        structure_analysis = self._analyze_structure(processed_text)
        confidence_analysis = self._analyze_confidence(processed_text)

        # Get AI-powered scoring
        ai_scores = await self._get_ai_scores(processed_text, question, question_type)

        # Combine all analyses into final scores
        final_scores = self._calculate_final_scores(
            basic_metrics, sentiment_analysis, structure_analysis,
            confidence_analysis, ai_scores, question_type
        )

        # Generate detailed feedback
        feedback = await self._generate_feedback(
            processed_text, question, final_scores, basic_metrics
        )

        return {
            'scores': final_scores,
            'feedback': feedback,
            'metrics': {
                'basic': basic_metrics,
                'sentiment': sentiment_analysis,
                'structure': structure_analysis,
                'confidence': confidence_analysis
            }
        }

    def _preprocess_text(self, text: str) -> str:
        """Clean and preprocess text for analysis"""
        # Remove excessive whitespace
        text = ' '.join(text.split())

        # Remove special characters but keep punctuation
        text = re.sub(r'[^\w\s\.\,\!\?\;\:\-\(\)]', '', text)

        return text.strip()

    def _analyze_basic_metrics(self, text: str) -> Dict:
        """Analyze basic text metrics"""
        words = text.split()
        sentences = re.split(r'[.!?]+', text)
        sentences = [s.strip() for s in sentences if s.strip()]

        # Count filler words
        filler_count = sum(1 for word in words if word.lower() in self.filler_words)

        # Calculate readability
        try:
            readability_score = simple_flesch_reading_ease(text)
            grade_level = simple_flesch_kincaid_grade(text)
        except:
            readability_score = 50  # Default moderate score
            grade_level = 8

        return {
            'word_count': len(words),
            'sentence_count': len(sentences),
            'unique_words': len(set(word.lower() for word in words)),
            'avg_words_per_sentence': len(words) / max(len(sentences), 1),
            'filler_words_count': filler_count,
            'filler_words_ratio': filler_count / max(len(words), 1),
            'readability_score': readability_score,
            'grade_level': grade_level
        }

    def _analyze_sentiment(self, text: str) -> Dict:
        """Analyze sentiment and emotional tone"""
        if not self.nlp:
            return {'sentiment_score': 0.0, 'emotional_tone': 'neutral'}

        doc = self.nlp(text)

        # Simple sentiment analysis based on word polarity
        positive_words = ['good', 'great', 'excellent', 'successful', 'achieved',
                         'accomplished', 'effective', 'efficient', 'improved']
        negative_words = ['bad', 'poor', 'failed', 'difficult', 'challenging',
                         'problem', 'issue', 'mistake', 'error']

        pos_count = sum(1 for token in doc if token.text.lower() in positive_words)
        neg_count = sum(1 for token in doc if token.text.lower() in negative_words)

        total_words = len([token for token in doc if token.is_alpha])
        sentiment_score = (pos_count - neg_count) / max(total_words, 1)

        # Determine emotional tone
        if sentiment_score > 0.1:
            tone = 'positive'
        elif sentiment_score < -0.1:
            tone = 'negative'
        else:
            tone = 'neutral'

        return {
            'sentiment_score': max(-1, min(1, sentiment_score)),
            'emotional_tone': tone,
            'positive_indicators': pos_count,
            'negative_indicators': neg_count
        }

    def _analyze_structure(self, text: str) -> Dict:
        """Analyze response structure and organization"""
        sentences = re.split(r'[.!?]+', text)
        sentences = [s.strip() for s in sentences if s.strip()]

        # Look for structure indicators
        structure_words = {
            'intro': ['first', 'initially', 'to begin', 'starting'],
            'body': ['then', 'next', 'after', 'following', 'subsequently'],
            'conclusion': ['finally', 'in conclusion', 'to summarize', 'overall']
        }

        structure_score = 0
        has_intro = any(any(word in sentence.lower() for word in structure_words['intro'])
                       for sentence in sentences[:2])
        has_body = any(any(word in sentence.lower() for word in structure_words['body'])
                      for sentence in sentences)
        has_conclusion = any(any(word in sentence.lower() for word in structure_words['conclusion'])
                           for sentence in sentences[-2:])

        if has_intro:
            structure_score += 30
        if has_body:
            structure_score += 40
        if has_conclusion:
            structure_score += 30

        # Check for logical flow
        if len(sentences) >= 3:
            structure_score += 10  # Bonus for having multiple sentences

        return {
            'structure_score': min(100, structure_score),
            'has_introduction': has_intro,
            'has_body': has_body,
            'has_conclusion': has_conclusion,
            'sentence_variety': len(set(len(s.split()) for s in sentences))
        }

    def _analyze_confidence(self, text: str) -> Dict:
        """Analyze confidence indicators in the response"""
        text_lower = text.lower()

        positive_confidence = sum(1 for word in self.confidence_indicators['positive']
                                if word in text_lower)
        negative_confidence = sum(1 for word in self.confidence_indicators['negative']
                                if word in text_lower)

        # Calculate confidence score
        total_indicators = positive_confidence + negative_confidence
        if total_indicators == 0:
            confidence_score = 0.5  # Neutral
        else:
            confidence_score = positive_confidence / total_indicators

        return {
            'confidence_score': confidence_score,
            'positive_indicators': positive_confidence,
            'negative_indicators': negative_confidence,
            'confidence_level': 'high' if confidence_score > 0.7 else 'medium' if confidence_score > 0.3 else 'low'
        }

    async def _get_ai_scores(self, text: str, question: str, question_type: str) -> Dict:
        """Get AI-powered scores using OpenAI GPT"""
        try:
            prompt = self._create_scoring_prompt(text, question, question_type)

            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are an expert interview evaluator."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=1000
            )

            result = response.choices[0].message.content
            return self._parse_ai_response(result)

        except Exception as e:
            print(f"Error getting AI scores: {e}")
            return self._get_fallback_scores(text, question_type)

    def _create_scoring_prompt(self, text: str, question: str, question_type: str) -> str:
        """Create prompt for AI scoring"""
        return f"""
        Please evaluate this interview response on a scale of 0-100 for each criterion:

        Question: {question}
        Question Type: {question_type}
        Response: {text}

        Please provide scores for:
        1. Content Relevance (0-100): How well does the response address the question?
        2. Communication Clarity (0-100): How clear and articulate is the response?
        3. Structure & Organization (0-100): How well-organized is the response?
        4. Technical Accuracy (0-100): How technically sound is the response? (if applicable)

        Also provide:
        - 3 key strengths
        - 3 areas for improvement
        - 3 specific suggestions for improvement

        Format your response as JSON:
        {{
            "content_relevance": score,
            "communication_clarity": score,
            "structure_organization": score,
            "technical_accuracy": score,
            "strengths": ["strength1", "strength2", "strength3"],
            "weaknesses": ["weakness1", "weakness2", "weakness3"],
            "suggestions": ["suggestion1", "suggestion2", "suggestion3"]
        }}
        """

    def _parse_ai_response(self, response: str) -> Dict:
        """Parse AI response and extract scores"""
        try:
            # Try to extract JSON from the response
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                result = json.loads(json_match.group())

                # Validate scores
                for key in ['content_relevance', 'communication_clarity', 'structure_organization']:
                    if key in result:
                        result[key] = max(0, min(100, int(result[key])))

                return result
        except:
            pass

        # Fallback parsing
        return self._get_fallback_scores("", "general")

    def _get_fallback_scores(self, text: str, question_type: str) -> Dict:
        """Provide fallback scores when AI scoring fails"""
        word_count = len(text.split())

        # Simple heuristic scoring
        base_score = min(85, max(40, word_count * 2))

        return {
            'content_relevance': base_score,
            'communication_clarity': base_score - 5,
            'structure_organization': base_score - 10,
            'technical_accuracy': base_score if question_type == 'technical' else None,
            'strengths': ["Response provided", "Attempted to answer", "Used appropriate language"],
            'weaknesses': ["Could be more detailed", "Could improve structure", "Could add examples"],
            'suggestions': ["Provide more specific examples", "Organize response better", "Expand on key points"]
        }

    def _calculate_final_scores(self, basic_metrics: Dict, sentiment: Dict,
                              structure: Dict, confidence: Dict, ai_scores: Dict,
                              question_type: str) -> Dict:
        """Calculate final weighted scores"""

        # Base scores from AI
        content_score = ai_scores.get('content_relevance', 70)
        clarity_score = ai_scores.get('communication_clarity', 70)
        structure_score = ai_scores.get('structure_organization', 70)
        technical_score = ai_scores.get('technical_accuracy')

        # Apply adjustments based on metrics

        # Adjust clarity based on filler words and readability
        filler_penalty = min(20, basic_metrics['filler_words_ratio'] * 100)
        clarity_score = max(0, clarity_score - filler_penalty)

        # Adjust structure based on organization analysis
        structure_bonus = (structure['structure_score'] - 70) * 0.3
        structure_score = max(0, min(100, structure_score + structure_bonus))

        # Calculate overall score
        scores = [content_score, clarity_score, structure_score]
        if technical_score is not None and question_type == 'technical':
            scores.append(technical_score)

        overall_score = int(sum(scores) / len(scores))

        return {
            'overall_score': overall_score,
            'content_relevance_score': int(content_score),
            'communication_clarity_score': int(clarity_score),
            'structure_organization_score': int(structure_score),
            'technical_accuracy_score': int(technical_score) if technical_score else None,
            'sentiment_score': sentiment['sentiment_score'],
            'confidence_indicators': confidence['positive_indicators'],
            'filler_words_count': basic_metrics['filler_words_count'],
            'word_count': basic_metrics['word_count'],
            'unique_words_count': basic_metrics['unique_words']
        }

    async def _generate_feedback(self, text: str, question: str, scores: Dict, metrics: Dict) -> Dict:
        """Generate detailed feedback for the response"""
        try:
            feedback_prompt = f"""
            Based on this interview response analysis, provide constructive feedback:

            Question: {question}
            Response: {text}
            Overall Score: {scores['overall_score']}/100
            Word Count: {metrics['word_count']}
            Filler Words: {metrics['filler_words_count']}

            Provide detailed feedback including:
            1. What the candidate did well
            2. Specific areas for improvement
            3. Actionable tips for better responses

            Keep feedback constructive and encouraging.
            """

            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a supportive interview coach."},
                    {"role": "user", "content": feedback_prompt}
                ],
                temperature=0.5,
                max_tokens=500
            )

            detailed_feedback = response.choices[0].message.content

        except Exception as e:
            detailed_feedback = self._generate_fallback_feedback(scores, metrics)

        return {
            'detailed_feedback': detailed_feedback,
            'improvement_tips': self._generate_improvement_tips(scores, metrics)
        }

    def _generate_fallback_feedback(self, scores: Dict, metrics: Dict) -> str:
        """Generate fallback feedback when AI generation fails"""
        score = scores['overall_score']

        if score >= 80:
            return "Excellent response! You demonstrated strong communication skills and provided relevant content."
        elif score >= 60:
            return "Good response with room for improvement. Consider adding more specific examples and improving organization."
        else:
            return "Your response shows effort, but could benefit from better structure and more detailed content."

    def _generate_improvement_tips(self, scores: Dict, metrics: Dict) -> str:
        """Generate specific improvement tips"""
        tips = []

        if scores['communication_clarity_score'] < 70:
            tips.append("Practice speaking more clearly and reduce filler words")

        if scores['structure_organization_score'] < 70:
            tips.append("Use the STAR method (Situation, Task, Action, Result) to structure your responses")

        if metrics['word_count'] < 50:
            tips.append("Provide more detailed responses with specific examples")

        if metrics['filler_words_count'] > 5:
            tips.append("Practice reducing filler words like 'um', 'uh', and 'like'")

        if not tips:
            tips.append("Continue practicing to maintain your strong performance")

        return "; ".join(tips)

    def _create_empty_score(self) -> Dict:
        """Create empty score structure for invalid responses"""
        return {
            'scores': {
                'overall_score': 0,
                'content_relevance_score': 0,
                'communication_clarity_score': 0,
                'structure_organization_score': 0,
                'technical_accuracy_score': None,
                'sentiment_score': 0.0,
                'confidence_indicators': 0,
                'filler_words_count': 0,
                'word_count': 0,
                'unique_words_count': 0
            },
            'feedback': {
                'detailed_feedback': "No response provided for analysis.",
                'improvement_tips': "Please provide a response to receive feedback."
            },
            'metrics': {}
        }
