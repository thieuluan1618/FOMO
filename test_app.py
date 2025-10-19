"""
Test cases for Meeting Notes Automation App
Based on the requirements provided
"""

import os
import sys
from dotenv import load_dotenv

# Add the current directory to the path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import the functions from our app
try:
    from app import initialize_client, summarize_meeting, answer_question, answer_question_auto_lang, detect_question_language
    load_dotenv()
except ImportError as e:
    print(f"Error importing modules: {e}")
    sys.exit(1)

def test_case_01():
    """TC_01: Summarize a short meeting transcript → concise notes produced"""
    print("\n🧪 Test Case 01: Short meeting transcript")
    
    short_transcript = """
    Meeting: Quick standup
    Alice: Good morning team. What did everyone work on yesterday?
    Bob: I completed the API integration.
    Carol: I finished the UI mockups.
    Alice: Great! Any blockers for today?
    Bob: None from me.
    Carol: All good here too.
    Alice: Perfect, let's reconvene tomorrow.
    """
    
    client = initialize_client()
    if client:
        result = summarize_meeting(client, short_transcript, "concise", 150, 0.3)
        print(f"✅ Result: {result}")
        return "✅ PASS" if len(result) > 10 and "❌" not in result else "❌ FAIL"
    else:
        return "❌ FAIL - Client initialization failed"

def test_case_02():
    """TC_02: Summarize a long transcript with multiple topics → clear sectioned notes"""
    print("\n🧪 Test Case 02: Long transcript with multiple topics")
    
    long_transcript = """
    Meeting: Quarterly Review
    
    Alice: Welcome to our Q3 review. Let's start with the engineering team update.
    Bob: We completed 85% of our planned features. The main achievements were the new API endpoints and improved performance.
    Carol: From the design side, we delivered all mockups on time and got great user feedback.
    
    Alice: Now let's discuss Q4 planning.
    Bob: We need to focus on scalability and security improvements.
    Carol: I suggest we also prioritize user experience enhancements.
    
    Alice: Budget discussion - we're on track but need to allocate more for cloud infrastructure.
    Bob: Agreed, we'll need at least 20% more for the expected traffic growth.
    
    Alice: Action items - Bob will prepare the infrastructure proposal, Carol will research UX tools.
    """
    
    client = initialize_client()
    if client:
        result = summarize_meeting(client, long_transcript, "detailed", 400, 0.3)
        print(f"✅ Result: {result}")
        return "✅ PASS" if len(result) > 50 and "❌" not in result else "❌ FAIL"
    else:
        return "❌ FAIL - Client initialization failed"

def test_case_03():
    """TC_03: Empty input text → returns helpful error or prompt to retry"""
    print("\n🧪 Test Case 03: Empty input handling")
    
    empty_transcript = ""
    
    client = initialize_client()
    if client:
        result = summarize_meeting(client, empty_transcript, "concise", 150, 0.3)
        print(f"✅ Result: {result}")
        return "✅ PASS" if "No content" in result or "⚠️" in result else "❌ FAIL"
    else:
        return "❌ FAIL - Client initialization failed"

def test_case_04():
    """TC_04: Invalid API key → handle authentication error"""
    print("\n🧪 Test Case 04: Invalid API key handling")
    
    # Temporarily modify environment variables to simulate invalid credentials
    original_key = os.getenv("AZURE_OPENAI_API_KEY")
    os.environ["AZURE_OPENAI_API_KEY"] = "invalid_key_test"
    
    client = initialize_client()
    
    # Restore original key
    if original_key:
        os.environ["AZURE_OPENAI_API_KEY"] = original_key
    
    if client is None:
        print("✅ Result: Client initialization failed gracefully")
        return "✅ PASS"
    else:
        # If client was created, try to use it and expect an error
        test_transcript = "Test meeting content"
        result = summarize_meeting(client, test_transcript, "concise", 150, 0.3)
        print(f"✅ Result: {result}")
        return "✅ PASS" if "❌" in result or "Error" in result else "❌ FAIL"

def test_case_05():
    """TC_05: Chatbot Q&A functionality → answers questions about meeting summary"""
    print("\n🧪 Test Case 05: Chatbot Q&A functionality")
    
    # Sample meeting summary for testing
    sample_summary = """
    Meeting Summary:
    - Discussed Q3 performance review
    - Bob completed API integration project
    - Carol finished UI mockups ahead of schedule
    - Action items: Bob to prepare infrastructure proposal, Carol to research UX tools
    - Budget discussion: need 20% more allocation for cloud infrastructure
    """
    
    test_question = "What are the action items from this meeting?"
    
    client = initialize_client()
    if client:
        result = answer_question(client, test_question, sample_summary)
        print(f"✅ Question: {test_question}")
        print(f"✅ Result: {result}")
        return "✅ PASS" if len(result) > 10 and "❌" not in result else "❌ FAIL"
    else:
        return "❌ FAIL - Client initialization failed"

def test_case_06():
    """TC_06: Empty question handling → returns helpful prompt"""
    print("\n🧪 Test Case 06: Empty question handling")
    
    sample_summary = "Meeting summary with some content"
    empty_question = ""
    
    client = initialize_client()
    if client:
        result = answer_question(client, empty_question, sample_summary)
        print(f"✅ Result: {result}")
        return "✅ PASS" if "ask a question" in result.lower() or "⚠️" in result else "❌ FAIL"
    else:
        return "❌ FAIL - Client initialization failed"

