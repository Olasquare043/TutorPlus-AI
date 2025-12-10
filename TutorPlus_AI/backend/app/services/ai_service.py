import logging
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM, BitsAndBytesConfig
from app.config import get_settings
from typing import Optional

logger = logging.getLogger(__name__)
settings = get_settings()


class AIService:
    """Service for AI/LLM operations using N-ATLaS model"""
    
    _instance = None
    _model = None
    _tokenizer = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(AIService, cls).__new__(cls)
        return cls._instance
    
    @classmethod
    def initialize(cls):
        """Initialize the model (call once at startup)"""
        if cls._model is not None:
            logger.info("Model already initialized")
            return
        
        try:
            logger.info(f"Initializing {settings.model_name}...")
            
            # Load tokenizer
            cls._tokenizer = AutoTokenizer.from_pretrained(
                settings.model_name,
                trust_remote_code=True,
            )
            logger.info("Tokenizer loaded")
            
            # Load model on CPU (no quantization for CPU)
            cls._model = AutoModelForCausalLM.from_pretrained(
                settings.model_name,
                trust_remote_code=True,
                device_map="cpu",
                torch_dtype=torch.float32,
                low_cpu_mem_usage=True,
            )
            logger.info(f"Model {settings.model_name} loaded successfully on CPU")
            
        except Exception as e:
            logger.error(f"Failed to initialize model: {str(e)}")
            raise
    
    @classmethod
    def get_model(cls):
        """Get the loaded model instance"""
        if cls._model is None:
            cls.initialize()
        return cls._model
    
    @classmethod
    def get_tokenizer(cls):
        """Get the loaded tokenizer instance"""
        if cls._tokenizer is None:
            cls.initialize()
        return cls._tokenizer
    
    @staticmethod
    def build_multilingual_prompt(
        query: str,
        language: str = "en",
        context: Optional[str] = None,
        system_role: str = "tutor"
    ) -> str:
        """Build a multilingual prompt for the model"""
        
        language_instructions = {
            "en": "Respond in English. Be clear, concise, and educational.",
            "yo": "Respond in Yoruba. Be clear, concise, and educational.",
            "ha": "Respond in Hausa. Be clear, concise, and educational.",
            "ig": "Respond in Igbo. Be clear, concise, and educational.",
        }
        
        system_prompts = {
            "tutor": "You are an expert Nigerian secondary school tutor. Provide clear, educational explanations tailored to students.",
            "mcq_generator": "You are an expert at creating multiple-choice questions for Nigerian secondary school exams.",
            "evaluator": "You are an expert at evaluating student answers and providing constructive feedback.",
        }
        
        lang_instruction = language_instructions.get(language, language_instructions["en"])
        system_prompt = system_prompts.get(system_role, system_prompts["tutor"])
            
        prompt = f"""System: {system_prompt}
            {lang_instruction}

            Context: {context if context else "General knowledge question"}

            Query: {query}

            Response:"""
        return prompt
    
    @staticmethod
    async def generate_text(
        query: str,
        language: str = "en",
        context: Optional[str] = None,
        max_tokens: int = 512,
        temperature: float = 0.5,
        system_role: str = "tutor"
        ) -> str:
        """Generate text response using N-ATLaS model with RAG context"""
        
        try:
            logger.info(f"Generating response for query: {query[:50]}...")
            
            model = AIService.get_model()
            tokenizer = AIService.get_tokenizer()
            
            # Build strict RAG prompt
            if context:
                prompt = f"""You are a helpful Nigerian secondary school tutor. Answer ONLY based on the curriculum context provided below.

                IMPORTANT RULES:
                1. ONLY use information from the CURRICULUM CONTEXT below
                2. If the context doesn't answer the question, say: "I don't have information about this in the curriculum"
                3. Do NOT make up information
                4. Do NOT hallucinate
                5. Be accurate and educational

                CURRICULUM CONTEXT:
                {context}

                STUDENT QUESTION: {query}

                ANSWER (based ONLY on curriculum context above):"""
            else:
                prompt = f"""Answer this question clearly and educationally:

                Question: {query}

                Answer:"""
                            
            # Tokenize
            inputs = tokenizer(prompt, return_tensors="pt")
            inputs = {k: v.to(model.device) for k, v in inputs.items()}
            
            # Generate
            with torch.no_grad():
                outputs = model.generate(
                    **inputs,
                    max_new_tokens=max_tokens,
                    temperature=temperature,
                    top_p=0.9,
                    do_sample=True,
                    pad_token_id=tokenizer.eos_token_id,
                )
            
            # Decode
            response_text = tokenizer.decode(outputs[0], skip_special_tokens=True)
            
            # Extract response part (remove prompt from output)
            if "ANSWER" in response_text:
                response_text = response_text.split("ANSWER")[-1].strip()
            elif "Answer:" in response_text:
                response_text = response_text.split("Answer:")[-1].strip()
            
            logger.info("Response generated successfully")
            return response_text
            
        except Exception as e:
            logger.error(f"Text generation failed: {str(e)}")
            raise
    
    @staticmethod
    async def generate_mcq(
        subject: str,
        topic: str,
        number_of_questions: int = 5,
        difficulty: str = "medium",
        language: str = "en"
    ) -> str:
        """Generate MCQ questions using N-ATLaS"""
        
        try:
            logger.info(f"Generating {number_of_questions} MCQs for {subject} - {topic}")
            
            # Build a more specific prompt
            prompt = f"""You are an expert at creating multiple-choice questions for Nigerian secondary school exams.

            IMPORTANT: Generate questions ONLY about {subject} and {topic}. Do NOT generate questions about other subjects.

            Subject: {subject}
            Topic: {topic}
            Number of questions: {number_of_questions}
            Difficulty level: {difficulty}

            Generate {number_of_questions} multiple-choice questions ONLY about {subject} - {topic}.

            Format EXACTLY as follows:
            Q1: [Question text about {subject} and {topic}]
            A) [Option A]
            B) [Option B]
            C) [Option C]
            D) [Option D]
            Answer: [Correct option letter]
            Explanation: [Brief explanation]

            Q2: [Next question about {subject} and {topic}]
            A) [Option A]
            B) [Option B]
            C) [Option C]
            D) [Option D]
            Answer: [Correct option letter]
            Explanation: [Brief explanation]

            Continue for all {number_of_questions} questions.

            START GENERATING NOW:"""
            
            response = await AIService.generate_text(
                query=prompt,
                language=language,
                max_tokens=2048,
                temperature=0.7,
                system_role="mcq_generator"
            )
            
            return response
            
        except Exception as e:
            logger.error(f"MCQ generation failed: {str(e)}")
            raise
    
    @staticmethod
    async def evaluate_answer(
        question: str,
        student_answer: str,
        correct_answer: str,
        language: str = "en"
    ) -> dict:
        """Evaluate student answer and provide feedback"""
        
        try:
            logger.info("Evaluating student answer...")
            
            evaluation_prompt = f"""Evaluate this student's answer to a question.

            Question: {question}
            Student's Answer: {student_answer}
            Correct Answer: {correct_answer}

            Provide your evaluation in this exact format:
            1. Correct: Yes/No
            2. Score: (0-100)
            3. Feedback: (how to improve)
            4. Key Concepts: (what student should know)

            EVALUATION:"""
            
            response = await AIService.generate_text(
                query=evaluation_prompt,
                language=language,
                max_tokens=512,
                temperature=0.5,
                system_role="evaluator"
            )
            
            # Parse response
             # Parse response to extract score
            score = 0
            is_correct = False
            
            lines = response.lower().split("\n")
            
            # Extract correctness from first line
            if lines and len(lines) > 0:
                is_correct = "yes" in lines[0]
            
            # Extract score from response (look for "score: XX" pattern)
            import re
            score_match = re.search(r'score:\s*(\d+)', response.lower())
            if score_match:
                score = int(score_match.group(1))
            else:
                # Default score based on correctness
                score = 100 if is_correct else 50
            
            return {
                "is_correct": is_correct,
                "score": score,
                "feedback": response,
                "explanation": "Evaluation completed by AI tutor"
            }
            
        except Exception as e:
            logger.error(f"Answer evaluation failed: {str(e)}")
            raise