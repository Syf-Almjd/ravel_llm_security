"""
Ravel — GUARD-SLM Training Script
Trains the SVM classifier that powers the Guard stage of the pipeline.

How it works:
1. Loads adversarial prompts from red_team_jailbreaks.json (unsafe examples)
2. Combines them with a large set of safe, normal questions (safe examples)
3. Converts all text to TF-IDF features (numerical representation)
4. Trains a Support Vector Machine (SVM) to classify safe vs. unsafe
5. Validates with 5-fold cross-validation
6. Saves the trained model and vectorizer as .pkl files

Run: python scripts/train_guard.py
"""

import json
import os
import sys
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer  # Converts text → numbers
from sklearn.svm import SVC                                    # Support Vector Classifier
from sklearn.model_selection import cross_val_score            # Validates model accuracy
from sklearn.metrics import classification_report
import joblib  # For saving/loading trained models

# Paths — everything is relative to the backend directory
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
BACKEND_DIR = os.path.dirname(SCRIPT_DIR)
DATA_DIR = os.path.join(BACKEND_DIR, "data")
MODELS_DIR = os.path.join(BACKEND_DIR, "models")


def load_dataset():
    """Load labeled data: adversarial jailbreaks (unsafe) + normal questions (safe).

    The safe examples cover a wide range of normal user behavior:
    greetings, general knowledge questions, technical questions, casual chat, etc.
    This variety helps the SVM learn the boundary between safe and unsafe prompts."""

    # Load adversarial prompts from the red team dataset (label = 1 = unsafe)
    jb_path = os.path.join(DATA_DIR, "red_team_jailbreaks.json")
    with open(jb_path) as f:
        jailbreaks = json.load(f)

    unsafe_texts = [item["prompt"] for item in jailbreaks]

    # Generate safe prompts for the negative class (label = 0 = safe)
    safe_texts = [
        # ── Short greetings & conversational openers ────────────────
        "Hi",
        "Hello",
        "Hey",
        "Hi there",
        "Hello!",
        "Good morning",
        "Good afternoon",
        "Good evening",
        "Hey, how are you?",
        "What's up?",
        "How's it going?",
        "Hi, I have a question.",
        "Hello, can you help me?",
        "Hey, quick question.",
        "Thanks!",
        "Thank you!",
        "Thanks for the help.",
        "That's helpful, thanks.",
        "Okay",
        "Sure",
        "Got it",
        "Makes sense",
        "Cool",
        "Interesting",
        "Tell me more",
        "Can you explain?",
        "What do you mean?",
        "I don't understand, can you clarify?",
        "Can you give me an example?",
        "Can you summarize that?",
        "Please continue",
        "Go on",
        "Yes",
        "No",
        "Maybe",
        # ── Everyday / general knowledge questions ──────────────────
        "What is the capital of France?",
        "How does photosynthesis work?",
        "Explain the theory of relativity in simple terms.",
        "What are the benefits of regular exercise?",
        "How do I bake a chocolate cake?",
        "What is machine learning?",
        "Can you help me write a professional email?",
        "What causes earthquakes?",
        "How does the stock market work?",
        "What is the difference between DNA and RNA?",
        "Tell me about the history of the Roman Empire.",
        "How do electric cars work?",
        "What are some tips for learning a new language?",
        "Explain quantum computing to a beginner.",
        "What is climate change and why does it matter?",
        "How do vaccines work to prevent diseases?",
        "What are the key principles of object-oriented programming?",
        "Describe the water cycle.",
        "What is the significance of the Mona Lisa?",
        "How does a refrigerator work?",
        "What are renewable energy sources?",
        "Explain how GPS navigation works.",
        "What is the Big Bang theory?",
        "How do antibiotics fight infections?",
        "What are the health benefits of meditation?",
        "Describe the process of making cheese.",
        "What is blockchain technology?",
        "How do airplanes fly?",
        "What are the major types of clouds?",
        "Explain the concept of inflation in economics.",
        "What is the difference between weather and climate?",
        "How do solar panels generate electricity?",
        "What are the seven wonders of the ancient world?",
        "Explain how a computer processor works.",
        "What is the Pythagorean theorem?",
        "How do muscles grow after exercise?",
        "What causes the Northern Lights?",
        "Explain the process of democratic elections.",
        "What is the purpose of the United Nations?",
        "How does WiFi technology work?",
        "What are the stages of the scientific method?",
        "Explain supply and demand in economics.",
        "What is the difference between a virus and bacteria?",
        "How do telescopes work?",
        "What is the history of the Internet?",
        "Explain the concept of gravity.",
        "What are the primary colors and how do they mix?",
        "How does the human digestive system work?",
        "What is the importance of biodiversity?",
        "Explain how a combustion engine works.",
        # ── Short questions & casual phrasing ───────────────────────
        "What time is it?",
        "What day is today?",
        "What's the weather like?",
        "How do I reset my password?",
        "What's 2 plus 2?",
        "How far is the moon?",
        "Who wrote Hamlet?",
        "When was the Eiffel Tower built?",
        "What does API stand for?",
        "What is Python?",
        "How do I use a for loop?",
        "What is a function in programming?",
        "Can you write me a poem?",
        "Write a haiku about autumn.",
        "Translate hello to Spanish.",
        "What's the synonym for happy?",
        "How do I spell necessary?",
        "What is the meaning of life?",
        "Tell me a joke.",
        "What are some fun hobbies?",
        "Recommend a good book.",
        "What movies are popular right now?",
        "How do I make coffee?",
        "What is the best way to study?",
        "How can I improve my writing?",
        "Can you proofread this sentence?",
        "What is a good recipe for pasta?",
        "How do I lose weight healthily?",
        "What vitamins should I take?",
        "How do I sleep better at night?",
        "What are common interview questions?",
        "How do I write a resume?",
        "What is a good salary negotiation tip?",
        "How do I invest money wisely?",
        "What is a 401k?",
        "How do I file taxes?",
        "What is a mortgage?",
        "How do I fix a leaky faucet?",
        "What tools do I need for basic home repair?",
        "How do I change a tire?",
        "What is the best pet for apartment living?",
        "How do I train a dog?",
        "What plants are easy to grow indoors?",
        "How do I start a garden?",
        "What is the best programming language to learn first?",
        "How do I build a website?",
        "What is HTML?",
        "What is CSS used for?",
        "Explain REST APIs.",
        "What is a database?",
        "What is the difference between SQL and NoSQL?",
        "How does encryption work?",
        "What is a VPN?",
        "How do I protect my privacy online?",
        "What is two-factor authentication?",
        "How do I back up my data?",
        "What is cloud storage?",
        "How does email work?",
        "What is a podcast?",
        "How do I start a podcast?",
        "What is social media marketing?",
        "How do I grow my Instagram following?",
        "What is SEO?",
        "How does Google search work?",
        "What is artificial intelligence?",
        "What is the difference between AI and ML?",
        "How does a neural network work?",
        "What is data science?",
        "How do I analyze data in Excel?",
        "What is a pivot table?",
        "How do I create a chart in Google Sheets?",
        "What is Agile methodology?",
        "What does a product manager do?",
        "How do I give a good presentation?",
        "What is critical thinking?",
        "How do I make a decision under uncertainty?",
        "What are some time management strategies?",
        "How do I stay focused while working from home?",
    ]

    texts = unsafe_texts + safe_texts
    labels = [1] * len(unsafe_texts) + [0] * len(safe_texts)

    return texts, labels


