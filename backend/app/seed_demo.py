from __future__ import annotations

from datetime import datetime

from sqlalchemy import or_

from app.auth import hash_password
from app.database import SessionLocal
from app.enum import (
    CourseVersionStatus,
    MembershipStatus,
    OrganizationRole,
    OrganizationType,
    SectionMode,
)
from app.models import (
    Activity,
    Assessment,
    AssessmentCompetencyAlignment,
    Course,
    CourseVersion,
    Enrollment,
    Lesson,
    Organization,
    OrganizationMembership,
    Question,
    Section,
    Source,
    Unit,
    User,
)

DEMO_PASSWORD = "password"
DEMO_ORG_NAME = "EchoEd Demo School"
DEMO_COURSE_TITLE = "Introduction to Africa"
LEGACY_DEMO_COURSE_TITLES = {
    DEMO_COURSE_TITLE,
    "K-5 Introduction to Africa",
}
DEMO_SECTION_NAME = "Grade 3 - Cohort A"
DEMO_UNITS = [
    {
        "title": "Origins and Geography",
        "order": 1,
        "content": "Learners build foundational geographic understanding of Africa through maps, regional stories, and place-based observation.",
        "lessons": [
            {
                "title": "Introduction to Africa",
                "order": 1,
                "duration_minutes": 20,
                "objective": "Identify Africa as a diverse continent with many regions, peoples, and environments.",
                "learning_objectives": "Students will describe Africa's size, identify major regions, and explain why Africa cannot be treated as one single place or culture.",
                "key_concepts": ["continent", "regions", "diversity", "place"],
                "hook": "Begin with a world map comparison that invites learners to notice Africa's size and ask what they already know.",
                "content": "Africa is a vast continent made up of many regions, countries, languages, histories, and environments. The lesson introduces Africa through maps, child-friendly visuals, and affirming language that emphasizes diversity and shared humanity.",
                "guided_practice": "As a class, locate North, West, East, Central, and Southern Africa on a guided map while naming one image or idea connected to each region.",
                "independent_practice": "Learners draw or label one classroom map detail and write two observations about Africa's diversity and scale.",
                "assessment": "Short written or spoken response naming one region and one accurate fact about Africa's diversity.",
                "discussion_questions": [
                    "Why is it important to remember that Africa is a continent and not a single country?",
                    "What can maps help us understand about people and place?",
                ],
                "teacher_notes": "Pacing: use this lesson as an entry point for the whole pathway. Remediation: revisit map vocabulary with visuals and partner talk. Enrichment: invite learners to compare Africa's size with another continent.",
                "skill_tags": ["geography", "map-reading", "literacy"],
                "standards_metadata": {
                    "pathway_key": "introduction-to-africa",
                    "unit_theme": "origins-and-geography",
                    "interdisciplinary_domains": ["geography", "literacy", "civic-understanding"],
                    "pacing_band": "core",
                },
                "sources": [
                    {
                        "citation": "National Geographic Kids: Africa overview",
                        "url": "https://kids.nationalgeographic.com/geography/continents/article/africa",
                    }
                ],
                "activities": [
                    {
                        "type": "story",
                        "title": "Map Window",
                        "order": 1,
                        "content": "Imagine opening a giant classroom map and noticing that Africa stretches across many regions, climates, and communities. As you read, look for clues that show Africa is a continent full of many stories rather than a single place.",
                    },
                    {
                        "type": "quiz",
                        "title": "Key Concept Check",
                        "order": 2,
                        "content": "{\"question\":\"Which word best describes Africa?\",\"options\":[\"A single country\",\"A diverse continent\",\"Only a desert\"]}",
                    },
                    {
                        "type": "reflection",
                        "title": "Place and Perspective Reflection",
                        "order": 3,
                        "content": "Write or say one new idea you learned about Africa and one reason it matters to learn about places with care and accuracy.",
                    },
                ],
            },
            {
                "title": "Regions, Rivers, and Routes",
                "order": 2,
                "duration_minutes": 20,
                "objective": "Describe how regions, rivers, and travel routes help people understand Africa's geography.",
                "learning_objectives": "Students will identify one major river, explain why rivers matter to communities, and connect travel routes to movement and trade.",
                "key_concepts": ["river", "route", "community", "movement"],
                "hook": "Show a river image and ask how water shapes where people live, travel, and gather.",
                "content": "Rivers and travel routes connect people, ideas, and goods. The Nile and other waterways help communities farm, trade, and travel, while routes across land and water link regions in meaningful ways.",
                "guided_practice": "Use a simple map to trace one river and one route while discussing how people might use them for travel, food, or community life.",
                "independent_practice": "Learners complete a short matching or drawing task that connects a river or route to one way it supports people.",
                "assessment": "Exit response explaining one reason rivers or routes matter to communities.",
                "discussion_questions": [
                    "How might a river help a family or community?",
                    "Why do routes matter when people share goods, stories, or ideas?",
                ],
                "teacher_notes": "Pacing: pause for vocabulary checks on river, route, and community. Remediation: use picture cards and sentence stems. Enrichment: compare two routes or ask learners to imagine a journey.",
                "skill_tags": ["geography", "vocabulary", "social-studies"],
                "standards_metadata": {
                    "pathway_key": "introduction-to-africa",
                    "unit_theme": "origins-and-geography",
                    "interdisciplinary_domains": ["geography", "history", "literacy"],
                    "pacing_band": "core",
                },
                "sources": [
                    {
                        "citation": "Britannica Kids: Nile River facts",
                        "url": "https://kids.britannica.com/kids/article/Nile-River/353619",
                    }
                ],
                "activities": [
                    {
                        "type": "story",
                        "title": "River Journey Prompt",
                        "order": 1,
                        "content": "Picture a family traveling beside a great river. What might they see, grow, carry, or trade along the way? Use the lesson clues to imagine the journey.",
                    },
                    {
                        "type": "checkpoint",
                        "title": "Geography Exploration Prompt",
                        "order": 2,
                        "content": "Point to one river or route on your class map and explain how it could help people move, gather food, or share ideas.",
                    },
                    {
                        "type": "reflection",
                        "title": "Community Connection",
                        "order": 3,
                        "content": "How do rivers, roads, or paths help communities in your world stay connected? Share one comparison with the lesson.",
                    },
                ],
            },
            {
                "title": "Map Stories of Home and Place",
                "order": 3,
                "duration_minutes": 20,
                "objective": "Connect map-reading to personal stories of home, place, and belonging.",
                "learning_objectives": "Students will use geographic language to describe place and connect a map-based observation to a story about home or belonging.",
                "key_concepts": ["home", "belonging", "location", "story"],
                "hook": "Invite learners to think about what helps a place feel like home and how a map tells only part of that story.",
                "content": "Maps show location, but people give places meaning through stories, relationships, and belonging. Learners explore how maps and stories work together to help us understand communities.",
                "guided_practice": "Model a short place-based story using a map and a sentence frame that links location to memory or community.",
                "independent_practice": "Learners create a short spoken, drawn, or written map story about a place that matters to them.",
                "assessment": "Share one map-based observation and one sentence about why a place matters.",
                "discussion_questions": [
                    "What can a story teach us that a map alone cannot?",
                    "How do people help make a place meaningful?",
                ],
                "teacher_notes": "Pacing: allow multiple ways to respond. Remediation: offer sentence stems and drawing supports. Enrichment: invite learners to compare a personal place story with a place from the lesson.",
                "skill_tags": ["literacy", "geography", "reflection"],
                "standards_metadata": {
                    "pathway_key": "introduction-to-africa",
                    "unit_theme": "origins-and-geography",
                    "interdisciplinary_domains": ["literacy", "geography", "social-emotional-learning"],
                    "pacing_band": "core",
                },
                "sources": [
                    {
                        "citation": "UNICEF Learning Passport: Place-based learning overview",
                        "url": "https://learningpassport.unicef.org/",
                    }
                ],
                "activities": [
                    {
                        "type": "story",
                        "title": "Storytelling Starter",
                        "order": 1,
                        "content": "A map can show where someone lives, but a story can show why that place matters. Listen for details that make a place feel special, safe, joyful, or meaningful.",
                    },
                    {
                        "type": "reflection",
                        "title": "My Place Story",
                        "order": 2,
                        "content": "Describe a place that matters to you. What do people do there, and how does that place help you feel connected or at home?",
                    },
                    {
                        "type": "checkpoint",
                        "title": "Discussion Bridge",
                        "order": 3,
                        "content": "Share one idea: what can a story teach us about a place that a map cannot show on its own?",
                    },
                ],
            },
        ],
    },
    {
        "title": "Kingdoms and Knowledge",
        "order": 2,
        "content": "Learners study African kingdoms, scholarship, trade, and community life through stories, evidence, and culturally grounded inquiry.",
        "lessons": [
            {
                "title": "Learning from Great African Kingdoms",
                "order": 1,
                "duration_minutes": 20,
                "objective": "Describe how African kingdoms contributed to learning, trade, and leadership.",
                "learning_objectives": "Students will explain one contribution from a major African kingdom and connect it to community strength or learning.",
                "key_concepts": ["kingdoms", "trade", "scholarship", "leadership"],
                "hook": "Show an image of Timbuktu and ask what people might learn or share in a place like this.",
                "content": "Kingdoms such as Mali and Songhai were centers of trade, learning, leadership, and cultural exchange. Their histories help learners see Africa as a source of knowledge and innovation.",
                "guided_practice": "Compare two contributions from different kingdoms using a simple class chart with evidence from the lesson.",
                "independent_practice": "Learners create one evidence-backed fact card about a kingdom, scholar, or trade center.",
                "assessment": "Exit ticket naming one kingdom and one contribution to learning, trade, or leadership.",
                "discussion_questions": [
                    "Why do centers of learning matter to a society?",
                    "How can leadership shape a community's future?",
                ],
                "teacher_notes": "Pacing: slow down for kingdom vocabulary and timeline context. Remediation: use picture supports and one-idea summaries. Enrichment: connect a kingdom's contribution to a present-day school or community institution.",
                "skill_tags": ["history", "literacy", "civic-understanding"],
                "standards_metadata": {
                    "pathway_key": "introduction-to-africa",
                    "unit_theme": "kingdoms-and-knowledge",
                    "interdisciplinary_domains": ["history", "literacy", "civic-understanding"],
                    "pacing_band": "core",
                },
                "sources": [
                    {
                        "citation": "Encyclopaedia Britannica: Mali Empire",
                        "url": "https://www.britannica.com/place/Mali-historical-empire-Africa",
                    }
                ],
                "activities": [
                    {
                        "type": "story",
                        "title": "Scholarship Spotlight",
                        "order": 1,
                        "content": "Imagine visiting a place where people gather to read, learn, trade, and share ideas. Notice how the lesson connects learning to leadership and community strength.",
                    },
                    {
                        "type": "checkpoint",
                        "title": "Kingdom Contribution Prompt",
                        "order": 2,
                        "content": "Name one kingdom, scholar, or trade center from the lesson and explain what it contributed to the wider community.",
                    },
                    {
                        "type": "reflection",
                        "title": "Learning Community Reflection",
                        "order": 3,
                        "content": "Why do you think communities become stronger when they value knowledge, teaching, and learning?",
                    },
                ],
            },
            {
                "title": "Markets, Stories, and Community Life",
                "order": 2,
                "duration_minutes": 20,
                "objective": "Explain how markets and stories help communities share resources, knowledge, and culture.",
                "learning_objectives": "Students will describe one way markets support community life and one way stories carry knowledge across generations.",
                "key_concepts": ["market", "storytelling", "exchange", "community"],
                "hook": "Ask learners what people share in a market besides objects and invite them to think about stories, news, and ideas.",
                "content": "Markets are community spaces where people exchange goods, stories, and news. Storytelling helps communities remember values, history, and identity across generations.",
                "guided_practice": "Create a class chart that sorts examples of things people can exchange in a market or community gathering.",
                "independent_practice": "Learners complete a short response or drawing showing something a community can share through stories or exchange.",
                "assessment": "Written or spoken explanation of how one market or story practice supports community life.",
                "discussion_questions": [
                    "What kinds of knowledge can people share in community spaces?",
                    "Why might stories matter as much as goods?",
                ],
                "teacher_notes": "Pacing: give learners time to connect ideas to familiar community spaces. Remediation: use oral rehearsal before writing. Enrichment: compare a local community space with one from the lesson.",
                "skill_tags": ["storytelling", "economics", "community"],
                "standards_metadata": {
                    "pathway_key": "introduction-to-africa",
                    "unit_theme": "kingdoms-and-knowledge",
                    "interdisciplinary_domains": ["economics", "literacy", "history"],
                    "pacing_band": "core",
                },
                "sources": [
                    {
                        "citation": "Smithsonian Center for Folklife and Cultural Heritage: Storytelling and community",
                        "url": "https://folklife.si.edu/",
                    }
                ],
                "activities": [
                    {
                        "type": "story",
                        "title": "Market Walk",
                        "order": 1,
                        "content": "Imagine walking through a busy market where people exchange food, cloth, stories, songs, and news. Think about how a market can teach as well as provide.",
                    },
                    {
                        "type": "quiz",
                        "title": "Vocabulary Reinforcement",
                        "order": 2,
                        "content": "{\"question\":\"What is one thing people can exchange in a market?\",\"options\":[\"Only objects\",\"Ideas and stories\",\"Nothing important\"]}",
                    },
                    {
                        "type": "reflection",
                        "title": "Community Sharing Prompt",
                        "order": 3,
                        "content": "What kinds of knowledge or traditions do people share in your community, and why are those exchanges important?",
                    },
                ],
            },
            {
                "title": "Wisdom Keepers and Libraries",
                "order": 3,
                "duration_minutes": 20,
                "objective": "Recognize libraries, scholars, and wisdom keepers as part of African intellectual history.",
                "learning_objectives": "Students will identify one example of African scholarship and explain why preserving knowledge matters.",
                "key_concepts": ["scholar", "library", "knowledge", "preservation"],
                "hook": "Show a stack of books or manuscripts and ask how communities protect important ideas over time.",
                "content": "Libraries, manuscripts, teachers, and scholars help communities preserve knowledge. African intellectual traditions include oral and written ways of protecting and sharing wisdom.",
                "guided_practice": "Read and discuss a short excerpt or image about libraries or scholars, naming what kinds of knowledge are being preserved.",
                "independent_practice": "Learners create a 'wisdom keeper' card that names a person, place, or object that helps protect learning.",
                "assessment": "Short response explaining why preserving knowledge matters for a community.",
                "discussion_questions": [
                    "Who helps keep knowledge safe in a community?",
                    "How can schools, libraries, and elders all teach us?",
                ],
                "teacher_notes": "Pacing: support the oral-to-written connection explicitly. Remediation: use visuals and sentence frames. Enrichment: compare two ways knowledge can be preserved.",
                "skill_tags": ["history", "research", "literacy"],
                "standards_metadata": {
                    "pathway_key": "introduction-to-africa",
                    "unit_theme": "kingdoms-and-knowledge",
                    "interdisciplinary_domains": ["history", "literacy", "research"],
                    "pacing_band": "core",
                },
                "sources": [
                    {
                        "citation": "UNESCO: Timbuktu manuscripts and African scholarship",
                        "url": "https://www.unesco.org/",
                    }
                ],
                "activities": [
                    {
                        "type": "story",
                        "title": "Library and Legacy Prompt",
                        "order": 1,
                        "content": "Picture a room full of books, manuscripts, or spoken stories that help a community remember important ideas. Think about the people who protect that knowledge.",
                    },
                    {
                        "type": "checkpoint",
                        "title": "Knowledge Keeper Prompt",
                        "order": 2,
                        "content": "Name one wisdom keeper from the lesson or your own life and explain how they help knowledge stay alive.",
                    },
                    {
                        "type": "reflection",
                        "title": "Preserving Knowledge Reflection",
                        "order": 3,
                        "content": "Why is it important for communities to save stories, books, teachings, and memories for future generations?",
                    },
                ],
            },
        ],
    },
    {
        "title": "Living Lands and Shared Futures",
        "order": 3,
        "content": "Learners connect ecosystems, arts, celebration, and civic care through culturally grounded inquiry into land, life, and community futures.",
        "lessons": [
            {
                "title": "Ecosystems Across Africa",
                "order": 1,
                "duration_minutes": 20,
                "objective": "Describe how different African ecosystems support living things and shape daily life.",
                "learning_objectives": "Students will identify at least two ecosystems and explain one way environment can influence how people and animals live.",
                "key_concepts": ["ecosystem", "environment", "adaptation", "habitat"],
                "hook": "Show contrasting images of a savanna and rainforest and ask what living things might need in each place.",
                "content": "Africa includes many ecosystems, from deserts and savannas to forests and coastlines. Plants, animals, and people respond to these environments in different ways.",
                "guided_practice": "Compare two ecosystems using a simple class chart that names climate, living things, and human/community connections.",
                "independent_practice": "Learners draw or write one detail about how an ecosystem supports life.",
                "assessment": "Short response naming an ecosystem and one way it shapes life there.",
                "discussion_questions": [
                    "How do environments shape what living things need?",
                    "Why is it important to care for different ecosystems?",
                ],
                "teacher_notes": "Pacing: use clear visuals and repetition for ecosystem vocabulary. Remediation: scaffold with picture sorts. Enrichment: invite learners to compare ecosystems across continents.",
                "skill_tags": ["science", "geography", "observation"],
                "standards_metadata": {
                    "pathway_key": "introduction-to-africa",
                    "unit_theme": "living-lands-and-shared-futures",
                    "interdisciplinary_domains": ["science", "geography", "civic-understanding"],
                    "pacing_band": "core",
                },
                "sources": [
                    {
                        "citation": "World Wildlife Fund: African ecosystems overview",
                        "url": "https://www.worldwildlife.org/",
                    }
                ],
                "activities": [
                    {
                        "type": "story",
                        "title": "Ecosystem Observation Prompt",
                        "order": 1,
                        "content": "Look closely at the idea of a savanna, forest, desert, or coast. What plants, animals, weather, and people might belong there, and what clues help you infer that?",
                    },
                    {
                        "type": "checkpoint",
                        "title": "Habitat Talk",
                        "order": 2,
                        "content": "Choose one ecosystem and explain how it supports both living things and human community life.",
                    },
                    {
                        "type": "reflection",
                        "title": "Care for Living Lands",
                        "order": 3,
                        "content": "What is one action people can take to help protect an ecosystem and the life it holds?",
                    },
                ],
            },
            {
                "title": "Music, Art, and Celebration",
                "order": 2,
                "duration_minutes": 20,
                "objective": "Explore how music, art, and celebration express identity, history, and joy.",
                "learning_objectives": "Students will describe one way music or art can communicate culture, identity, or celebration.",
                "key_concepts": ["music", "art", "celebration", "expression"],
                "hook": "Play or describe a short rhythmic pattern and ask learners how sound and movement can help people celebrate together.",
                "content": "Music, dance, art, and celebration are powerful ways communities express identity, memory, and joy. Learners explore these forms as living expressions of culture rather than decoration.",
                "guided_practice": "Discuss one example of artistic expression and identify the feeling, message, or community value it may carry.",
                "independent_practice": "Learners create a short response, sketch, or movement idea that reflects a message of celebration, belonging, or gratitude.",
                "assessment": "Share one sentence about what a piece of music or art can communicate to a community.",
                "discussion_questions": [
                    "How can music or art help people feel connected?",
                    "Why do celebrations matter in communities?",
                ],
                "teacher_notes": "Pacing: keep responses multimodal. Remediation: offer drawing and speaking choices. Enrichment: connect an artistic form from the lesson to learners' own communities.",
                "skill_tags": ["arts", "music", "community"],
                "standards_metadata": {
                    "pathway_key": "introduction-to-africa",
                    "unit_theme": "living-lands-and-shared-futures",
                    "interdisciplinary_domains": ["arts", "music", "social-emotional-learning"],
                    "pacing_band": "core",
                },
                "sources": [
                    {
                        "citation": "Smithsonian National Museum of African Art: Learning resources",
                        "url": "https://africa.si.edu/education/",
                    }
                ],
                "activities": [
                    {
                        "type": "story",
                        "title": "Celebration and Expression Prompt",
                        "order": 1,
                        "content": "Think about a song, rhythm, image, or celebration that helps people remember joy, belonging, or gratitude. Notice how art can carry a message as well as a feeling.",
                    },
                    {
                        "type": "reflection",
                        "title": "Art and Identity Reflection",
                        "order": 2,
                        "content": "How can music or art help people feel proud of who they are and connected to others?",
                    },
                    {
                        "type": "checkpoint",
                        "title": "Creative Response Prompt",
                        "order": 3,
                        "content": "Sketch, describe, or act out one idea for a celebration that shows community, gratitude, or joy.",
                    },
                ],
            },
            {
                "title": "Caring for Land and Community",
                "order": 3,
                "duration_minutes": 20,
                "objective": "Connect environmental care and community care to shared futures.",
                "learning_objectives": "Students will explain one action that supports land, people, or community wellbeing and connect that action to shared responsibility.",
                "key_concepts": ["care", "responsibility", "community", "future"],
                "hook": "Ask learners what caring for a place looks like and how caring for land can also mean caring for people.",
                "content": "Communities care for land, water, one another, and future generations in many ways. The lesson invites learners to think about stewardship, responsibility, and collective wellbeing.",
                "guided_practice": "Build a class list of actions that help protect places, ecosystems, or community relationships.",
                "independent_practice": "Learners choose one action and explain how it helps a place or community thrive.",
                "assessment": "Closure response naming one caring action and why it matters.",
                "discussion_questions": [
                    "What does it mean to care for a place and the people in it?",
                    "How can small actions support a shared future?",
                ],
                "teacher_notes": "Pacing: use the final lesson as pathway closure and synthesis. Remediation: revisit the unit's big ideas with visual prompts. Enrichment: invite learners to propose a simple community care project idea.",
                "skill_tags": ["civic-understanding", "science", "reflection"],
                "standards_metadata": {
                    "pathway_key": "introduction-to-africa",
                    "unit_theme": "living-lands-and-shared-futures",
                    "interdisciplinary_domains": ["civic-understanding", "science", "reflection"],
                    "pacing_band": "closure",
                },
                "sources": [
                    {
                        "citation": "United Nations Environment Programme: Children and environmental stewardship",
                        "url": "https://www.unep.org/",
                    }
                ],
                "activities": [
                    {
                        "type": "story",
                        "title": "Shared Future Prompt",
                        "order": 1,
                        "content": "Imagine a neighborhood, village, or town where people work together to care for water, land, animals, and one another. What actions help that community stay strong?",
                    },
                    {
                        "type": "reflection",
                        "title": "Community Care Reflection",
                        "order": 2,
                        "content": "Describe one way you can care for a place, a person, or your shared environment this week.",
                    },
                    {
                        "type": "checkpoint",
                        "title": "Lightweight Project Prompt",
                        "order": 3,
                        "content": "Plan a simple class, home, or community care action. What would you do, who would it help, and why would it matter?",
                    },
                ],
            },
        ],
    },
]

