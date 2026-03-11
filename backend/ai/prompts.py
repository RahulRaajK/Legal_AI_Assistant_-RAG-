"""Curated prompt templates for Indian legal AI agents."""

SYSTEM_PROMPT = """You are an expert AI Legal Assistant specialized in Indian Law. You have deep knowledge of:
- Constitution of India (all articles and schedules)
- Bharatiya Nyaya Sanhita 2023 (replaced IPC)
- Bharatiya Nagarik Suraksha Sanhita 2023 (replaced CrPC)
- Bharatiya Sakshya Adhiniyam 2023 (replaced Evidence Act)
- Indian Penal Code (historical reference)
- Code of Criminal Procedure (historical reference)
- Code of Civil Procedure
- Evidence Act (historical reference)
- All major Indian statutes and regulations
- Supreme Court and High Court judgments
- Legal precedents and principles

You ALWAYS:
1. Cite specific Act names, Section numbers, and Article numbers
2. Reference relevant case law with proper citations
3. Explain legal concepts in clear, structured format
4. Distinguish between current and repealed laws
5. Provide balanced analysis of legal issues

Format your responses with:
- **Title** of the legal topic
- **Relevant Acts/Sections** cited
- **Explanation** in clear language
- **Key Points** as bullet points
- **Case References** if applicable
- **Legal Reasoning** analysis
"""

LAW_SUMMARIZATION_PROMPT = """Based on the following legal text and context, provide a comprehensive summary.

LEGAL CONTEXT:
{context}

USER QUERY: {query}

Provide your response in this exact format:

## {title}

### Relevant Acts & Sections
- List each relevant act and section

### Summary
Provide a clear, plain-language summary of the law/section.

### Key Points
- Point 1
- Point 2
- Point 3

### Legal Interpretation
How courts have interpreted this provision.

### Practical Application
How this applies in real-world scenarios.

### Important Case References
- Case Name (Year) - Key ruling
"""

CASE_ANALYSIS_PROMPT = """Analyze the following case details and provide legal insights.

CASE FACTS:
{facts}

RELEVANT LEGAL CONTEXT:
{context}

Previous similar cases:
{precedents}

Provide your analysis in this format:

## Case Analysis

### Applicable Laws
- List specific acts and sections that apply

### Analysis of Facts
Analyze each key fact in light of applicable law.

### Precedent Analysis
Compare with similar past cases and their outcomes.

### Arguments For the Petitioner
1. Argument 1 with legal basis
2. Argument 2 with legal basis

### Arguments For the Respondent
1. Counter-argument 1
2. Counter-argument 2

### Possible Outcomes
- Scenario 1 with probability assessment
- Scenario 2 with probability assessment

### Recommendation
Overall assessment and recommended strategy.
"""

ARGUMENT_GENERATION_PROMPT = """Generate legal arguments for the {side} side.

CASE DETAILS:
{case_details}

RELEVANT LAWS:
{context}

RELEVANT PRECEDENTS:
{precedents}

Generate comprehensive arguments:

## Legal Arguments for {side}

### Primary Arguments
1. **Argument**: [State the argument]
   **Legal Basis**: [Cite specific section/article]
   **Supporting Case Law**: [Cite relevant case]
   **Reasoning**: [Explain why this argument is strong]

### Secondary Arguments
[Same format]

### Anticipating Counter-Arguments
For each primary argument, identify potential counter-arguments and prepare rebuttals.

### Evidence Requirements
List what evidence would strengthen each argument.
"""

WIN_PROBABILITY_PROMPT = """Based on the analysis of the following case, estimate the probability of success.

CASE DETAILS:
{case_details}

APPLICABLE LAWS:
{context}

SIMILAR CASE OUTCOMES:
{precedents}

Provide your analysis:

## Case Win Probability Assessment

### Strength of Legal Position: [Strong/Moderate/Weak]

### Factor Analysis
| Factor | Score (1-10) | Reasoning |
|--------|-------------|-----------|
| Legal Merit | X | ... |
| Evidence Strength | X | ... |
| Precedent Support | X | ... |
| Procedural Compliance | X | ... |
| Judicial Tendency | X | ... |

### Estimated Success Probability: X%

### Key Risk Factors
- Risk 1
- Risk 2

### Recommendations to Improve Chances
- Suggestion 1
- Suggestion 2
"""

CITIZEN_EXPLAIN_PROMPT = """The user is a common citizen with no legal background. Explain the following legal matter in simple, easy-to-understand language. Avoid legal jargon and use everyday examples.

LEGAL CONTEXT:
{context}

USER QUESTION: {query}

## Understanding Your Legal Rights

### In Simple Words
[Explain in very simple language, as if explaining to a friend]

### What This Means For You
- Point 1
- Point 2

### What You Can Do
- Step-by-step guidance

### Where to Get Help
- Relevant authorities or resources

### Important Things to Remember
- Key takeaways
"""

DOCUMENT_QA_PROMPT = """Answer the user's question based on the uploaded document content.

DOCUMENT CONTENT:
{context}

USER QUESTION: {query}

Provide a thorough answer citing specific parts of the document.
"""

JUDGE_SUMMARY_PROMPT = """Provide a judicial summary of this case for a sitting judge.

CASE OVERVIEW:
{case_details}

APPLICABLE LAW:
{context}

PRECEDENTS:
{precedents}

## Judicial Summary

### Case Overview
Brief summary of facts and issues.

### Questions of Law
- Legal question 1
- Legal question 2

### Applicable Provisions
- Section/Article with relevance

### Key Precedents
- Case citations with holdings

### Points for Consideration
- Important factors the bench should consider

### Legal Framework Analysis
How the applicable law applies to the facts of this case.
"""
