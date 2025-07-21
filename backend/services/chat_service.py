import google.generativeai as genai
from datetime import datetime
from fastapi import HTTPException
from config.settings import settings
from utils.storage import pdf_contexts, chat_histories
from models.chat import ChatMessage, ChatResponse

# Configure Gemini AI
genai.configure(api_key=settings.GEMINI_API_KEY)
model = genai.GenerativeModel(settings.GEMINI_MODEL)

class ChatService:
    @staticmethod
    async def chat(message: ChatMessage, token: str) -> ChatResponse:
        if token not in pdf_contexts:
            raise HTTPException(status_code=400, detail="No PDF selected. Please select a PDF first.")

        pdf_context = pdf_contexts[token]

        # Initialize chat history if not exists
        if token not in chat_histories:
            chat_histories[token] = []

        # Check if this is a Q&A generation request (needs full content)
        is_qa_generation = any(keyword in message.message.lower() for keyword in [
            'generate', 'create', 'analyze this document', 'questions', 'sections', 'comprehensive'
        ])

        # Use more content for Q&A generation, limited content for regular chat
        content_limit = 50000 if is_qa_generation else 15000
        pdf_content = pdf_context['content'][:content_limit]

        # Add indication if content was truncated
        content_suffix = "..." if len(pdf_context['content']) > content_limit else ""

        # Prepare context for Gemini
        context = f"""
        You are an AI assistant helping students learn from their selected PDF document.

        Document: {pdf_context['filename']}
        Content: {pdf_content}{content_suffix}

        Previous conversation:
        {chr(10).join([f"User: {msg['user']}{chr(10)}Assistant: {msg['assistant']}" for msg in chat_histories[token][-3:]])}

        Current question: {message.message}

        Please provide a helpful, educational response based on the document content and conversation history.
        """

        try:
            # Generate response using Gemini
            response = model.generate_content(context)
            ai_response = response.text

            # Store in chat history
            chat_histories[token].append({
                "user": message.message,
                "assistant": ai_response,
                "timestamp": datetime.now().isoformat()
            })

            return ChatResponse(
                response=ai_response,
                timestamp=datetime.now().isoformat()
            )

        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to generate response: {str(e)}")

    @staticmethod
    def get_chat_history(token: str) -> dict:
        if token not in chat_histories:
            return {"history": []}

        return {"history": chat_histories[token]}
    
    @staticmethod
    def clear_chat_history(token: str) -> dict:
        if token in chat_histories:
            chat_histories[token] = []
        return {"message": "Chat history cleared"}

    @staticmethod
    async def generate_questions(token: str, topic: str = None, count: int = 25) -> ChatResponse:
        if token not in pdf_contexts:
            raise HTTPException(status_code=400, detail="No PDF selected. Please select a PDF first.")

        pdf_context = pdf_contexts[token]

        # Get the full PDF content for question generation
        full_content = pdf_context['content']

        print(f"Generating questions for PDF: {pdf_context['filename']}")
        print(f"Content length: {len(full_content)} characters")
        print(f"Content preview: {full_content[:500]}...")

        # Check if content is too short
        if len(full_content.strip()) < 100:
            raise HTTPException(status_code=400, detail="Document content is too short to generate meaningful questions")

        # Prepare context for Gemini with full content
        topic_instruction = ""
        if topic and topic.strip():
            topic_instruction = f"""
        SPECIFIC TOPIC FOCUS: "{topic.strip()}"
        Focus your questions specifically on this topic, but use the full document content as context to ensure accuracy and completeness.
        """

        context = f"""
        You are an educational AI assistant. Analyze the following document content and create comprehensive questions for learning.

        Document: {pdf_context['filename']}
        {topic_instruction}

        FULL DOCUMENT CONTENT:
        {full_content}

        TASK: Create exactly {count} educational questions based on the document content above{' focusing on the specified topic' if topic and topic.strip() else ''}.

        REQUIREMENTS:
        1. Read and analyze the ENTIRE document content provided above
        2. {'Focus specifically on the topic: "' + topic.strip() + '" while using the full document as context' if topic and topic.strip() else 'Create questions that cover the full scope of the document'}
        3. Include questions about:
           - Key concepts and definitions from the text
           - Important details and facts mentioned
           - Practical applications discussed
           - Examples and case studies provided
           - Critical thinking questions about the content
           - Main themes and ideas
           - Specific processes or methods described
           - Important people, places, or events mentioned
           - Cause and effect relationships
           - Comparisons and contrasts made in the text

        FORMAT: Respond with ONLY a valid JSON object in this exact format:
        {{
          "questions": [
            "What is [specific concept from document]?",
            "How does [specific process from document] work?",
            "What are the key benefits of [specific topic] mentioned in the text?",
            "Can you explain the relationship between [concept A] and [concept B] as described?",
            "What examples are provided to illustrate [specific concept]?",
            "What are the main steps involved in [specific process from text]?",
            "How does the document define [important term]?",
            "What problems does [solution mentioned] solve according to the text?",
            "What are the different types of [category from document] mentioned?",
            "How can [concept from text] be applied in practice?",
            "What are the advantages and disadvantages of [approach from document]?",
            "What recommendations does the text make regarding [topic]?",
            "How does [concept] compare to [alternative] according to the document?",
            "What are the key takeaways from the document?",
            "What future implications are discussed for [topic from text]?",
            "Who are the main people mentioned in the document and what are their contributions?",
            "What are the most important facts or statistics presented?",
            "What real-world applications are discussed in the text?",
            "What challenges or problems are identified in the document?",
            "How does the author support their main arguments?",
            "What conclusions does the document reach?",
            "What are the practical implications of the concepts discussed?",
            "How do the different sections of the document relate to each other?",
            "What evidence is provided to support the main points?",
            "What questions does the document leave unanswered?"
          ]
        }}

        Make sure:
        - Questions are specific to the actual document content provided above
        - Each question can be answered using information from the document
        - Questions progress from basic to advanced understanding
        - {'Focus specifically on the topic "' + topic.strip() + '" while ensuring all questions can be answered from the document content' if topic and topic.strip() else 'Cover all major topics and themes in the document'}
        - Use actual terms, concepts, and examples from the text provided
        - Questions are diverse and cover different aspects of the {'specified topic' if topic and topic.strip() else 'content'}

        Generate exactly {count} questions now based on the full document content provided above{' focusing on the specified topic' if topic and topic.strip() else ''}.
        """

        try:
            # Generate response using Gemini
            print("Sending request to Gemini AI...")
            response = model.generate_content(context)

            if not response or not response.text:
                raise HTTPException(status_code=500, detail="AI service returned empty response")

            ai_response = response.text

            print(f"AI Response length: {len(ai_response)} characters")
            print(f"AI Response preview: {ai_response[:500]}...")

            # Validate that response contains JSON-like structure
            if '{' not in ai_response or '}' not in ai_response:
                print("Warning: Response doesn't appear to contain JSON structure")
                print(f"Full response: {ai_response}")

            return ChatResponse(
                response=ai_response,
                timestamp=datetime.now().isoformat()
            )

        except Exception as e:
            print(f"Error generating questions: {str(e)}")
            import traceback
            traceback.print_exc()
            raise HTTPException(status_code=500, detail=f"Failed to generate questions: {str(e)}")