DEMO_FLAGSHIP_ASSESSMENTS = [
    {
        "title": "Introduction to Africa Lesson Check",
        "description": "A gentle check for understanding that helps learners name Africa as a diverse continent.",
        "scope": "lesson",
        "unit_title": "Origins and Geography",
        "lesson_title": "Introduction to Africa",
        "assessment_state": "published",
        "availability_state": "available",
        "passing_score": 70.0,
        "max_attempts": 2,
        "policy_metadata": {"assessment_kind": "formative", "supportive_tone": True},
        "lifecycle_metadata": {"flagship_pathway": True, "seed_key": "intro-africa-lesson-check"},
        "questions": [
            {
                "prompt": "Which sentence best describes Africa?",
                "choices": ["Africa is one country.", "Africa is a diverse continent.", "Africa is only desert."],
                "correct_answer": "Africa is a diverse continent.",
                "points": 1,
                "order": 1,
                "explanation": "Africa is a continent made up of many countries, regions, peoples, and environments.",
            },
            {
                "prompt": "Why is it important to learn about Africa with care and accuracy?",
                "choices": [
                    "Because places and people deserve respect.",
                    "Because only maps matter.",
                    "Because one story explains everything.",
                ],
                "correct_answer": "Because places and people deserve respect.",
                "points": 1,
                "order": 2,
                "explanation": "Accurate learning helps us honor people, stories, and places with respect.",
            },
        ],
        "competency_alignments": [
            {
                "objective_key": "africa-diversity-and-respect",
                "objective_title": "Africa Diversity and Respect",
                "objective_type": "objective",
                "weight": 1.0,
                "mastery_threshold": 70.0,
                "question_order": 1,
                "metadata": {"evidence_kind": "formative-check"},
            },
            {
                "objective_key": "careful-place-learning",
                "objective_title": "Careful Place Learning",
                "objective_type": "competency",
                "weight": 1.0,
                "mastery_threshold": 70.0,
                "question_order": 2,
                "metadata": {"evidence_kind": "reflection-support"},
            },
        ],
    },
    {
        "title": "Origins and Geography Unit Check",
        "description": "A supportive unit check on regions, routes, and place-based stories.",
        "scope": "unit",
        "unit_title": "Origins and Geography",
        "assessment_state": "published",
        "availability_state": "available",
        "passing_score": 70.0,
        "max_attempts": 2,
        "policy_metadata": {"assessment_kind": "unit-check", "supportive_tone": True},
        "lifecycle_metadata": {"flagship_pathway": True, "seed_key": "origins-geography-unit-check"},
        "questions": [
            {
                "prompt": "What can maps help us understand?",
                "choices": ["Only one story", "Regions and place", "Nothing about community"],
                "correct_answer": "Regions and place",
                "points": 1,
                "order": 1,
                "explanation": "Maps help us understand location, regions, and relationships between places.",
            },
            {
                "prompt": "Why do rivers and routes matter to communities?",
                "choices": ["They support movement and connection.", "They erase differences.", "They are only decorations."],
                "correct_answer": "They support movement and connection.",
                "points": 1,
                "order": 2,
                "explanation": "Rivers and routes connect people, goods, and ideas.",
            },
        ],
        "competency_alignments": [
            {
                "objective_key": "africa-geography-foundations",
                "objective_title": "Africa Geography Foundations",
                "objective_type": "objective",
                "weight": 1.0,
                "mastery_threshold": 70.0,
                "question_order": 1,
                "metadata": {"evidence_kind": "unit-check"},
            },
            {
                "objective_key": "routes-rivers-and-community",
                "objective_title": "Routes, Rivers, and Community",
                "objective_type": "competency",
                "weight": 1.0,
                "mastery_threshold": 70.0,
                "question_order": 2,
                "metadata": {"evidence_kind": "unit-check"},
            },
        ],
    },
    {
        "title": "Kingdoms and Knowledge Unit Check",
        "description": "A reflective check on scholarship, exchange, and community knowledge.",
        "scope": "unit",
        "unit_title": "Kingdoms and Knowledge",
        "assessment_state": "published",
        "availability_state": "available",
        "passing_score": 70.0,
        "max_attempts": 2,
        "policy_metadata": {"assessment_kind": "unit-check", "supportive_tone": True},
        "lifecycle_metadata": {"flagship_pathway": True, "seed_key": "kingdoms-knowledge-unit-check"},
        "questions": [
            {
                "prompt": "Which place in the lesson was known for learning and scholarship?",
                "choices": ["Timbuktu", "A random factory", "Only a market stall"],
                "correct_answer": "Timbuktu",
                "points": 1,
                "order": 1,
                "explanation": "Timbuktu is one example learners encounter as a center of study and knowledge.",
            },
            {
                "prompt": "What can communities exchange besides objects?",
                "choices": ["Stories and ideas", "Nothing meaningful", "Only silence"],
                "correct_answer": "Stories and ideas",
                "points": 1,
                "order": 2,
                "explanation": "Communities exchange knowledge, traditions, and stories as well as goods.",
            },
        ],
        "competency_alignments": [
            {
                "objective_key": "african-knowledge-centers",
                "objective_title": "African Knowledge Centers",
                "objective_type": "objective",
                "weight": 1.0,
                "mastery_threshold": 70.0,
                "question_order": 1,
                "metadata": {"evidence_kind": "unit-check"},
            },
            {
                "objective_key": "community-exchange-and-story",
                "objective_title": "Community Exchange and Story",
                "objective_type": "competency",
                "weight": 1.0,
                "mastery_threshold": 70.0,
                "question_order": 2,
                "metadata": {"evidence_kind": "discussion-aligned"},
            },
        ],
    },
    {
        "title": "Living Lands and Shared Futures Unit Check",
        "description": "A caring synthesis check on ecosystems, art, and community responsibility.",
        "scope": "unit",
        "unit_title": "Living Lands and Shared Futures",
        "assessment_state": "published",
        "availability_state": "available",
        "passing_score": 70.0,
        "max_attempts": 2,
        "policy_metadata": {"assessment_kind": "unit-check", "supportive_tone": True},
        "lifecycle_metadata": {"flagship_pathway": True, "seed_key": "living-lands-unit-check"},
        "questions": [
            {
                "prompt": "Why do ecosystems matter?",
                "choices": ["They support life and relationships.", "They are only for pictures.", "They never change."],
                "correct_answer": "They support life and relationships.",
                "points": 1,
                "order": 1,
                "explanation": "Ecosystems connect living things, places, and community wellbeing.",
            },
            {
                "prompt": "What is one way people can care for land and community?",
                "choices": ["Work together responsibly", "Ignore shared spaces", "Never help others"],
                "correct_answer": "Work together responsibly",
                "points": 1,
                "order": 2,
                "explanation": "Shared responsibility helps people care for land, water, and one another.",
            },
        ],
        "competency_alignments": [
            {
                "objective_key": "ecosystem-observation-and-care",
                "objective_title": "Ecosystem Observation and Care",
                "objective_type": "objective",
                "weight": 1.0,
                "mastery_threshold": 70.0,
                "question_order": 1,
                "metadata": {"evidence_kind": "unit-check"},
            },
            {
                "objective_key": "shared-future-responsibility",
                "objective_title": "Shared Future Responsibility",
                "objective_type": "competency",
                "weight": 1.0,
                "mastery_threshold": 70.0,
                "question_order": 2,
                "metadata": {"evidence_kind": "project-aligned"},
            },
        ],
    },
    {
        "title": "Introduction to Africa Pathway Celebration Check",
        "description": "A warm end-of-pathway check that celebrates understanding, care, and connection.",
        "scope": "course",
        "assessment_state": "published",
        "availability_state": "available",
        "passing_score": 75.0,
        "max_attempts": 2,
        "policy_metadata": {"assessment_kind": "course-check", "supportive_tone": True},
        "lifecycle_metadata": {"flagship_pathway": True, "seed_key": "intro-africa-pathway-check"},
        "questions": [
            {
                "prompt": "Which statement best shows what learners should remember about Africa?",
                "choices": [
                    "Africa holds many regions, histories, and communities.",
                    "Africa is one single story.",
                    "Africa has no connection to learning and culture.",
                ],
                "correct_answer": "Africa holds many regions, histories, and communities.",
                "points": 1,
                "order": 1,
                "explanation": "The pathway emphasizes diversity, knowledge, culture, and community.",
            },
            {
                "prompt": "How can learners show care after this pathway?",
                "choices": [
                    "By learning with respect and curiosity",
                    "By repeating stereotypes",
                    "By ignoring community knowledge",
                ],
                "correct_answer": "By learning with respect and curiosity",
                "points": 1,
                "order": 2,
                "explanation": "Curiosity, care, and respect are part of the pathway's learning stance.",
            },
        ],
        "competency_alignments": [
            {
                "objective_key": "flagship-pathway-synthesis",
                "objective_title": "Flagship Pathway Synthesis",
                "objective_type": "objective",
                "weight": 1.0,
                "mastery_threshold": 75.0,
                "question_order": 1,
                "metadata": {"evidence_kind": "course-check"},
            },
            {
                "objective_key": "culturally-grounded-curiosity",
                "objective_title": "Culturally Grounded Curiosity",
                "objective_type": "competency",
                "weight": 1.0,
                "mastery_threshold": 75.0,
                "question_order": 2,
                "metadata": {"evidence_kind": "course-check"},
            },
        ],
    },
    {
        "title": "Teacher Preview: Geography Extension Check",
        "description": "A preview-only assessment kept unavailable to learners until later phases.",
        "scope": "lesson",
        "unit_title": "Origins and Geography",
        "lesson_title": "Regions, Rivers, and Routes",
        "assessment_state": "draft",
        "availability_state": "pending_review",
        "passing_score": 70.0,
        "max_attempts": 1,
        "policy_metadata": {"assessment_kind": "preview", "supportive_tone": True},
        "lifecycle_metadata": {"flagship_pathway": True, "seed_key": "teacher-preview-geography-extension"},
        "questions": [
            {
                "prompt": "Which idea best fits this preview check?",
                "choices": ["Routes connect people", "Maps erase stories", "Rivers do not matter"],
                "correct_answer": "Routes connect people",
                "points": 1,
                "order": 1,
                "explanation": "The preview still reinforces route and community understanding.",
            }
        ],
        "competency_alignments": [
            {
                "objective_key": "preview-geography-extension",
                "objective_title": "Preview Geography Extension",
                "objective_type": "objective",
                "weight": 1.0,
                "mastery_threshold": 70.0,
                "question_order": 1,
                "metadata": {"evidence_kind": "preview"},
            }
        ],
    },
]

