from __future__ import annotations

from typing import Any

from app.prompts.datasets.example_factory import normalize_examples

ENGLISH_COMMON_QUALITY_CRITERIA = [
    "Write in natural, modern English.",
    "Make the post sound human, not AI-generated.",
    "Focus on one clear idea per post.",
    "Avoid vague motivational content.",
    "Use specific examples, trade-offs, or practical framing.",
    "Keep the writing concise and easy to read on Twitter/X.",
    "Avoid over-explaining.",
    "Avoid sounding too salesy or promotional.",
]


ENGLISH_TRAIN_EXAMPLES: list[dict[str, Any]] = [
    {
        "topic": "How AI automation helps founders save time on weekly content planning",
        "tone": "professional",
        "audience": "startup founders",
        "language": "English",
        "count": 1,
        "max_chars": 280,
        "include_hashtags": True,
        "quality_criteria": ENGLISH_COMMON_QUALITY_CRITERIA + [
            "Explain the value of AI automation without making it sound like a magic replacement.",
            "Position AI as a workflow assistant, not a founder substitute.",
        ],
        "avoid": [
            "Generic claims like 'AI saves time'.",
            "Overhyped AI language.",
            "More than 2 hashtags.",
        ],
        "reference_posts": [
            "AI does not replace a founder’s point of view. It removes the blank-page work: collecting ideas, drafting angles, and organizing the weekly plan so founders can spend more time refining the message. #AI #Startups"
        ],
    },
    {
        "topic": "Why approval workflows matter before auto-publishing social posts",
        "tone": "educational",
        "audience": "marketing teams",
        "language": "English",
        "count": 1,
        "max_chars": 280,
        "include_hashtags": False,
        "quality_criteria": ENGLISH_COMMON_QUALITY_CRITERIA + [
            "Explain approval workflows as a quality control layer.",
            "Make the risk of auto-publishing feel practical, not dramatic.",
        ],
        "avoid": [
            "Fear-based writing.",
            "Too much technical detail.",
            "Sounding like compliance documentation.",
        ],
        "reference_posts": [
            "Auto-publishing is useful until the wrong draft goes live on the wrong channel. Approval workflows are not just a delay. They protect brand voice, context, timing, and trust before automation scales the mistake."
        ],
    },
    {
        "topic": "Building realtime AI streaming UI with FastAPI and Next.js",
        "tone": "bold",
        "audience": "software developers",
        "language": "English",
        "count": 1,
        "max_chars": 280,
        "include_hashtags": True,
        "quality_criteria": ENGLISH_COMMON_QUALITY_CRITERIA + [
            "Make the engineering point clear and confident.",
            "Mention the user experience benefit of streaming UI.",
        ],
        "avoid": [
            "Buzzwords without implementation meaning.",
            "Too much framework comparison.",
            "More than 2 hashtags.",
        ],
        "reference_posts": [
            "A realtime AI UI is not just a spinner with better branding. With FastAPI streaming and Next.js, users can see the model think, fetch, draft, and refine step by step. The experience feels alive. #AI #NextJS"
        ],
    },
    {
        "topic": "Why small SaaS teams should document product decisions before shipping",
        "tone": "educational",
        "audience": "indie hackers",
        "language": "English",
        "count": 2,
        "max_chars": 240,
        "include_hashtags": False,
        "quality_criteria": ENGLISH_COMMON_QUALITY_CRITERIA + [
            "Make documentation feel lightweight, not bureaucratic.",
            "Show how decision notes help future product work.",
        ],
        "avoid": [
            "Enterprise-style process advice.",
            "Long documentation rituals.",
        ],
        "reference_posts": [
            "Small SaaS teams do not need heavy docs. They need decision notes: what changed, why it changed, and what trade-off was accepted. Future you will thank present you.",
            "Shipping fast is easier when decisions are written down. Otherwise every product debate gets reopened because nobody remembers why the team chose that path."
        ],
    },
    {
        "topic": "What founders misunderstand about using AI for customer support drafts",
        "tone": "contrarian",
        "audience": "B2B SaaS founders",
        "language": "English",
        "count": 1,
        "max_chars": 240,
        "include_hashtags": False,
        "quality_criteria": ENGLISH_COMMON_QUALITY_CRITERIA + [
            "Challenge a common assumption about AI support.",
            "Keep the tone sharp but reasonable.",
        ],
        "avoid": [
            "Anti-AI messaging.",
            "Overly aggressive contrarian takes.",
        ],
        "reference_posts": [
            "The mistake is not using AI for support drafts. The mistake is letting AI decide the tone. AI can prepare the response, but humans still need to own empathy, context, and judgment."
        ],
    },
    {
        "topic": "How product teams can use user interview notes to write better launch content",
        "tone": "insightful",
        "audience": "product marketers",
        "language": "English",
        "count": 2,
        "max_chars": 260,
        "include_hashtags": True,
        "quality_criteria": ENGLISH_COMMON_QUALITY_CRITERIA + [
            "Connect user research to messaging.",
            "Show how customer language improves launch copy.",
        ],
        "avoid": [
            "Generic launch advice.",
            "Treating interviews as only product research.",
            "More than 2 hashtags.",
        ],
        "reference_posts": [
            "User interview notes are not just for product decisions. They are launch copy material. The exact phrases customers use to describe pain often become stronger messaging than anything written in a brainstorm. #ProductMarketing",
            "Before writing launch content, read the interview notes again. Look for repeated frustrations, emotional words, and workarounds. That is usually where the strongest angle lives. #SaaS"
        ],
    },
    {
        "topic": "Why realtime AI demos fail when loading states are treated as an afterthought",
        "tone": "bold",
        "audience": "frontend engineers",
        "language": "English",
        "count": 1,
        "max_chars": 230,
        "include_hashtags": False,
        "quality_criteria": ENGLISH_COMMON_QUALITY_CRITERIA + [
            "Make the frontend UX lesson clear.",
            "Show why loading states are part of the product experience.",
        ],
        "avoid": [
            "Mocking developers.",
            "Only talking about visual polish.",
        ],
        "reference_posts": [
            "Realtime AI demos fail when the loading state is just an afterthought. Users do not only judge the final answer. They judge whether the system feels active, useful, and trustworthy while it works."
        ],
    },
    {
        "topic": "What makes onboarding copy feel helpful instead of robotic",
        "tone": "friendly",
        "audience": "product designers",
        "language": "English",
        "count": 1,
        "max_chars": 220,
        "include_hashtags": False,
        "quality_criteria": ENGLISH_COMMON_QUALITY_CRITERIA + [
            "Make the copy advice feel practical for product designers.",
            "Use simple UX language.",
        ],
        "avoid": [
            "Corporate UX jargon.",
            "Overly cute product copy.",
        ],
        "reference_posts": [
            "Helpful onboarding copy does not just tell users what a button does. It explains why the next step matters, what will happen after clicking, and how the user stays in control."
        ],
    },
    {
        "topic": "How agencies can turn client strategy calls into better social content ideas",
        "tone": "practical",
        "audience": "agency owners",
        "language": "English",
        "count": 2,
        "max_chars": 260,
        "include_hashtags": True,
        "quality_criteria": ENGLISH_COMMON_QUALITY_CRITERIA + [
            "Give a practical content repurposing angle.",
            "Make the agency workflow sound simple and repeatable.",
        ],
        "avoid": [
            "Vague advice like 'listen to your clients'.",
            "Too much agency jargon.",
            "More than 2 hashtags.",
        ],
        "reference_posts": [
            "Client strategy calls are full of content ideas. Do not only capture tasks. Capture objections, customer language, repeated questions, and strong opinions. Those become better posts than generic content prompts. #Agency",
            "A good agency content system starts inside the client call. Every decision, concern, and customer story can become an angle if the team knows what to listen for. #ContentMarketing"
        ],
    },
    {
        "topic": "Why content systems break when every post starts from a blank page",
        "tone": "analytical",
        "audience": "content leads",
        "language": "English",
        "count": 1,
        "max_chars": 230,
        "include_hashtags": False,
        "quality_criteria": ENGLISH_COMMON_QUALITY_CRITERIA + [
            "Explain the system problem behind inconsistent content.",
            "Make the point useful for content operations.",
        ],
        "avoid": [
            "Blaming writers.",
            "Generic productivity advice.",
        ],
        "reference_posts": [
            "Content systems break when every post starts from zero. Strong teams reuse inputs: customer questions, product decisions, sales calls, support tickets, and internal notes. The system feeds the ideas."
        ],
    },
    {
        "topic": "How to explain API latency issues to non-technical stakeholders without losing trust",
        "tone": "calm",
        "audience": "engineering managers",
        "language": "English",
        "count": 1,
        "max_chars": 260,
        "include_hashtags": False,
        "quality_criteria": ENGLISH_COMMON_QUALITY_CRITERIA + [
            "Make the explanation clear for non-technical stakeholders.",
            "Preserve trust by being transparent and specific.",
        ],
        "avoid": [
            "Overly technical explanations.",
            "Defensive engineering language.",
        ],
        "reference_posts": [
            "When explaining API latency, do not hide behind technical terms. Say what users feel, what is causing it, what the team is measuring, and what will change next. Clarity builds more trust than jargon."
        ],
    },
    {
        "topic": "Why AI-generated content still needs a human point of view",
        "tone": "thoughtful",
        "audience": "founder-led brands",
        "language": "English",
        "count": 1,
        "max_chars": 240,
        "include_hashtags": False,
        "quality_criteria": ENGLISH_COMMON_QUALITY_CRITERIA + [
            "Clarify the difference between drafting and thinking.",
            "Keep the post reflective but practical.",
        ],
        "avoid": [
            "Saying AI is useless.",
            "Overly philosophical writing.",
        ],
        "reference_posts": [
            "AI can generate a draft, but it cannot know what your company believes unless you make that clear. The human point of view is what turns acceptable content into memorable content."
        ],
    },
    {
        "topic": "How engineering teams can make internal updates easier to understand",
        "tone": "calm",
        "audience": "cross-functional teams",
        "language": "English",
        "count": 2,
        "max_chars": 240,
        "include_hashtags": False,
        "quality_criteria": ENGLISH_COMMON_QUALITY_CRITERIA + [
            "Translate technical updates into business/product impact.",
            "Make the advice useful for async communication.",
        ],
        "avoid": [
            "Too much engineering detail.",
            "Status updates with no context.",
        ],
        "reference_posts": [
            "A good engineering update answers three things: what changed, why it matters, and what is still uncertain. Non-technical teams do not need every detail. They need context they can act on.",
            "Internal updates get clearer when engineers separate facts from impact. “The endpoint is slower” is a fact. “Users may wait longer during export” is the impact."
        ],
    },
    {
        "topic": "Why polished product launches can still feel forgettable",
        "tone": "analytical",
        "audience": "product marketers",
        "language": "English",
        "count": 1,
        "max_chars": 230,
        "include_hashtags": False,
        "quality_criteria": ENGLISH_COMMON_QUALITY_CRITERIA + [
            "Explain why polish alone is not enough.",
            "Connect launch messaging to customer relevance.",
        ],
        "avoid": [
            "Generic launch criticism.",
            "Overly negative tone.",
        ],
        "reference_posts": [
            "A launch can look polished and still be forgettable if the message is only about features. Strong launches make the customer feel seen before they make the product look impressive."
        ],
    },
]