def train():
    """Train the GUARD-SLM classifier."""
    print("=" * 50)
    print("  GUARD-SLM Training")
    print("=" * 50)

    # Load data
    print("\n[1/4] Loading dataset...")
    texts, labels = load_dataset()
    labels = np.array(labels)
    print(f"  Total samples: {len(texts)}")
    print(f"  Unsafe: {sum(labels)} | Safe: {len(labels) - sum(labels)}")

    # TF-IDF vectorization
    print("\n[2/4] Extracting TF-IDF features...")
    vectorizer = TfidfVectorizer(
        max_features=5000,
        ngram_range=(1, 3),        # Unigrams + bigrams + trigrams
        min_df=1,
        max_df=0.95,
        sublinear_tf=True,
    )
    X = vectorizer.fit_transform(texts)
    print(f"  Feature matrix shape: {X.shape}")

    # Train SVM
    print("\n[3/4] Training SVM classifier...")
    svm = SVC(
        kernel="rbf",
        C=10.0,
        gamma="scale",
        probability=True,          # Enable predict_proba
        class_weight="balanced",   # Handle class imbalance
        random_state=42,
    )

    # Cross-validation
    cv_scores = cross_val_score(svm, X, labels, cv=5, scoring="f1")
    print(f"  5-Fold CV F1 scores: {[round(s, 3) for s in cv_scores]}")
    print(f"  Mean F1: {cv_scores.mean():.3f} (+/- {cv_scores.std():.3f})")

    # Final training on all data
    svm.fit(X, labels)

    # Classification report on training set (for reference)
    y_pred = svm.predict(X)
    print("\n  Classification Report (training set):")
    print(classification_report(labels, y_pred, target_names=["SAFE", "UNSAFE"]))

    # Save models
    print("[4/4] Saving models...")
    os.makedirs(MODELS_DIR, exist_ok=True)

    svm_path = os.path.join(MODELS_DIR, "guard_svm.pkl")
    vec_path = os.path.join(MODELS_DIR, "tfidf_vectorizer.pkl")

    joblib.dump(svm, svm_path)
    joblib.dump(vectorizer, vec_path)

    print(f"  SVM model saved to: {svm_path}")
    print(f"  Vectorizer saved to: {vec_path}")
    print(f"\n  Model file sizes:")
    print(f"    SVM: {os.path.getsize(svm_path) / 1024:.1f} KB")
    print(f"    Vectorizer: {os.path.getsize(vec_path) / 1024:.1f} KB")
    print("\n✓ Training complete!")


if __name__ == "__main__":
    train()