DEMO_FLAGSHIP_SUPPORT_PROFILES = {
    "Introduction to Africa": {
        "teacher_addendum": (
            " Facilitation: open with affirming prior-knowledge talk, then guide learners to compare what they thought "
            "with what the map actually shows. Family/community extension: invite learners to ask someone at home what "
            "helps them learn about places respectfully."
        ),
        "discussion_extensions": [
            "What is one respectful way to talk about a place that is new to you?",
        ],
        "family_extensions": [
            "At home, ask a family member what helps them learn about another place with care and respect.",
        ],
        "homeschool_adaptations": [
            "Use a globe, atlas, or printed map and pause after each region to let the learner retell one observation aloud.",
        ],
        "classroom_facilitation": [
            "Use partner talk before whole-group sharing so younger learners can rehearse one accurate idea about Africa.",
        ],
        "pacing_hints": [
            "Pause after the map comparison for a quick turn-and-talk before moving into guided region naming.",
        ],
        "intervention_hints": [
            "If learners generalize too broadly, return to the words continent, region, and diversity with visual supports.",
        ],
        "community_extensions": [
            "Invite learners to notice how community stories and maps can work together to teach place with accuracy.",
        ],
    },
    "Regions, Rivers, and Routes": {
        "teacher_addendum": (
            " Facilitation: model one think-aloud about how water and movement shape daily life before asking learners "
            "to describe their own examples. Homeschool adaptation: let the learner trace the route with a finger or pencil "
            "before answering in words."
        ),
        "discussion_extensions": [
            "How do routes help people share more than things?",
        ],
        "family_extensions": [
            "Ask at home about a road, river, path, or bus route that helps people stay connected in your community.",
        ],
        "homeschool_adaptations": [
            "Turn the guided map into a conversation by stopping after each route and asking what people might carry, share, or learn there.",
        ],
        "classroom_facilitation": [
            "Have learners point, trace, and speak so map understanding is supported by movement and oral language.",
        ],
        "pacing_hints": [
            "Keep the vocabulary loop short and concrete before asking for independent explanations.",
        ],
        "intervention_hints": [
            "Use picture cards for river, route, travel, and trade if learners need extra vocabulary support.",
        ],
        "community_extensions": [
            "Invite learners to compare a local travel path with one route discussed in the lesson.",
        ],
    },
    "Map Stories of Home and Place": {
        "teacher_addendum": (
            " Facilitation: protect choice and belonging by inviting drawing, speaking, or writing rather than one required "
            "mode of response. Family/community extension: encourage a short home conversation about a place that feels meaningful."
        ),
        "discussion_extensions": [
            "How can listening to someone else's place story help us show care?",
        ],
        "family_extensions": [
            "Invite a family member to share a story about a place that matters to them and what makes it feel special.",
        ],
        "homeschool_adaptations": [
            "Create a simple place-story page together with one drawing and one sentence about belonging.",
        ],
        "classroom_facilitation": [
            "Use sentence stems and opt-in sharing so learners can participate without pressure.",
        ],
        "pacing_hints": [
            "Leave time for quiet reflection before discussion so younger learners can form their ideas.",
        ],
        "intervention_hints": [
            "If learners struggle to begin, offer prompts about sounds, people, routines, or feelings connected to a place.",
        ],
        "community_extensions": [
            "Invite learners to think about how homes, schools, and neighborhoods all hold stories of belonging.",
        ],
    },
    "Learning from Great African Kingdoms": {
        "teacher_addendum": (
            " Facilitation: anchor the lesson in dignity and achievement by naming scholarship, leadership, and trade as "
            "examples of human excellence. Classroom adaptation: use one evidence chart that stays visible through the discussion."
        ),
        "discussion_extensions": [
            "What kind of leader helps learning grow in a community?",
        ],
        "family_extensions": [
            "At home, ask who in your family or community helps others learn and what makes that leadership meaningful.",
        ],
        "homeschool_adaptations": [
            "Turn the fact card task into a read-talk-draw cycle, with one oral retelling before writing.",
        ],
        "classroom_facilitation": [
            "Keep one contribution from each kingdom visible on the board so learners can compare evidence clearly.",
        ],
        "pacing_hints": [
            "Pause after each kingdom example so learners can restate the contribution in their own words.",
        ],
        "intervention_hints": [
            "If the timeline feels abstract, ground the discussion in the concrete idea of people gathering to trade and learn.",
        ],
        "community_extensions": [
            "Invite learners to connect a historical learning center to a school, library, or community hub they know today.",
        ],
    },
    "Markets, Stories, and Community Life": {
        "teacher_addendum": (
            " Facilitation: help learners notice that community spaces share culture, memory, and care alongside goods. "
            "Family/community extension: encourage a conversation about where stories are shared in daily life."
        ),
        "discussion_extensions": [
            "Why might a story shared in a community space matter for more than one generation?",
        ],
        "family_extensions": [
            "Ask someone at home where people in your family or community share stories, news, or traditions.",
        ],
        "homeschool_adaptations": [
            "Use a pretend market conversation where the learner names one good and one idea or story that could be shared there.",
        ],
        "classroom_facilitation": [
            "Let pairs sort examples of goods, news, music, and stories before whole-group discussion.",
        ],
        "pacing_hints": [
            "Keep the exchange examples concrete and familiar before moving to abstract cultural ideas.",
        ],
        "intervention_hints": [
            "If learners focus only on buying and selling, return to the idea of community gathering and knowledge-sharing.",
        ],
        "community_extensions": [
            "Invite learners to notice where local communities gather to exchange food, help, stories, or music.",
        ],
    },
    "Wisdom Keepers and Libraries": {
        "teacher_addendum": (
            " Facilitation: name oral and written knowledge as equally worthy of care so learners see wisdom as something communities protect together. "
            "Homeschool adaptation: alternate reading with oral retelling."
        ),
        "discussion_extensions": [
            "Who helps protect important knowledge in a family or community?",
        ],
        "family_extensions": [
            "Ask someone at home about a story, saying, recipe, or lesson that has been passed from one person to another.",
        ],
        "homeschool_adaptations": [
            "Create a simple family wisdom list with one thing the learner wants to remember and share.",
        ],
        "classroom_facilitation": [
            "Let learners categorize examples as oral, written, or both to make preservation methods more concrete.",
        ],
        "pacing_hints": [
            "Alternate short reading moments with oral restatement so the content stays manageable for younger learners.",
        ],
        "intervention_hints": [
            "If preserving knowledge feels abstract, connect it to keeping class books, family sayings, or important stories safe.",
        ],
        "community_extensions": [
            "Invite learners to notice how elders, librarians, teachers, and storytellers all help communities remember.",
        ],
    },
    "Living Lands and Ecosystems": {
        "teacher_addendum": (
            " Facilitation: keep observation joyful and concrete by focusing on what living things need and how places support life. "
            "Family/community extension: invite learners to observe one living thing near home."
        ),
        "discussion_extensions": [
            "How can careful observation help us care for living things?",
        ],
        "family_extensions": [
            "Take a short walk or window observation at home and name one plant, animal, or weather pattern you notice together.",
        ],
        "homeschool_adaptations": [
            "Turn the observation prompt into a small nature notebook page with one sketch and one sentence.",
        ],
        "classroom_facilitation": [
            "Use gestures and visuals to reinforce habitat, ecosystem, and observation language.",
        ],
        "pacing_hints": [
            "Pause after each ecosystem example so learners can describe one thing they noticed before moving on.",
        ],
        "intervention_hints": [
            "If ecosystem vocabulary is difficult, return to simple questions about where living things get food, water, and shelter.",
        ],
        "community_extensions": [
            "Help learners connect African ecosystem study to respectful observation of the environments around them.",
        ],
    },
    "Music, Art, and Celebration": {
        "teacher_addendum": (
            " Facilitation: emphasize belonging, expression, and joy rather than performance pressure. Classroom adaptation: "
            "offer drawing, rhythm, speaking, or movement as valid responses."
        ),
        "discussion_extensions": [
            "How can celebrations help people remember who they are together?",
        ],
        "family_extensions": [
            "Invite a family member to share a song, rhythm, artwork, or celebration tradition that carries meaning for them.",
        ],
        "homeschool_adaptations": [
            "Create a simple home celebration response with a drawing, clap pattern, or short spoken explanation.",
        ],
        "classroom_facilitation": [
            "Use multimodal response stations so learners can choose how to show understanding.",
        ],
        "pacing_hints": [
            "Give a short quiet reflection before asking learners to share an artistic response.",
        ],
        "intervention_hints": [
            "If learners feel hesitant, invite them to describe an image or sound before creating their own response.",
        ],
        "community_extensions": [
            "Invite learners to notice how art and celebration help communities share memory, gratitude, and joy.",
        ],
    },
    "Caring for Land and Community": {
        "teacher_addendum": (
            " Facilitation: close the pathway with agency by helping learners choose one realistic act of care they can explain. "
            "Homeschool/classroom adaptation: keep the care action small, concrete, and doable."
        ),
        "discussion_extensions": [
            "What makes a caring action small enough to do and big enough to matter?",
        ],
        "family_extensions": [
            "Choose one small care action at home, such as cleaning a shared space, helping a neighbor, or caring for a plant.",
        ],
        "homeschool_adaptations": [
            "Turn the final reflection into a family care plan with one action, one helper, and one reason it matters.",
        ],
        "classroom_facilitation": [
            "Invite learners to propose one class care action and explain how it supports people or place.",
        ],
        "pacing_hints": [
            "Leave time for synthesis so learners can connect geography, community, art, and care before closure.",
        ],
        "intervention_hints": [
            "If learners struggle to name an action, offer examples tied to home, school, or local environment.",
        ],
        "community_extensions": [
            "Help learners connect pathway learning to shared responsibility in neighborhoods, schools, and community spaces.",
        ],
    },
}

