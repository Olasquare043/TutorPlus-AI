import logging
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM, BitsAndBytesConfig
from huggingface_hub import login, HfFolder
from app.config import get_settings
from typing import Optional

logger = logging.getLogger(__name__)
settings = get_settings()


class AIService:
    """Accelerate-enabled service for N-ATLaS model operations."""

    _instance = None
    _model = None
    _tokenizer = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(AIService, cls).__new__(cls)
        return cls._instance

    @classmethod
    def _authenticate_huggingface(cls):
        """Login to Hugging Face for gated model access."""
        try:
            if not settings.huggingface_api_key:
                raise ValueError("Huggingface API key missing (.env)")

            # Save token locally for auto-auth
            HfFolder.save_token(settings.huggingface_api_key)

            # Non-interactive login
            login(token=settings.huggingface_api_key, add_to_git_credential=False)

            logger.info("Authenticated with Hugging Face successfully.")

        except Exception as e:
            logger.error(f"Failed to authenticate Hugging Face: {str(e)}")
            raise

    @classmethod
    def initialize(cls):
        """Initialize/Load the model using Accelerate."""
        
        if cls._model is not None:
            logger.info("Model already initialized.")
            return

        try:
            cls._authenticate_huggingface()
            logger.info(f"Loading model: {settings.model_name}")

            # Load tokenizer
            cls._tokenizer = AutoTokenizer.from_pretrained(
                settings.model_name,
                trust_remote_code=True,
                token=settings.huggingface_api_key
            )
            logger.info("Tokenizer loaded.")
            # 4-bit quantization
            quant_config = BitsAndBytesConfig(
                load_in_4bit=True,
                bnb_4bit_compute_dtype=torch.float16,
                bnb_4bit_use_double_quant=True,
                bnb_4bit_quant_type="nf4"
            )

            # Load model with Accelerate (auto device placement + quantization)
            cls._model = AutoModelForCausalLM.from_pretrained(
                settings.model_name,
                trust_remote_code=True,
                device_map="auto",               # Accelerate handles CPU/GPU
                quantization_config=quant_config,               # quantization
                # torch_dtype=torch.float32,     # efficient precision
                token=settings.huggingface_api_key
            )

            logger.info(f"Model {settings.model_name} loaded using Accelerate.")

        except Exception as e:
            logger.error(f"Model initialization failed: {str(e)}")
            raise

    @classmethod
    def get_model(cls):
        if cls._model is None:
            cls.initialize()
        return cls._model

    @classmethod
    def get_tokenizer(cls):
        if cls._tokenizer is None:
            cls.initialize()
        return cls._tokenizer

    @staticmethod
    async def generate_text(
        query: str,
        language: str = "en",
        context: Optional[str] = None,
        max_tokens: int = 512,
        temperature: float = 0.5,
        system_role: str = "tutor"
    ) -> str:

        try:
            logger.info(f"Generating response for query: {query[:50]}...")

            model = AIService.get_model()
            tokenizer = AIService.get_tokenizer()

            # Construct prompt
            if context:
                prompt = f"""You are a helpful Nigerian secondary school tutor. Answer ONLY using the context below.

CONTEXT:
{context}

QUESTION:
{query}

ANSWER (strictly from context):"""
            else:
                prompt = f"Question: {query}\nAnswer:"

            # Tokenize input
            inputs = tokenizer(prompt, return_tensors="pt").to(model.device)

            # Generate
            with torch.no_grad():
                outputs = model.generate(
                    **inputs,
                    max_new_tokens=max_tokens,
                    temperature=temperature,
                    do_sample=True,
                    top_p=0.9,
                    pad_token_id=tokenizer.eos_token_id
                )

            # Decode output
            text = tokenizer.decode(outputs[0], skip_special_tokens=True)

            # Cleanup
            if "ANSWER" in text:
                text = text.split("ANSWER")[-1].strip()
            elif "Answer:" in text:
                text = text.split("Answer:")[-1].strip()

            return text

        except Exception as e:
            logger.error(f"Text generation failure: {str(e)}")
            raise