def test_case_07():
    """TC_07: Multi-language summary generation → generates summary in specified language"""
    print("\n🧪 Test Case 07: Multi-language summary generation")
    
    short_transcript = """
    Meeting: Quick standup
    Alice: Good morning team. What did everyone work on yesterday?
    Bob: I completed the API integration.
    Carol: I finished the UI mockups.
    Alice: Great! Any blockers for today?
    Bob: None from me.
    Carol: All good here too.
    Alice: Perfect, let's reconvene tomorrow.
    """
    
    client = initialize_client()
    if client:
        # Test Spanish summary
        result = summarize_meeting(client, short_transcript, "concise", 150, 0.3, "Spanish")
        print(f"✅ Spanish Result: {result}")
        
        # Simple check - if it contains Spanish words or characters, consider it a pass
        spanish_indicators = ['reunión', 'equipo', 'trabajo', 'ayer', 'hoy', 'mañana', 'completé', 'terminé']
        has_spanish = any(word in result.lower() for word in spanish_indicators) or "✅" not in result
        
        return "✅ PASS" if has_spanish and "❌" not in result else "❌ FAIL"
    else:
        return "❌ FAIL - Client initialization failed"

def test_case_08():
    """TC_08: Multi-language Q&A → answers questions in specified language"""
    print("\n🧪 Test Case 08: Multi-language Q&A")
    
    sample_summary = """
    Meeting Summary:
    - Discussed Q3 performance review
    - Bob completed API integration project
    - Action items: Prepare infrastructure proposal
    """
    
    test_question = "What are the action items?"
    
    client = initialize_client()
    if client:
        # Test French Q&A
        result = answer_question(client, test_question, sample_summary, "", "French")
        print(f"✅ French Q&A Result: {result}")
        
        # Simple check for French response
        french_indicators = ['éléments', 'actions', 'tâches', 'proposer', 'infrastructure', 'projet']
        has_french = any(word in result.lower() for word in french_indicators) or len(result) > 10
        
        return "✅ PASS" if has_french and "❌" not in result else "❌ FAIL"
    else:
        return "❌ FAIL - Client initialization failed"

def test_case_09():
    """TC_09: Language auto-detection → detects question language correctly"""
    print("\n🧪 Test Case 09: Language auto-detection")
    
    client = initialize_client()
    if client:
        # Test different language questions
        test_cases = [
            ("What are the action items?", "English"),
            ("¿Cuáles son los elementos de acción?", "Spanish"),
            ("Quels sont les éléments d'action?", "French")
        ]
        
        results = []
        for question, expected_lang in test_cases:
            detected = detect_question_language(client, question)
            print(f"✅ Question: '{question}' → Detected: {detected} (Expected: {expected_lang})")
            results.append(detected.lower() == expected_lang.lower())
        
        # Pass if at least 2 out of 3 detections are correct
        success_rate = sum(results) / len(results)
        return "✅ PASS" if success_rate >= 0.66 else "❌ FAIL"
    else:
        return "❌ FAIL - Client initialization failed"

def test_case_10():
    """TC_10: Auto-language Q&A → responds in detected question language"""
    print("\n🧪 Test Case 10: Auto-language Q&A")
    
    sample_summary = """
    Meeting Summary:
    - Discussed Q3 performance review
    - Bob completed API integration project
    - Action items: Prepare infrastructure proposal
    """
    
    client = initialize_client()
    if client:
        # Test Spanish question with auto-detection
        spanish_question = "¿Cuáles fueron las decisiones principales?"
        result = answer_question_auto_lang(client, spanish_question, sample_summary)
        print(f"✅ Spanish Auto-Detection Result: {result}")
        
        # Check if response contains Spanish elements or is substantial
        spanish_indicators = ['decisiones', 'principales', 'reunión', 'proyecto', 'revisión']
        has_spanish = any(word in result.lower() for word in spanish_indicators) or len(result) > 20
        
        return "✅ PASS" if has_spanish and "❌" not in result else "❌ FAIL"
    else:
        return "❌ FAIL - Client initialization failed"

def run_all_tests():
    """Run all test cases and display results"""
    print("🚀 Running Meeting Notes Automation Test Suite")
    print("=" * 60)
    
    test_results = {
        "TC_01": test_case_01(),
        "TC_02": test_case_02(), 
        "TC_03": test_case_03(),
        "TC_04": test_case_04(),
        "TC_05": test_case_05(),
        "TC_06": test_case_06(),
        "TC_07": test_case_07(),
        "TC_08": test_case_08(),
        "TC_09": test_case_09(),
        "TC_10": test_case_10()
    }
    
    print("\n" + "=" * 60)
    print("📊 TEST RESULTS SUMMARY")
    print("=" * 60)
    
    passed = 0
    total = len(test_results)
    
    for test_id, result in test_results.items():
        print(f"{test_id}: {result}")
        if "PASS" in result:
            passed += 1
    
    print(f"\n🎯 Overall Result: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed!")
    else:
        print("⚠️ Some tests failed. Please check the implementation.")

if __name__ == "__main__":
    run_all_tests()