DEMO_USERS = {
    "org_admin": {
        "firstname": "Olivia",
        "lastname": "Admin",
        "username": "orgadmin",
        "email": "orgadmin@demo.com",
        "role": "admin",
    },
    "teacher": {
        "firstname": "Tariq",
        "lastname": "Teacher",
        "username": "teacher",
        "email": "teacher@demo.com",
        "role": "teacher",
    },
    "parent": {
        "firstname": "Paula",
        "lastname": "Parent",
        "username": "parent",
        "email": "parent@demo.com",
        "role": "parent",
    },
    "student1": {
        "firstname": "Sami",
        "lastname": "Student",
        "username": "student1",
        "email": "student1@demo.com",
        "role": "student",
    },
    "student2": {
        "firstname": "Sasha",
        "lastname": "Student",
        "username": "student2",
        "email": "student2@demo.com",
        "role": "student",
    },
    "content_admin": {
        "firstname": "Carmen",
        "lastname": "Content",
        "username": "contentadmin",
        "email": "content@demo.com",
        "role": "content_admin",
    },
    "super_admin": {
        "firstname": "Sam",
        "lastname": "Super",
        "username": "superadmin",
        "email": "superadmin@demo.com",
        "role": "super_admin",
    },
}

MEMBERSHIP_MAP = {
    "org_admin": OrganizationRole.ORG_ADMIN,
    "teacher": OrganizationRole.TEACHER,
    "parent": OrganizationRole.PARENT,
    "student1": OrganizationRole.STUDENT,
    "student2": OrganizationRole.STUDENT,
    "content_admin": OrganizationRole.CONTENT_ADMIN,
}


