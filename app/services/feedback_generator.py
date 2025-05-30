"""
Feedback generation service for interview responses
"""
from typing import Dict, List, Optional
import openai
from sqlalchemy.orm import Session

from app.config import settings
from app.models.response import InterviewResponse, ResponseScore
from app.models.question import Question


class FeedbackGenerator:
    """Service for generating comprehensive feedback and suggestions"""
    
    def __init__(self):
        """Initialize the feedback generator"""
        if settings.openai_api_key:
            self.client = openai.OpenAI(api_key=settings.openai_api_key)
        else:
            self.client = None
    
    def generate_comprehensive_feedback(self, 
                                      response: InterviewResponse, 
                                      score: ResponseScore, 
                                      question: Question) -> Dict:
        """
        Generate comprehensive feedback for an interview response
        
        Args:
            response: The interview response object
            score: The response score object
            question: The question object
        
        Returns:
            Dictionary containing detailed feedback and suggestions
        """
        # Extract key information
        response_text = response.processed_text or response.original_text or ""
        question_text = question.content
        question_type = question.question_type
        overall_score = score.overall_score
        
        # Generate different types of feedback
        strengths = self._identify_strengths(score, response_text, question_type)
        weaknesses = self._identify_weaknesses(score, response_text, question_type)
        suggestions = self._generate_suggestions(score, response_text, question_type)
        
        # Generate personalized feedback
        personalized_feedback = self._generate_personalized_feedback(
            response_text, question_text, overall_score, strengths, weaknesses
        )
        
        # Generate improvement roadmap
        improvement_plan = self._create_improvement_plan(score, question_type)
        
        return {
            'strengths': strengths,
            'weaknesses': weaknesses,
            'suggestions': suggestions,
            'personalized_feedback': personalized_feedback,
            'improvement_plan': improvement_plan,
            'score_breakdown': self._create_score_breakdown(score),
            'next_steps': self._suggest_next_steps(score, question_type)
        }
    
    def _identify_strengths(self, score: ResponseScore, text: str, question_type: str) -> List[str]:
        """Identify strengths based on scores and analysis"""
        strengths = []
        
        # Content relevance strengths
        if score.content_relevance_score >= 80:
            strengths.append("Excellent content relevance - directly addressed the question")
        elif score.content_relevance_score >= 70:
            strengths.append("Good content relevance - mostly addressed the question")
        
        # Communication clarity strengths
        if score.communication_clarity_score >= 80:
            strengths.append("Clear and articulate communication")
        elif score.communication_clarity_score >= 70:
            strengths.append("Generally clear communication")
        
        # Structure strengths
        if score.structure_organization_score >= 80:
            strengths.append("Well-organized and structured response")
        elif score.structure_organization_score >= 70:
            strengths.append("Good response structure")
        
        # Technical accuracy (if applicable)
        if score.technical_accuracy_score and score.technical_accuracy_score >= 80:
            strengths.append("Strong technical accuracy and knowledge")
        elif score.technical_accuracy_score and score.technical_accuracy_score >= 70:
            strengths.append("Good technical understanding")
        
        # Word count and detail
        if score.word_count and score.word_count >= 100:
            strengths.append("Provided detailed and comprehensive response")
        
        # Confidence indicators
        if score.confidence_indicators and score.confidence_indicators >= 3:
            strengths.append("Demonstrated confidence in responses")
        
        # Sentiment analysis
        if score.sentiment_score and score.sentiment_score > 0.3:
            strengths.append("Positive and enthusiastic tone")
        
        # Vocabulary diversity
        if (score.word_count and score.unique_words_count and 
            score.unique_words_count / score.word_count > 0.7):
            strengths.append("Rich vocabulary and varied expression")
        
        # Ensure we have at least some strengths
        if not strengths:
            strengths.append("Attempted to provide a response")
            if score.word_count and score.word_count > 20:
                strengths.append("Provided a substantive answer")
        
        return strengths[:5]  # Limit to top 5 strengths
    
    def _identify_weaknesses(self, score: ResponseScore, text: str, question_type: str) -> List[str]:
        """Identify areas for improvement based on scores"""
        weaknesses = []
        
        # Content relevance issues
        if score.content_relevance_score < 60:
            weaknesses.append("Response could be more directly relevant to the question")
        
        # Communication clarity issues
        if score.communication_clarity_score < 60:
            weaknesses.append("Communication could be clearer and more articulate")
        
        # Structure issues
        if score.structure_organization_score < 60:
            weaknesses.append("Response structure and organization needs improvement")
        
        # Technical accuracy issues
        if (score.technical_accuracy_score and score.technical_accuracy_score < 60 
            and question_type == 'technical'):
            weaknesses.append("Technical accuracy and knowledge could be strengthened")
        
        # Filler words
        if score.filler_words_count and score.filler_words_count > 5:
            weaknesses.append("Reduce use of filler words (um, uh, like)")
        
        # Response length
        if score.word_count and score.word_count < 30:
            weaknesses.append("Response could be more detailed and comprehensive")
        elif score.word_count and score.word_count > 300:
            weaknesses.append("Response could be more concise and focused")
        
        # Confidence issues
        if score.confidence_indicators is not None and score.confidence_indicators == 0:
            weaknesses.append("Could demonstrate more confidence in responses")
        
        # Sentiment issues
        if score.sentiment_score and score.sentiment_score < -0.2:
            weaknesses.append("Could adopt a more positive tone")
        
        return weaknesses[:5]  # Limit to top 5 weaknesses
    
    def _generate_suggestions(self, score: ResponseScore, text: str, question_type: str) -> List[str]:
        """Generate specific improvement suggestions"""
        suggestions = []
        
        # Content improvement suggestions
        if score.content_relevance_score < 70:
            suggestions.append("Practice the STAR method (Situation, Task, Action, Result) for behavioral questions")
            suggestions.append("Ensure you directly answer what is being asked before adding additional context")
        
        # Communication improvement suggestions
        if score.communication_clarity_score < 70:
            suggestions.append("Practice speaking slowly and clearly")
            suggestions.append("Use simple, direct language to convey your points")
        
        # Structure improvement suggestions
        if score.structure_organization_score < 70:
            suggestions.append("Start with a brief overview, then provide details, and conclude with key takeaways")
            suggestions.append("Use transition words to connect your ideas smoothly")
        
        # Technical improvement suggestions
        if (score.technical_accuracy_score and score.technical_accuracy_score < 70 
            and question_type == 'technical'):
            suggestions.append("Review fundamental concepts related to the question topic")
            suggestions.append("Practice explaining technical concepts in simple terms")
        
        # Filler word reduction
        if score.filler_words_count and score.filler_words_count > 3:
            suggestions.append("Practice pausing instead of using filler words")
            suggestions.append("Record yourself speaking to identify and reduce filler word usage")
        
        # Length optimization
        if score.word_count and score.word_count < 50:
            suggestions.append("Provide specific examples to support your points")
            suggestions.append("Elaborate on your thought process and reasoning")
        
        # Confidence building
        if score.confidence_indicators is not None and score.confidence_indicators < 2:
            suggestions.append("Practice your responses out loud to build confidence")
            suggestions.append("Use definitive language instead of uncertain phrases")
        
        # General suggestions
        suggestions.append("Practice mock interviews to improve overall performance")
        suggestions.append("Research common interview questions for your field")
        
        return suggestions[:6]  # Limit to top 6 suggestions
    
    def _generate_personalized_feedback(self, text: str, question: str, 
                                      score: int, strengths: List[str], 
                                      weaknesses: List[str]) -> str:
        """Generate personalized feedback using AI if available"""
        if not self.client:
            return self._generate_template_feedback(score, strengths, weaknesses)
        
        try:
            prompt = f"""
            Provide encouraging and constructive feedback for this interview response:
            
            Question: {question}
            Response: {text}
            Score: {score}/100
            
            Key Strengths: {', '.join(strengths)}
            Areas for Improvement: {', '.join(weaknesses)}
            
            Write a personalized, encouraging feedback message that:
            1. Acknowledges their strengths
            2. Provides specific, actionable advice for improvement
            3. Maintains a positive, supportive tone
            4. Is 3-4 sentences long
            
            Focus on being helpful and motivating.
            """
            
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a supportive interview coach providing constructive feedback."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=200
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            print(f"Error generating personalized feedback: {e}")
            return self._generate_template_feedback(score, strengths, weaknesses)
    
    def _generate_template_feedback(self, score: int, strengths: List[str], 
                                  weaknesses: List[str]) -> str:
        """Generate template-based feedback when AI is not available"""
        if score >= 80:
            tone = "Excellent work!"
        elif score >= 70:
            tone = "Good job!"
        elif score >= 60:
            tone = "Nice effort!"
        else:
            tone = "Keep practicing!"
        
        feedback = f"{tone} "
        
        if strengths:
            feedback += f"Your response showed {strengths[0].lower()}. "
        
        if weaknesses:
            feedback += f"To improve further, focus on {weaknesses[0].lower()}. "
        
        feedback += "Keep practicing and you'll continue to improve!"
        
        return feedback
    
    def _create_improvement_plan(self, score: ResponseScore, question_type: str) -> Dict:
        """Create a structured improvement plan"""
        plan = {
            'immediate_focus': [],
            'short_term_goals': [],
            'long_term_development': []
        }
        
        # Immediate focus (next 1-2 practice sessions)
        if score.filler_words_count and score.filler_words_count > 5:
            plan['immediate_focus'].append("Practice reducing filler words")
        
        if score.structure_organization_score < 60:
            plan['immediate_focus'].append("Work on response structure using STAR method")
        
        # Short-term goals (next 2-4 weeks)
        if score.communication_clarity_score < 70:
            plan['short_term_goals'].append("Improve communication clarity through regular practice")
        
        if score.content_relevance_score < 70:
            plan['short_term_goals'].append("Practice answering questions more directly and relevantly")
        
        # Long-term development (1-3 months)
        if question_type == 'technical' and score.technical_accuracy_score and score.technical_accuracy_score < 70:
            plan['long_term_development'].append("Deepen technical knowledge in relevant areas")
        
        plan['long_term_development'].append("Build confidence through consistent practice")
        plan['long_term_development'].append("Develop a personal library of examples and stories")
        
        return plan
    
    def _create_score_breakdown(self, score: ResponseScore) -> Dict:
        """Create a detailed score breakdown with explanations"""
        breakdown = {
            'overall': {
                'score': score.overall_score,
                'interpretation': self._interpret_score(score.overall_score)
            },
            'content_relevance': {
                'score': score.content_relevance_score,
                'interpretation': self._interpret_score(score.content_relevance_score)
            },
            'communication_clarity': {
                'score': score.communication_clarity_score,
                'interpretation': self._interpret_score(score.communication_clarity_score)
            },
            'structure_organization': {
                'score': score.structure_organization_score,
                'interpretation': self._interpret_score(score.structure_organization_score)
            }
        }
        
        if score.technical_accuracy_score:
            breakdown['technical_accuracy'] = {
                'score': score.technical_accuracy_score,
                'interpretation': self._interpret_score(score.technical_accuracy_score)
            }
        
        return breakdown
    
    def _interpret_score(self, score: int) -> str:
        """Interpret numerical score into descriptive text"""
        if score >= 90:
            return "Excellent"
        elif score >= 80:
            return "Very Good"
        elif score >= 70:
            return "Good"
        elif score >= 60:
            return "Satisfactory"
        elif score >= 50:
            return "Needs Improvement"
        else:
            return "Requires Significant Improvement"
    
    def _suggest_next_steps(self, score: ResponseScore, question_type: str) -> List[str]:
        """Suggest specific next steps for improvement"""
        next_steps = []
        
        # Based on overall performance
        if score.overall_score < 60:
            next_steps.append("Schedule additional practice sessions")
            next_steps.append("Review basic interview techniques")
        elif score.overall_score < 80:
            next_steps.append("Focus on specific weak areas identified")
            next_steps.append("Practice with similar question types")
        else:
            next_steps.append("Maintain current performance level")
            next_steps.append("Challenge yourself with more difficult questions")
        
        # Question type specific suggestions
        if question_type == 'behavioral':
            next_steps.append("Prepare more STAR method examples")
        elif question_type == 'technical':
            next_steps.append("Review technical concepts and practice explanations")
        elif question_type == 'situational':
            next_steps.append("Practice problem-solving scenarios")
        
        next_steps.append("Record yourself practicing to self-evaluate")
        
        return next_steps[:4]  # Limit to 4 next steps