ENGLISH_VAL_EXAMPLES: list[dict[str, Any]] = [
    {
        "topic": "Why changelog posts rarely earn attention unless they explain the decision behind the feature",
        "tone": "analytical",
        "audience": "product marketers",
        "language": "English",
        "count": 1,
        "max_chars": 240,
        "include_hashtags": False,
        "quality_criteria": ENGLISH_COMMON_QUALITY_CRITERIA + [
            "Connect product updates to user relevance, not just shipping velocity.",
            "Make the messaging lesson specific for product communication.",
        ],
        "avoid": [
            "Just listing features.",
            "Internal-team celebration with no customer angle.",
        ],
        "reference_posts": [
            "Most changelog posts read like release notes pasted into a feed. People care more when you explain the decision behind the feature: what pain it removes, what trade-off it solves, or what changed for the user."
        ],
    },
    {
        "topic": "Why prompt quality matters more than model switching for many content workflows",
        "tone": "educational",
        "audience": "AI builders",
        "language": "English",
        "count": 1,
        "max_chars": 230,
        "include_hashtags": True,
        "quality_criteria": ENGLISH_COMMON_QUALITY_CRITERIA + [
            "Explain the value of prompt structure clearly.",
            "Avoid making the claim too absolute.",
        ],
        "avoid": [
            "Model wars.",
            "Overly technical prompt engineering language.",
            "More than 2 hashtags.",
        ],
        "reference_posts": [
            "Many content workflows do not fail because the model is weak. They fail because the prompt gives no audience, angle, examples, constraints, or quality bar. Better inputs often beat model switching. #AI #Prompting"
        ],
    },
    {
        "topic": "How founders can reuse webinar transcripts without sounding repetitive",
        "tone": "practical",
        "audience": "creator founders",
        "language": "English",
        "count": 2,
        "max_chars": 250,
        "include_hashtags": False,
        "quality_criteria": ENGLISH_COMMON_QUALITY_CRITERIA + [
            "Give a practical repurposing workflow.",
            "Avoid making the content feel copied from a transcript.",
        ],
        "avoid": [
            "Copy-paste advice.",
            "Generic repurposing tips.",
        ],
        "reference_posts": [
            "A webinar transcript should not become 20 identical posts. Pull out different assets: one strong quote, one mistake, one framework, one customer question, and one opinion. Same source, different angles.",
            "To reuse a webinar well, do not summarize the whole thing. Pick one moment that would make someone stop scrolling, then rewrite it for the feed instead of the stage."
        ],
    },
    {
        "topic": "How product teams should talk about failed experiments without sounding defensive",
        "tone": "reflective",
        "audience": "product leaders",
        "language": "English",
        "count": 2,
        "max_chars": 250,
        "include_hashtags": False,
        "quality_criteria": ENGLISH_COMMON_QUALITY_CRITERIA + [
            "Frame failure as learning without sounding weak or self-congratulatory.",
            "Make the writing useful for teams communicating product decisions publicly.",
        ],
        "avoid": [
            "Excuse-making.",
            "Vague lessons with no concrete takeaway.",
        ],
        "reference_posts": [
            "A failed experiment is still valuable if the team can explain what they believed, what they tested, what they learned, and what changed next. The goal is not to defend the miss. The goal is to show the quality of thinking.",
            "Teams sound defensive when they talk around the result. They sound credible when they name the assumption, the evidence, and the next decision clearly."
        ],
    },
    {
        "topic": "Why user-facing AI features need better empty states",
        "tone": "insightful",
        "audience": "product designers",
        "language": "English",
        "count": 1,
        "max_chars": 230,
        "include_hashtags": False,
        "quality_criteria": ENGLISH_COMMON_QUALITY_CRITERIA + [
            "Explain why empty states matter in AI UX.",
            "Make it useful for product designers.",
        ],
        "avoid": [
            "Only talking about visual design.",
            "Vague UX advice.",
        ],
        "reference_posts": [
            "AI empty states matter because users often do not know what to ask first. A good empty state teaches the shape of a useful prompt, shows examples, and lowers the fear of starting wrong."
        ],
    },
]

ENGLISH_TRAIN_EXAMPLES = normalize_examples(ENGLISH_TRAIN_EXAMPLES)
ENGLISH_VAL_EXAMPLES = normalize_examples(ENGLISH_VAL_EXAMPLES)


def build_english_gepa_trainset() -> list[dict[str, Any]]:
    """
    Training examples for GEPA optimization.

    The extra fields can be used by your evaluator/metric:
    - quality_criteria: what a strong answer should satisfy
    - avoid: what the model should not do
    - reference_posts: example outputs that represent the desired quality
    - bad_examples: examples of weak outputs to avoid resembling
    - desired_structure / hook_style / must_include / content_goal: clearer generation goals
    - scoring_rubric: explicit evaluation hints
    """
    return ENGLISH_TRAIN_EXAMPLES


def build_english_gepa_valset() -> list[dict[str, Any]]:
    """
    Validation examples for checking generalization.

    Keep these related to the same product/content domain,
    but not too close to the training topics.
    """
    return ENGLISH_VAL_EXAMPLES