def _get_or_create_demo_org(db) -> Organization:
    org = db.query(Organization).filter(Organization.name == DEMO_ORG_NAME).first()
    if org is None:
        org = Organization(
            name=DEMO_ORG_NAME,
            type=OrganizationType.SCHOOL,
            country="US",
            timezone="America/New_York",
        )
        db.add(org)
        db.flush()
        return org

    org.type = OrganizationType.SCHOOL
    org.country = "US"
    org.timezone = "America/New_York"
    db.flush()
    return org


def _upsert_demo_user(db, profile: dict[str, str]) -> User:
    user = (
        db.query(User)
        .filter(
            or_(
                User.username == profile["username"],
                User.email == profile["email"],
            )
        )
        .first()
    )

    if user is None:
        user = User(username=profile["username"], email=profile["email"])
        db.add(user)

    user.firstname = profile["firstname"]
    user.lastname = profile["lastname"]
    user.username = profile["username"]
    user.email = profile["email"]
    user.role = profile["role"]
    user.hashed_password = hash_password(DEMO_PASSWORD)
    user.updated_at = datetime.utcnow()

    db.flush()
    return user


def _ensure_membership(db, org: Organization, user: User, role: OrganizationRole) -> None:
    membership = (
        db.query(OrganizationMembership)
        .filter(
            OrganizationMembership.organization_id == org.id,
            OrganizationMembership.user_id == user.id,
        )
        .first()
    )
    if membership is None:
        membership = OrganizationMembership(
            organization_id=org.id,
            user_id=user.id,
            role=role,
            status=MembershipStatus.ACTIVE,
        )
        db.add(membership)
    else:
        membership.role = role
        membership.status = MembershipStatus.ACTIVE

    db.flush()


def _get_or_create_course(db, org: Organization, content_admin: User) -> Course:
    course = (
        db.query(Course)
        .filter(
            Course.organization_id == org.id,
            Course.title.in_(LEGACY_DEMO_COURSE_TITLES),
        )
        .first()
    )
    if course is None:
        course = Course(
            title=DEMO_COURSE_TITLE,
            description="Flagship K-5 interdisciplinary course that introduces Africa through geography, history, science, arts, and community-centered learning.",
            subject="Interdisciplinary Studies",
            age_band_min=5,
            age_band_max=11,
            default_locale="en",
            learning_objectives="Learners build foundational understanding of Africa through place-based geography, history, ecosystems, storytelling, arts, and community reflection.",
            skill_tags=[
                "flagship-pathway",
                "afrocentric-learning",
                "geography",
                "history",
                "science",
                "arts",
            ],
            standards_metadata={
                "pathway_key": "introduction-to-africa",
                "grade_band": "K-5",
                "pacing_model": "guided-flexible",
                "flagship": True,
                "interdisciplinary": True,
            },
            created_by=content_admin.id,
            organization_id=org.id,
        )
        db.add(course)
    else:
        course.title = DEMO_COURSE_TITLE
        course.description = "Flagship K-5 interdisciplinary course that introduces Africa through geography, history, science, arts, and community-centered learning."
        course.subject = "Interdisciplinary Studies"
        course.age_band_min = 5
        course.age_band_max = 11
        course.default_locale = "en"
        course.learning_objectives = "Learners build foundational understanding of Africa through place-based geography, history, ecosystems, storytelling, arts, and community reflection."
        course.skill_tags = [
            "flagship-pathway",
            "afrocentric-learning",
            "geography",
            "history",
            "science",
            "arts",
        ]
        course.standards_metadata = {
            "pathway_key": "introduction-to-africa",
            "grade_band": "K-5",
            "pacing_model": "guided-flexible",
            "flagship": True,
            "interdisciplinary": True,
        }
        course.created_by = content_admin.id
        course.organization_id = org.id
        course.updated_at = datetime.utcnow()

    db.flush()
    return course


def _get_or_create_course_version(db, course: Course, content_admin: User) -> CourseVersion:
    version = (
        db.query(CourseVersion)
        .filter(
            CourseVersion.course_id == course.id,
            CourseVersion.version_number == 1,
        )
        .first()
    )
    if version is None:
        version = CourseVersion(
            course_id=course.id,
            version_number=1,
            status=CourseVersionStatus.PUBLISHED,
            changelog="Initial published version",
            published_at=datetime.utcnow(),
            published_by=content_admin.id,
        )
        db.add(version)
    else:
        version.status = CourseVersionStatus.PUBLISHED
        version.changelog = "Initial published version"
        version.published_at = version.published_at or datetime.utcnow()
        version.published_by = content_admin.id

    db.flush()
    return version


def _get_or_create_section(db, org: Organization, version: CourseVersion, teacher: User) -> Section:
    section = (
        db.query(Section)
        .filter(
            Section.organization_id == org.id,
            Section.course_version_id == version.id,
            Section.name == DEMO_SECTION_NAME,
        )
        .first()
    )
    if section is None:
        section = Section(
            organization_id=org.id,
            course_version_id=version.id,
            name=DEMO_SECTION_NAME,
            mode=SectionMode.IN_PERSON,
            start_date=datetime.utcnow(),
            created_by=teacher.id,
        )
        db.add(section)
    else:
        section.mode = SectionMode.IN_PERSON
        section.start_date = section.start_date or datetime.utcnow()
        section.created_by = teacher.id

    db.flush()
    return section


def _sync_lesson_sources(db, lesson: Lesson, sources: list[dict[str, str]]) -> None:
    existing_sources = list(lesson.sources or [])

    for index, source_seed in enumerate(sources):
        if index < len(existing_sources):
            source = existing_sources[index]
            source.citation = source_seed["citation"]
            source.url = source_seed["url"]
        else:
            db.add(
                Source(
                    lesson_id=lesson.id,
                    citation=source_seed["citation"],
                    url=source_seed["url"],
                )
            )

    for stale_source in existing_sources[len(sources) :]:
        db.delete(stale_source)


def _sync_lesson_activities(db, lesson: Lesson, activities: list[dict[str, str | int]]) -> None:
    existing_activities = sorted(
        list(lesson.activities or []),
        key=lambda activity: (
            activity.order is None,
            activity.order if activity.order is not None else 0,
            str(activity.id),
        ),
    )

    for index, activity_seed in enumerate(activities):
        if index < len(existing_activities):
            activity = existing_activities[index]
        else:
            activity = Activity(lesson_id=lesson.id)
            db.add(activity)

        activity.type = str(activity_seed["type"])
        activity.title = str(activity_seed["title"])
        activity.content = str(activity_seed["content"])
        activity.order = int(activity_seed["order"])

    for stale_activity in existing_activities[len(activities) :]:
        db.delete(stale_activity)


def _sync_assessment_questions(db, assessment: Assessment, questions: list[dict[str, object]]) -> dict[int, Question]:
    existing_questions = sorted(
        list(assessment.questions or []),
        key=lambda question: (
            question.order is None,
            question.order if question.order is not None else 0,
            str(question.id),
        ),
    )

    for index, question_seed in enumerate(questions):
        if index < len(existing_questions):
            question = existing_questions[index]
        else:
            question = Question(assessment_id=assessment.id)
            db.add(question)

        question.prompt = str(question_seed["prompt"])
        question.question_type = str(question_seed.get("question_type", "multiple_choice"))
        question.choices = list(question_seed.get("choices", []))
        question.correct_answer = str(question_seed["correct_answer"])
        question.explanation = str(question_seed["explanation"]) if question_seed.get("explanation") else None
        question.points = float(question_seed.get("points", 1))
        question.order = int(question_seed["order"])

    if not assessment.attempts:
        for stale_question in existing_questions[len(questions) :]:
            db.delete(stale_question)

    db.flush()
    return {question.order: question for question in assessment.questions}


def _sync_assessment_competency_alignments(
    db,
    assessment: Assessment,
    alignments: list[dict[str, object]],
    questions_by_order: dict[int, Question],
) -> None:
    for existing_alignment in list(assessment.competency_alignments or []):
        db.delete(existing_alignment)
    db.flush()

    for alignment_seed in alignments:
        question_order = alignment_seed.get("question_order")
        question = questions_by_order.get(int(question_order)) if question_order is not None else None
        db.add(
            AssessmentCompetencyAlignment(
                assessment_id=assessment.id,
                question_id=question.id if question is not None else None,
                objective_key=str(alignment_seed["objective_key"]),
                objective_title=str(alignment_seed["objective_title"]) if alignment_seed.get("objective_title") else None,
                objective_type=str(alignment_seed.get("objective_type", "objective")),
                weight=float(alignment_seed.get("weight", 1.0)),
                mastery_threshold=float(alignment_seed.get("mastery_threshold", 80.0)),
                metadata_=dict(alignment_seed.get("metadata", {})),
            )
        )


def _default_flagship_support_profile(lesson_seed: dict[str, object]) -> dict[str, object]:
    lesson_title = str(lesson_seed["title"])
    objective = str(lesson_seed.get("objective") or "the lesson goal")
    return {
        "teacher_addendum": (
            " Facilitation: use brief modeling, supportive discussion, and age-appropriate examples to help learners "
            f"work toward {objective.lower()}. Family/community extension: invite a short home or community "
            "conversation that helps learners connect the lesson to people, place, or care."
        ),
        "discussion_extensions": [
            f"What is one important idea from {lesson_title} that you would want to explain to someone else?",
        ],
        "family_extensions": [
            f"Invite a family or community member to talk with the learner about one idea from {lesson_title}.",
        ],
        "homeschool_adaptations": [
            "Break the lesson into short read-talk-reflect moments and let the learner respond aloud before writing.",
        ],
        "classroom_facilitation": [
            "Use partner rehearsal before whole-group sharing so learners can practice one clear idea with confidence.",
        ],
        "pacing_hints": [
            "Pause after each major section to restate the key idea in simple language before moving on.",
        ],
        "intervention_hints": [
            "Return to visuals, sentence stems, and one-step questions if learners need extra scaffolding.",
        ],
        "remediation_review_prompts": [
            f"Say, draw, or write one idea from {lesson_title} that you want to remember.",
            f"Use a lesson word to explain how {objective.lower()} in your own way.",
        ],
        "enrichment_extensions": [
            f"Look a little deeper at {lesson_title} by connecting one lesson idea to a place, community, or question you want to explore next.",
            f"Share one bigger question from {lesson_title} that could lead to another story, map, artwork, or conversation.",
        ],
        "community_extensions": [
            "Encourage learners to notice how the lesson connects to community knowledge, care, or belonging.",
        ],
    }


def _get_flagship_support_profile(lesson_seed: dict[str, object]) -> dict[str, object]:
    lesson_title = str(lesson_seed["title"])
    support_profile = _default_flagship_support_profile(lesson_seed)
    support_profile.update(DEMO_FLAGSHIP_SUPPORT_PROFILES.get(lesson_title) or {})
    return support_profile


def _build_flagship_teacher_notes(lesson_seed: dict[str, object]) -> str:
    base_notes = str(lesson_seed["teacher_notes"])
    support_profile = _get_flagship_support_profile(lesson_seed)
    return f"{base_notes}{support_profile['teacher_addendum']}"


def _build_flagship_discussion_questions(lesson_seed: dict[str, object]) -> list[str]:
    base_questions = list(lesson_seed["discussion_questions"])
    support_profile = _get_flagship_support_profile(lesson_seed)
    return base_questions + list(support_profile["discussion_extensions"])


def _build_flagship_standards_metadata(lesson_seed: dict[str, object]) -> dict[str, object]:
    metadata = dict(lesson_seed["standards_metadata"])
    support_profile = _get_flagship_support_profile(lesson_seed)
    metadata.update(
        {
            "family_extensions": list(support_profile["family_extensions"]),
            "homeschool_adaptations": list(support_profile["homeschool_adaptations"]),
            "classroom_facilitation": list(support_profile["classroom_facilitation"]),
            "pacing_hints": list(support_profile["pacing_hints"]),
            "intervention_hints": list(support_profile["intervention_hints"]),
            "remediation_review_prompts": list(support_profile["remediation_review_prompts"]),
            "enrichment_extensions": list(support_profile["enrichment_extensions"]),
            "community_extensions": list(support_profile["community_extensions"]),
        }
    )
    return metadata


def _ensure_flagship_assessments(db, course: Course, content_admin: User) -> None:
    units_by_title = {unit.title: unit for unit in course.units}
    lessons_by_key = {
        (unit.title, lesson.title): lesson
        for unit in course.units
        for lesson in unit.lessons
    }

    for assessment_seed in DEMO_FLAGSHIP_ASSESSMENTS:
        scope = str(assessment_seed["scope"])
        unit = units_by_title.get(str(assessment_seed["unit_title"])) if assessment_seed.get("unit_title") else None
        lesson = (
            lessons_by_key.get((str(assessment_seed["unit_title"]), str(assessment_seed["lesson_title"])))
            if assessment_seed.get("unit_title") and assessment_seed.get("lesson_title")
            else None
        )

        query = db.query(Assessment).filter(Assessment.title == assessment_seed["title"])
        if scope == "lesson" and lesson is not None:
            query = query.filter(Assessment.lesson_id == lesson.id)
        elif scope == "unit" and unit is not None:
            query = query.filter(Assessment.unit_id == unit.id)
        elif scope == "course":
            query = query.filter(Assessment.course_id == course.id)

        assessment = query.first()
        if assessment is None:
            assessment = Assessment(title=str(assessment_seed["title"]))
            db.add(assessment)
            db.flush()

        assessment.title = str(assessment_seed["title"])
        assessment.description = str(assessment_seed["description"])
        assessment.unit_id = unit.id if scope == "unit" and unit is not None else None
        assessment.lesson_id = lesson.id if scope == "lesson" and lesson is not None else None
        assessment.course_id = course.id if scope == "course" else None
        assessment.program_id = None
        assessment.assessment_scope = scope
        assessment.assessment_state = str(assessment_seed["assessment_state"])
        assessment.availability_state = str(assessment_seed["availability_state"])
        assessment.passing_score = float(assessment_seed.get("passing_score", 70.0))
        assessment.max_attempts = int(assessment_seed["max_attempts"]) if assessment_seed.get("max_attempts") is not None else None
        assessment.policy_metadata = dict(assessment_seed.get("policy_metadata", {}))
        assessment.lifecycle_metadata = dict(assessment_seed.get("lifecycle_metadata", {}))
        assessment.created_by = content_admin.id

        db.flush()
        questions_by_order = _sync_assessment_questions(db, assessment, list(assessment_seed["questions"]))
        _sync_assessment_competency_alignments(
            db,
            assessment,
            list(assessment_seed["competency_alignments"]),
            questions_by_order,
        )

    db.flush()


def _ensure_governed_demo_lessons(db, course: Course, version: CourseVersion) -> None:
    for unit_seed in DEMO_UNITS:
        unit = (
            db.query(Unit)
            .filter(
                Unit.course_id == course.id,
                Unit.title == unit_seed["title"],
            )
            .first()
        )
        if unit is None:
            unit = Unit(
                course_id=course.id,
                course_version_id=version.id,
                title=unit_seed["title"],
                content=unit_seed["content"],
                order=unit_seed["order"],
            )
            db.add(unit)
            db.flush()
        else:
            unit.course_version_id = version.id
            unit.content = unit_seed["content"]
            unit.order = unit_seed["order"]

        for lesson_seed in unit_seed["lessons"]:
            lesson = (
                db.query(Lesson)
                .filter(
                    Lesson.unit_id == unit.id,
                    Lesson.title == lesson_seed["title"],
                )
                .first()
            )
            if lesson is None:
                lesson = Lesson(unit_id=unit.id, title=lesson_seed["title"])
                db.add(lesson)
                db.flush()

            lesson.objective = lesson_seed["objective"]
            lesson.learning_objectives = lesson_seed["learning_objectives"]
            lesson.key_concepts = lesson_seed["key_concepts"]
            lesson.teacher_notes = _build_flagship_teacher_notes(lesson_seed)
            lesson.discussion_questions = _build_flagship_discussion_questions(lesson_seed)
            lesson.hook = lesson_seed["hook"]
            lesson.content = lesson_seed["content"]
            lesson.guided_practice = lesson_seed["guided_practice"]
            lesson.independent_practice = lesson_seed["independent_practice"]
            lesson.assessment = lesson_seed["assessment"]
            lesson.skill_tags = lesson_seed["skill_tags"]
            lesson.standards_metadata = _build_flagship_standards_metadata(lesson_seed)
            lesson.review_status = "approved"
            lesson.order = lesson_seed["order"]
            lesson.duration_minutes = lesson_seed["duration_minutes"]

            _sync_lesson_sources(db, lesson, lesson_seed["sources"])
            _sync_lesson_activities(db, lesson, lesson_seed["activities"])

    db.flush()


def _ensure_enrollment(db, section: Section, user: User) -> None:
    enrollment = (
        db.query(Enrollment)
        .filter(
            Enrollment.section_id == section.id,
            Enrollment.user_id == user.id,
        )
        .first()
    )
    if enrollment is None:
        db.add(Enrollment(section_id=section.id, user_id=user.id))
        db.flush()


def run() -> None:
    db = SessionLocal()
    try:
        org = _get_or_create_demo_org(db)
        users = {
            key: _upsert_demo_user(db, profile)
            for key, profile in DEMO_USERS.items()
        }

        for key, role in MEMBERSHIP_MAP.items():
            _ensure_membership(db, org, users[key], role)

        course = _get_or_create_course(db, org, users["content_admin"])
        version = _get_or_create_course_version(db, course, users["content_admin"])
        _ensure_governed_demo_lessons(db, course, version)
        _ensure_flagship_assessments(db, course, users["content_admin"])
        section = _get_or_create_section(db, org, version, users["teacher"])

        _ensure_enrollment(db, section, users["student1"])
        _ensure_enrollment(db, section, users["student2"])

        db.commit()
        print(
            "Seeded demo data. Login uses usernames with password "
            f"'{DEMO_PASSWORD}' (for example: student1 / {DEMO_PASSWORD}, teacher / {DEMO_PASSWORD})."
        )
    finally:
        db.close()


if __name__ == "__main__":
    run()
