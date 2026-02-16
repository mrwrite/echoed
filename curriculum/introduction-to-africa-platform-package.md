# EchoEd Demo Course Package: Introduction to Africa (K–5)

## 1) Structured JSON Blocks

### Phase 1: Course Metadata

```json
{
  "course": {
    "id": "course_intro_africa_k5_demo",
    "title": "Introduction to Africa",
    "grade_band": "K-5",
    "differentiation_tags": ["K-2", "3-5"],
    "subject": ["Social Studies", "Geography", "Literacy"],
    "duration": "4-6 weeks",
    "description_marketing": [
      "Introduction to Africa is a joyful, standards-aligned elementary course that helps students build global understanding through maps, stories, and inquiry. Learners explore Africa as a diverse continent with 54 countries, developing geographic thinking while practicing foundational literacy skills.",
      "Designed for flexible implementation in K-5 classrooms, the course blends whole-group teaching, hands-on practice, and differentiated tasks for K-2 and grades 3-5. Students investigate major features such as the Sahara Desert and Nile River, examine ecosystems and animals, and learn how geography connects to daily life.",
      "The culminating celebration project turns learning into student voice: children present what they discovered through posters, mini-books, or short presentations. With printable resources, built-in assessments, and teacher-facing supports, this demo is ready for district pilots and organization-level showcase."
    ],
    "learning_outcomes": [
      "Locate Africa on a globe and world map with at least 90% accuracy.",
      "Explain that Africa is a continent made up of 54 countries.",
      "Identify and label key physical features including the Sahara Desert and Nile River.",
      "Describe at least three African ecosystems and one matching animal adaptation for each.",
      "Use grade-appropriate vocabulary (e.g., continent, climate, ecosystem) in speaking and writing.",
      "Compare how climate and landforms influence transportation, homes, and food in different regions.",
      "Retell an African folktale and identify a theme or lesson.",
      "Create and present a final project using evidence from maps, texts, and class activities.",
      "Show respectful language when discussing cultures, languages, and traditions across African countries.",
      "Reflect on learning by writing or discussing one new idea and one question for future study."
    ],
    "skills_tags": [
      "map-reading",
      "spatial-reasoning",
      "informational-reading",
      "discussion",
      "writing-to-learn",
      "cultural-literacy",
      "presentation",
      "collaboration"
    ],
    "vocabulary": [
      "continent",
      "country",
      "equator",
      "map key",
      "legend",
      "desert",
      "river",
      "rainforest",
      "savanna",
      "climate",
      "ecosystem",
      "habitat",
      "tradition",
      "folktale",
      "diversity"
    ],
    "sel_alignment": [
      "Self-awareness: identify what I know and what I still wonder.",
      "Social awareness: respect similarities and differences across communities.",
      "Relationship skills: listen, take turns, and ask thoughtful questions.",
      "Responsible decision-making: use accurate facts and avoid stereotypes.",
      "Self-management: complete project milestones and reflect on feedback."
    ],
    "culturally_responsive_notes": [
      "Teach Africa as a continent of many countries, languages, and lived experiences.",
      "Use examples from multiple regions (North, West, East, Central, and Southern Africa).",
      "Pair historical and present-day examples to avoid a single-story narrative.",
      "Center dignity and everyday life (school, family, work, arts, science, cities, and rural communities).",
      "Use teacher-vetted media created by or featuring people from African countries whenever possible."
    ]
  }
}
```

### Phase 2 + 3: Units and Lessons (Course > Unit > Lesson > Activity-ready)

```json
{
  "units": [
    {
      "title": "Unit 1: What Is Africa?",
      "overview": "Students build foundational map knowledge and learn that Africa is a continent with 54 countries.",
      "essential_question": "How do maps help us understand Africa as a continent?",
      "duration": "4-5 class periods",
      "standards_alignment": ["NCSS Geography", "C3 D2.Geo.1-2", "CCSS RI/SL K-5"],
      "lessons": [
        {
          "title": "Lesson 1.1 - Continent Detective",
          "learning_objectives": ["Identify Africa on a globe and map", "Define continent"],
          "hook": "Students solve a map mystery using continent clues.",
          "direct_instruction": "Teacher models how to find continents and oceans, then zooms into Africa.",
          "guided_practice": "Class points to Africa on projected maps; partners use sentence frame 'Africa is a continent.'",
          "independent_practice": "K-2: color Africa on world map. 3-5: label all continents and compass rose.",
          "assessment": {"type": "exit ticket", "prompt": "Circle Africa and write/dictate one fact."},
          "printable_artifacts": ["africa_map_blank.pdf"],
          "media_assets": ["media/world-map-animated.mp4"]
        },
        {
          "title": "Lesson 1.2 - 54 Countries, Many Places",
          "learning_objectives": ["Explain that Africa has 54 countries", "Distinguish continent vs country"],
          "hook": "Country-card reveal game.",
          "direct_instruction": "Teacher introduces examples of countries from different African regions.",
          "guided_practice": "Students sort cards into continent or country.",
          "independent_practice": "K-2: picture sort. 3-5: write 3 country facts from class cards.",
          "assessment": {"type": "checklist", "criteria": ["Uses terms correctly", "Names at least two countries"]},
          "printable_artifacts": ["vocabulary_cards_africa_unit.pdf"],
          "media_assets": ["media/country-photo-set.zip"]
        },
        {
          "title": "Lesson 1.3 - Labeling the Map",
          "learning_objectives": ["Label Africa, Atlantic Ocean, Indian Ocean", "Use map key symbols"],
          "hook": "Quick draw race: ocean or land?",
          "direct_instruction": "Teacher models map labeling and legend reading.",
          "guided_practice": "Shared labeling with think-aloud.",
          "independent_practice": "K-2: trace and label 3 terms. 3-5: add equator and neighboring seas.",
          "assessment": {"type": "artifact", "name": "Map Labeling Sheet"},
          "printable_artifacts": ["africa_map_labeled.pdf"],
          "media_assets": ["media/map-labeling-demo.png"]
        }
      ]
    },
    {
      "title": "Unit 2: Land, Water, and Climate",
      "overview": "Students explore major physical features and climate zones across Africa.",
      "essential_question": "How do landforms and climate shape life across Africa?",
      "duration": "5 class periods",
      "standards_alignment": ["NCSS Geography", "NGSS 3-ESS2", "CCSS RI.3-5"],
      "lessons": [
        {
          "title": "Lesson 2.1 - Big Features of Africa",
          "learning_objectives": ["Locate Sahara Desert and Nile River", "Name two other major features"],
          "hook": "Mystery postcards from river, mountain, and desert locations.",
          "direct_instruction": "Teacher introduces Sahara Desert, Nile River, Congo River, Zambezi River, Atlas Mountains, Mt. Kilimanjaro.",
          "guided_practice": "Students place feature cards on class map.",
          "independent_practice": "K-2: sticker map. 3-5: short paragraph on one feature.",
          "assessment": {"type": "oral + map check", "prompt": "Point and name two features."},
          "printable_artifacts": ["africa_map_labeled.pdf"],
          "media_assets": ["media/physical-map-africa.jpg"]
        },
        {
          "title": "Lesson 2.2 - Climate Zones",
          "learning_objectives": ["Describe desert, rainforest, savanna, Mediterranean climates", "Match climate to simple characteristics"],
          "hook": "Weather wardrobe challenge.",
          "direct_instruction": "Teacher uses climate color map and simple weather data icons.",
          "guided_practice": "Class completes climate-to-picture matching.",
          "independent_practice": "K-2: draw one climate scene. 3-5: compare two climates using Venn chart.",
          "assessment": {"type": "quick quiz", "items": 5},
          "printable_artifacts": ["land_water_climate_sketch_sheet.pdf"],
          "media_assets": ["media/climate-zones-africa.svg"]
        },
        {
          "title": "Lesson 2.3 - Geography and Daily Life",
          "learning_objectives": ["Explain how environment can influence daily routines", "Use evidence from maps and photos"],
          "hook": "Photo talk: 'What do you notice? What do you wonder?'",
          "direct_instruction": "Teacher models claim-evidence sentence stems.",
          "guided_practice": "Students discuss homes, transportation, and farming examples.",
          "independent_practice": "K-2: complete sentence frame with drawing. 3-5: write claim + 2 evidences.",
          "assessment": {"type": "constructed response", "rubric": "2-point evidence rubric"},
          "printable_artifacts": ["land_water_climate_sketch_sheet.pdf"],
          "media_assets": ["media/photo-pack-daily-life.zip"]
        }
      ]
    },
    {
      "title": "Unit 3: People, Languages, and Culture",
      "overview": "Students learn that African cultures are diverse, dynamic, and rooted in local histories.",
      "essential_question": "How can we learn about people and culture with respect and curiosity?",
      "duration": "5 class periods",
      "standards_alignment": ["NCSS Culture", "CCSS SL K-5", "SEL Social Awareness"],
      "lessons": [
        {
          "title": "Lesson 3.1 - Many Languages, Many Communities",
          "learning_objectives": ["Identify examples of African languages", "Practice respectful comparisons"],
          "hook": "Greeting circle in multiple languages.",
          "direct_instruction": "Teacher introduces examples: Swahili, Arabic, Amharic, Hausa, Yoruba, Zulu.",
          "guided_practice": "Students match language cards to map regions (non-exhaustive).",
          "independent_practice": "K-2: greeting poster. 3-5: write reflection on language diversity.",
          "assessment": {"type": "discussion rubric", "focus": "respectful listening"},
          "printable_artifacts": ["vocabulary_cards_africa_unit.pdf"],
          "media_assets": ["media/greetings-audio-mix.mp3"]
        },
        {
          "title": "Lesson 3.2 - Music, Art, and Pattern",
          "learning_objectives": ["Recognize art and music as cultural expression", "Create a pattern with meaning"],
          "hook": "Rhythm echo game.",
          "direct_instruction": "Teacher shows examples of textiles, percussion patterns, and contemporary artwork.",
          "guided_practice": "Class co-creates a rhythm line and visual motif chart.",
          "independent_practice": "K-2: color pattern strip. 3-5: create pattern with artist statement.",
          "assessment": {"type": "artifact review", "criteria": ["Pattern repetition", "Meaning statement"]},
          "printable_artifacts": ["vocabulary_cards_africa_unit.pdf"],
          "media_assets": ["media/pattern-gallery-slides.pptx"]
        },
        {
          "title": "Lesson 3.3 - Everyday Life Across Places",
          "learning_objectives": ["Compare two communities using photos/text", "Avoid overgeneralization"],
          "hook": "Two-photo compare and contrast.",
          "direct_instruction": "Teacher models language: 'In one community...' 'In another community...'",
          "guided_practice": "Students sort observations into school, family, food, transport.",
          "independent_practice": "K-2: draw + label one comparison. 3-5: paragraph compare/contrast.",
          "assessment": {"type": "paragraph or oral recording", "rubric": "accuracy + respectful language"},
          "printable_artifacts": ["celebration_project_planner.pdf"],
          "media_assets": ["media/everyday-life-gallery.zip"]
        }
      ]
    },
    {
      "title": "Unit 4: Animals and Ecosystems",
      "overview": "Students connect habitats, climate, and animal adaptations.",
      "essential_question": "How do ecosystems support different animals across Africa?",
      "duration": "4-5 class periods",
      "standards_alignment": ["NGSS LS4", "NCSS Geography", "CCSS RI"],
      "lessons": [
        {
          "title": "Lesson 4.1 - Ecosystem Explorer",
          "learning_objectives": ["Define ecosystem and habitat", "Name 4 African ecosystem types"],
          "hook": "Habitat charades.",
          "direct_instruction": "Teacher introduces savanna, rainforest, desert, wetland with visuals.",
          "guided_practice": "Students place ecosystem icons on a large map.",
          "independent_practice": "K-2: matching cards. 3-5: ecosystem notes chart.",
          "assessment": {"type": "matching task", "auto_graded": true},
          "printable_artifacts": ["africa_animal_flashcards.pdf"],
          "media_assets": ["media/ecosystem-cards.png"]
        },
        {
          "title": "Lesson 4.2 - Animal Adaptations",
          "learning_objectives": ["Match animal traits to habitat", "Use because-statements"],
          "hook": "Who am I? adaptation clues.",
          "direct_instruction": "Teacher models how body parts/behaviors support survival.",
          "guided_practice": "Class completes adaptation sentence stems.",
          "independent_practice": "K-2: choose animal and dictate reason. 3-5: write two adaptation explanations.",
          "assessment": {"type": "short response", "prompt": "This animal survives because..."},
          "printable_artifacts": ["africa_animal_flashcards.pdf"],
          "media_assets": ["media/animal-closeups.zip"]
        },
        {
          "title": "Lesson 4.3 - Build a Food Web",
          "learning_objectives": ["Classify herbivore/carnivore/omnivore", "Construct a simple food web"],
          "hook": "Eat like? game.",
          "direct_instruction": "Teacher introduces food chain arrows and producer/consumer basics.",
          "guided_practice": "Small groups connect organism cards.",
          "independent_practice": "K-2: three-card chain. 3-5: five-organism web with labels.",
          "assessment": {"type": "performance check", "rubric": "correct links and vocabulary"},
          "printable_artifacts": ["africa_animal_flashcards.pdf"],
          "media_assets": ["media/food-web-template.pdf"]
        }
      ]
    },
    {
      "title": "Unit 5: Folktales and Traditions",
      "overview": "Students read, retell, and create stories inspired by folktale structures.",
      "essential_question": "What can stories teach us about values and community?",
      "duration": "4 class periods",
      "standards_alignment": ["CCSS RL K-5", "CCSS W K-5", "SEL"],
      "lessons": [
        {
          "title": "Lesson 5.1 - Reading a Folktale",
          "learning_objectives": ["Identify characters, setting, problem, solution", "Discuss lesson/theme"],
          "hook": "Story object mystery bag.",
          "direct_instruction": "Teacher read-aloud of age-appropriate folktale adaptation.",
          "guided_practice": "Class completes shared story map.",
          "independent_practice": "K-2: picture sequence. 3-5: short retell paragraph.",
          "assessment": {"type": "story map", "rubric": "4 elements present"},
          "printable_artifacts": ["mini_book_template_folktale.pdf"],
          "media_assets": ["media/folktale-audio.mp3"]
        },
        {
          "title": "Lesson 5.2 - Sequence and Retell",
          "learning_objectives": ["Use sequence words", "Retell with beginning-middle-end"],
          "hook": "Human timeline cards.",
          "direct_instruction": "Teacher models retell using first/next/then/finally.",
          "guided_practice": "Partners practice oral retells.",
          "independent_practice": "K-2: draw 3 scenes. 3-5: write 6-8 sentence retell.",
          "assessment": {"type": "oral fluency or writing sample"},
          "printable_artifacts": ["mini_book_template_folktale.pdf"],
          "media_assets": ["media/story-sequence-cards.png"]
        },
        {
          "title": "Lesson 5.3 - Create a Mini-Book",
          "learning_objectives": ["Publish a short folktale-inspired book", "Add illustrations and captions"],
          "hook": "Teacher author share.",
          "direct_instruction": "Teacher shows planning, drafting, revising process.",
          "guided_practice": "Students conference in pairs with checklist.",
          "independent_practice": "K-2: dictate text; 3-5: draft/edit independently.",
          "assessment": {"type": "published artifact", "rubric": "story structure + clarity"},
          "printable_artifacts": ["mini_book_template_folktale.pdf"],
          "media_assets": ["media/mini-book-example.pdf"]
        }
      ]
    },
    {
      "title": "Unit 6: Celebration Project",
      "overview": "Students synthesize learning in a final presentation and reflection.",
      "essential_question": "How can we teach others what we learned about Africa with accuracy and respect?",
      "duration": "5 class periods + showcase",
      "standards_alignment": ["CCSS SL Presentation", "NCSS Integration", "SEL Reflection"],
      "lessons": [
        {
          "title": "Lesson 6.1 - Project Planning",
          "learning_objectives": ["Choose a focus topic", "Plan evidence and visuals"],
          "hook": "Gallery of sample projects.",
          "direct_instruction": "Teacher introduces project options and success criteria.",
          "guided_practice": "Students complete planner with teacher conference.",
          "independent_practice": "K-2: drawing + labels plan. 3-5: outline with 3 facts + source notes.",
          "assessment": {"type": "planner checkpoint", "artifact": "celebration_project_planner.pdf"},
          "printable_artifacts": ["celebration_project_planner.pdf"],
          "media_assets": ["media/project-examples-slide-deck.pptx"]
        },
        {
          "title": "Lesson 6.2 - Build and Rehearse",
          "learning_objectives": ["Create final product", "Practice speaking skills"],
          "hook": "Strong start sentence challenge.",
          "direct_instruction": "Teacher models voice level, eye contact, and transition words.",
          "guided_practice": "Peer rehearsal with glow/grow feedback.",
          "independent_practice": "K-2: 30-60 second share. 3-5: 2-3 minute presentation.",
          "assessment": {"type": "rubric", "files": ["presentation_rubric_k2.pdf", "presentation_rubric_35.pdf"]},
          "printable_artifacts": ["presentation_rubric_k2.pdf", "presentation_rubric_35.pdf"],
          "media_assets": ["media/presentation-tips-video.mp4"]
        },
        {
          "title": "Lesson 6.3 - Showcase and Reflect",
          "learning_objectives": ["Present learning to audience", "Reflect on growth and next questions"],
          "hook": "Celebration opening music and welcome.",
          "direct_instruction": "Teacher reviews respectful audience behaviors and feedback norms.",
          "guided_practice": "Class practice for introductions and Q&A.",
          "independent_practice": "Students present and submit reflection.",
          "assessment": {"type": "performance + reflection", "weight": "final"},
          "printable_artifacts": ["celebration_project_planner.pdf"],
          "media_assets": ["media/showcase-certificate-template.pdf"]
        }
      ]
    }
  ]
}
```

### Phase 6: Teacher Dashboard Demo Seed Data JSON

```json
{
  "students": [
    {
      "name": "Amina R.",
      "completed_lessons": ["1.1", "1.2", "1.3", "2.1", "2.2", "2.3", "3.1", "3.2", "3.3", "4.1", "4.2", "4.3", "5.1", "5.2", "5.3", "6.1", "6.2", "6.3"],
      "assessment_scores": {"map_quiz": 96, "climate_check": 92, "folktale_retell": 95, "final_project": 98},
      "strengths": ["Map labeling accuracy", "Evidence-based speaking"],
      "growth_areas": ["Ask deeper follow-up questions"]
    },
    {
      "name": "Ben T.",
      "completed_lessons": ["1.1", "1.2", "1.3", "2.1", "2.2", "3.1", "4.1", "4.2", "5.1", "6.1"],
      "assessment_scores": {"map_quiz": 74, "climate_check": 68, "folktale_retell": 79, "final_project": 76},
      "strengths": ["Oral discussion", "Creative visuals"],
      "growth_areas": ["Vocabulary precision", "Completing independent writing tasks"]
    },
    {
      "name": "Camila S.",
      "completed_lessons": ["1.1", "1.2", "1.3", "2.1", "2.2", "2.3", "3.1", "3.2", "4.1", "4.2", "5.1", "5.2", "6.1", "6.2"],
      "assessment_scores": {"map_quiz": 88, "climate_check": 84, "folktale_retell": 82, "final_project": 85},
      "strengths": ["Compare/contrast writing", "Collaboration"],
      "growth_areas": ["Reading fluency for oral presentations"]
    },
    {
      "name": "Diego M.",
      "completed_lessons": ["1.1", "1.2", "2.1", "2.2", "3.1", "3.3", "4.1", "4.2", "5.1", "5.2", "6.1"],
      "assessment_scores": {"map_quiz": 63, "climate_check": 59, "folktale_retell": 71, "final_project": 70},
      "strengths": ["Hands-on sorting tasks", "Class participation"],
      "growth_areas": ["Map feature retention", "Written response stamina"]
    },
    {
      "name": "Elena K.",
      "completed_lessons": ["1.1", "1.2", "1.3", "2.1", "2.2", "2.3", "3.1", "3.2", "3.3", "4.1", "4.2", "4.3", "5.1", "5.2", "5.3", "6.1", "6.2"],
      "assessment_scores": {"map_quiz": 91, "climate_check": 89, "folktale_retell": 93, "final_project": 90},
      "strengths": ["Academic vocabulary", "Thoughtful reflection"],
      "growth_areas": ["Time management during project build"]
    }
  ],
  "teacher_insights": [
    "Class average is strongest in oral discussion and project creativity.",
    "Map-specific reteach is recommended for 3 students before cumulative test.",
    "Sentence stems improved respectful compare/contrast language across all groups.",
    "Small-group support in Unit 2 increased climate vocabulary retention.",
    "Family showcase night had 90% attendance and strong student confidence growth."
  ]
}
```

---

## 2) Printable Markdown Sections (PDF-ready content)

### 1. `africa_map_blank.pdf`
**Student Page**
- Title: Blank Map of Africa
- Directions (K-2): Trace the continent outline. Color Africa green. Label: Africa.
- Directions (3-5): Label Africa, Atlantic Ocean, Indian Ocean, Mediterranean Sea, and Equator.
- Box prompt: "One fact I know about Africa: ________."

**Teacher Instructions**
- Use after Unit 1 Lesson 1.3.
- Model one label first, then release to students.
- Encourage map orientation language (north, south, east, west).

**Answer Key**
- Required labels: Africa.
- Extension labels: Atlantic Ocean (west), Indian Ocean (east), Mediterranean Sea (north), Equator (crossing central Africa).

### 2. `africa_map_labeled.pdf`
**Student Page**
- Reference map with labeled features: Africa, Sahara Desert, Nile River, Congo River, Zambezi River, Atlas Mountains, Mt. Kilimanjaro.
- Caption prompts:
  1. "A desert I can find is ____."
  2. "A river I can find is ____."

**Teacher Instructions**
- Use as scaffold for Unit 2.
- Pair students for partner pointing game.

**Answer Key**
- Accept exact feature labels listed above.

### 3. `vocabulary_cards_africa_unit.pdf`
**Student Page**
- 15 cut-out cards with term, kid-friendly definition, and picture box.
- Example: "Continent - one of Earth’s large land areas."

**Teacher Instructions**
- Print on cardstock for centers.
- K-2: matching game; 3-5: Frayer model extension.

**Answer Key**
- Matching set aligns term to definition list in metadata section.

### 4. `africa_animal_flashcards.pdf`
**Student Page**
- 16 cards: animal image placeholder, habitat icon, one adaptation sentence stem.
- Example stem: "The giraffe survives in the savanna because ____."

**Teacher Instructions**
- Use for Lessons 4.1-4.3 sorts.
- Add movement cue for each animal in K-2.

**Answer Key**
- Sample pairings: lion-savanna, gorilla-rainforest, camel-desert, hippopotamus-wetland/river.

### 5. `mini_book_template_folktale.pdf`
**Student Page**
- 8-page mini-book structure:
  1. Title
  2. Characters
  3. Setting
  4. Problem
  5. Events
  6. Solution
  7. Lesson/Moral
  8. My Illustration + Author Note

**Teacher Instructions**
- K-2 may dictate text.
- 3-5 should include sequence words and complete sentences.

**Answer Key**
- N/A (creative product). Check for all required story elements.

### 6. `land_water_climate_sketch_sheet.pdf`
**Student Page**
- Three-column template: Landform | Water Feature | Climate.
- Draw + label one example per column.
- Prompt: "How does this place affect living things?"

**Teacher Instructions**
- Use as spiral review after Unit 2.

**Answer Key**
- Accept accurate combinations and explanations (e.g., desert = little rainfall).

### 7. `presentation_rubric_k2.pdf`
**Student Page**
- 4 criteria, 3-point scale (Emerging/Developing/Strong):
  - I shared facts.
  - I used my picture or model.
  - I spoke so others could hear.
  - I was respectful listener/speaker.

**Teacher Instructions**
- Use visuals and smiley anchors.

**Answer Key**
- N/A; rubric scoring guide included with behavior descriptors.

### 8. `presentation_rubric_35.pdf`
**Student Page**
- 5 criteria, 4-point scale:
  - Accuracy of content
  - Use of evidence/vocabulary
  - Organization and clarity
  - Visual support quality
  - Speaking skills and audience engagement

**Teacher Instructions**
- Pre-teach rubric language and exemplars.

**Answer Key**
- N/A; rubric descriptors define proficiency by level.

### 9. `celebration_project_planner.pdf`
**Student Page**
- Sections: Topic, 3 Key Facts, 1 Map Feature, 1 Vocabulary Word, Visual Plan, Materials Checklist, Rehearsal Script, Reflection.

**Teacher Instructions**
- Conference with each student at planning and rehearsal checkpoints.

**Answer Key**
- N/A; must include accurate facts and at least one mapped feature.

---

## 3) Assessment Bank

### A) 15 Multiple Choice Questions (Auto-graded)

```json
[
  {"question_type":"multiple_choice","question":"Africa is a...","choices":["country","continent","city","ocean"],"correct_answer":"continent","explanation":"Africa is one of Earth’s seven continents."},
  {"question_type":"multiple_choice","question":"How many countries are in Africa?","choices":["12","54","80","5"],"correct_answer":"54","explanation":"Africa has 54 recognized countries."},
  {"question_type":"multiple_choice","question":"Which is a major desert in Africa?","choices":["Gobi","Sahara","Atacama","Mojave"],"correct_answer":"Sahara","explanation":"The Sahara Desert is in North Africa."},
  {"question_type":"multiple_choice","question":"The Nile is a...","choices":["mountain","river","forest","city"],"correct_answer":"river","explanation":"The Nile River is one of the longest rivers in the world."},
  {"question_type":"multiple_choice","question":"Which habitat is best for a camel?","choices":["desert","rainforest","wetland","tundra"],"correct_answer":"desert","explanation":"Camels are adapted to dry desert environments."},
  {"question_type":"multiple_choice","question":"A map key helps us...","choices":["eat lunch","understand symbols","write a story","measure music"],"correct_answer":"understand symbols","explanation":"Map keys/legends explain map symbols and colors."},
  {"question_type":"multiple_choice","question":"Which is an ecosystem in Africa?","choices":["savanna","parking lot","subway","playground"],"correct_answer":"savanna","explanation":"Savanna is a major grassland ecosystem."},
  {"question_type":"multiple_choice","question":"Folktales often teach a...","choices":["recipe","lesson","weather report","math formula"],"correct_answer":"lesson","explanation":"Folktales often include a moral or life lesson."},
  {"question_type":"multiple_choice","question":"Which is respectful to say?","choices":["Africa is one culture","Africa has many cultures and languages","Everyone lives the same way","Only one language is spoken"],"correct_answer":"Africa has many cultures and languages","explanation":"Africa is diverse across countries and communities."},
  {"question_type":"multiple_choice","question":"Which body of water borders Africa to the east?","choices":["Indian Ocean","Pacific Ocean","Arctic Ocean","Black Sea"],"correct_answer":"Indian Ocean","explanation":"The Indian Ocean lies east of Africa."},
  {"question_type":"multiple_choice","question":"Which feature is in North Africa?","choices":["Sahara Desert","Amazon River","Rocky Mountains","Great Barrier Reef"],"correct_answer":"Sahara Desert","explanation":"The Sahara extends across parts of North Africa."},
  {"question_type":"multiple_choice","question":"A giraffe is commonly found in the...","choices":["savanna","polar ice","coral reef","tundra"],"correct_answer":"savanna","explanation":"Giraffes are adapted to savanna habitats."},
  {"question_type":"multiple_choice","question":"Which tool helps locate places on Earth?","choices":["globe","drum","paintbrush","thermometer"],"correct_answer":"globe","explanation":"A globe shows Earth and continents."},
  {"question_type":"multiple_choice","question":"Climate means...","choices":["what you wear","long-term weather pattern","a country name","a type of song"],"correct_answer":"long-term weather pattern","explanation":"Climate describes typical weather over time."},
  {"question_type":"multiple_choice","question":"Why do we cite facts in presentations?","choices":["to be accurate","to be louder","to finish faster","to avoid pictures"],"correct_answer":"to be accurate","explanation":"Using facts helps presentations stay truthful and clear."}
]
```

### B) 10 Short-Answer Prompts

```json
[
  {"question_type":"short_answer","question":"Write one fact about Africa as a continent.","choices":[],"correct_answer":"Answers vary (must be accurate)","explanation":"Accept facts such as 54 countries or second-largest continent."},
  {"question_type":"short_answer","question":"Why is it important to use a map key?","choices":[],"correct_answer":"It explains symbols/colors","explanation":"Students should mention understanding map symbols."},
  {"question_type":"short_answer","question":"Name one river in Africa and one thing rivers help people do.","choices":[],"correct_answer":"Example: Nile; water/transport/farming","explanation":"Any correct river-use pair earns credit."},
  {"question_type":"short_answer","question":"Describe one way climate can affect homes or clothing.","choices":[],"correct_answer":"Answers vary","explanation":"Look for logical climate-to-lifestyle connection."},
  {"question_type":"short_answer","question":"What lesson did the folktale teach?","choices":[],"correct_answer":"Answers vary","explanation":"Must state a coherent theme or moral."},
  {"question_type":"short_answer","question":"How are savanna and rainforest different?","choices":[],"correct_answer":"Grassland vs dense forest/wet climate","explanation":"Need one accurate contrast."},
  {"question_type":"short_answer","question":"Name two African languages from class.","choices":[],"correct_answer":"Any two taught examples","explanation":"Examples: Swahili, Arabic, Amharic, Hausa, Yoruba, Zulu."},
  {"question_type":"short_answer","question":"Explain one adaptation of an African animal.","choices":[],"correct_answer":"Answers vary","explanation":"Must include trait + survival purpose."},
  {"question_type":"short_answer","question":"What makes a source reliable for learning geography?","choices":[],"correct_answer":"Accurate, trusted, verifiable source","explanation":"Look for mention of trusted maps/books/experts."},
  {"question_type":"short_answer","question":"What is one question you still have about an African country?","choices":[],"correct_answer":"Student-generated question","explanation":"Assesses curiosity and inquiry."}
]
```

### C) 5 Map-Labeling Prompts

```json
[
  {"question_type":"map_labeling","question":"Label Africa on a blank world map.","choices":[],"correct_answer":"Africa correctly identified","explanation":"Student marks continent shape in eastern hemisphere."},
  {"question_type":"map_labeling","question":"Label the Sahara Desert.","choices":[],"correct_answer":"North Africa region","explanation":"Should appear across northern band of continent."},
  {"question_type":"map_labeling","question":"Label the Nile River.","choices":[],"correct_answer":"Northeast Africa river system","explanation":"Flows generally north toward Mediterranean."},
  {"question_type":"map_labeling","question":"Label the Atlantic and Indian Oceans.","choices":[],"correct_answer":"Atlantic west; Indian east","explanation":"Correct relative placement required."},
  {"question_type":"map_labeling","question":"Draw and label the Equator crossing Africa.","choices":[],"correct_answer":"Horizontal equator line through central Africa","explanation":"Line should cross middle latitudes of continent."}
]
```

### D) 5 Performance Tasks

```json
[
  {"question_type":"performance_task","question":"Create a labeled physical map poster with at least 5 features.","choices":[],"correct_answer":"Rubric-scored","explanation":"Evaluate accuracy, labels, and neatness."},
  {"question_type":"performance_task","question":"Record a 60-120 second habitat explanation using one animal example.","choices":[],"correct_answer":"Rubric-scored","explanation":"Assess vocabulary use and adaptation explanation."},
  {"question_type":"performance_task","question":"Retell a folktale with beginning, middle, end, and lesson.","choices":[],"correct_answer":"Rubric-scored","explanation":"Check sequencing and theme statement."},
  {"question_type":"performance_task","question":"Compare two communities using photo evidence and respectful language.","choices":[],"correct_answer":"Rubric-scored","explanation":"Assess compare/contrast and cultural responsiveness."},
  {"question_type":"performance_task","question":"Present final celebration project with 3 facts and 1 map element.","choices":[],"correct_answer":"Rubric-scored","explanation":"Final synthesis task with audience Q&A."}
]
```

### E) Cumulative Unit Test

```json
{
  "question_type": "cumulative_unit_test",
  "question": "Introduction to Africa End-of-Course Check",
  "choices": [],
  "correct_answer": "Mixed-format scoring",
  "explanation": "Test includes 10 MCQ, 3 short answer, 2 map-labeling tasks, and 1 mini performance prompt.",
  "sections": {
    "mcq_count": 10,
    "short_answer_count": 3,
    "map_labeling_count": 2,
    "performance_prompt": "Explain how one ecosystem and one climate are connected.",
    "answer_key_summary": "Use keys above for objective items; constructed/performance scored with grade-band rubrics."
  }
}
```

---

## 4) Teacher Guide + Student View Content

### Teacher Guide (implementation snapshot)
- **Pacing:** 4-6 weeks, 3-4 sessions per week, 35-50 minutes each.
- **Differentiation:**
  - K-2: visual supports, sentence stems, oral response options, shorter writing blocks.
  - 3-5: evidence statements, compare/contrast paragraphs, map extension tasks.
- **UDL supports:** chunked directions, audio read-aloud options, flexible output (draw/speak/write), bilingual glossary support.
- **Family connections:** optional weekly take-home "Ask Me About" cards and showcase invitation.
- **Data cycle:** weekly map check + vocabulary quick check + teacher anecdotal notes.

### Student View Content (sample copy)
- **Welcome message:** "In this course, you will be a geography explorer, storyteller, and presenter."
- **Unit launcher cards:** each unit starts with one essential question and one image.
- **Daily checklist:** warm-up, mini-lesson, practice, share, reflect.
- **Progress language:** "You are building your Africa Expert Badge by completing lessons and projects."

---

## 5) HTML Snippets for Frontend Demo (Phase 7)

### A) Fully Rendered Lesson Page

```html
<section class="lesson-page">
  <header>
    <h1>Unit 2 · Lesson 2.1: Big Features of Africa</h1>
    <p class="standards">NCSS Geography · CCSS RI.3.2</p>
    <p class="essential">Essential Question: How do landforms and water features shape life?</p>
  </header>

  <article class="block hook">
    <h2>Hook</h2>
    <p>Mystery Postcard: Is this from a desert, river, or mountain area? Share your guess with a partner.</p>
  </article>

  <article class="block instruction">
    <h2>Direct Instruction</h2>
    <p>Today we will locate the Sahara Desert, Nile River, Congo River, Zambezi River, Atlas Mountains, and Mt. Kilimanjaro.</p>
    <ul>
      <li><strong>K-2:</strong> Point and repeat key feature names with picture icons.</li>
      <li><strong>3-5:</strong> Add one note about each feature in your geography journal.</li>
    </ul>
  </article>

  <article class="block practice">
    <h2>Guided Practice</h2>
    <p>Drag each feature label to the map. Check your answers with the class map.</p>
  </article>

  <article class="block independent">
    <h2>Independent Practice</h2>
    <p><strong>K-2:</strong> Sticker map labeling. <strong>3-5:</strong> Write 3-4 sentences: "One important feature is..."</p>
  </article>

  <footer>
    <button>Submit Exit Ticket</button>
    <button>Open Printable: africa_map_labeled.pdf</button>
  </footer>
</section>
```

### B) Interactive Quiz Page

```html
<section class="quiz-page">
  <h1>Quick Check: Climate and Ecosystems</h1>
  <form>
    <div class="question">
      <p>1) Africa is a:</p>
      <label><input type="radio" name="q1"> Country</label>
      <label><input type="radio" name="q1"> Continent</label>
      <label><input type="radio" name="q1"> Ocean</label>
    </div>
    <div class="question">
      <p>2) Which habitat matches a camel?</p>
      <select>
        <option>Choose one</option>
        <option>Desert</option>
        <option>Rainforest</option>
        <option>Wetland</option>
      </select>
    </div>
    <button type="submit">Check My Answers</button>
  </form>
</section>
```

### C) Project Submission Page

```html
<section class="project-submit">
  <h1>Celebration Project Submission</h1>
  <label>Project Title <input type="text" /></label>
  <label>Project Type
    <select>
      <option>Poster</option>
      <option>Diorama</option>
      <option>Slide Presentation</option>
      <option>Mini-Book</option>
    </select>
  </label>
  <label>Upload File <input type="file" /></label>
  <label>Reflection
    <textarea placeholder="One thing I learned, one question I still have..."></textarea>
  </label>
  <button>Submit Project</button>
</section>
```

### D) Progress Tracker View

```html
<section class="progress-tracker">
  <h1>My Africa Course Progress</h1>
  <p>Student: Amina R. · Badge Progress: 92%</p>
  <ul>
    <li>Unit 1: ✅ Complete</li>
    <li>Unit 2: ✅ Complete</li>
    <li>Unit 3: ✅ Complete</li>
    <li>Unit 4: ✅ Complete</li>
    <li>Unit 5: ✅ Complete</li>
    <li>Unit 6: 🟡 In Progress (Showcase next week)</li>
  </ul>
  <p>Teacher Note: Great map evidence use. Keep practicing presentation pacing.</p>
</section>
```

---

## 6) Admin Demo Selling Points (Phase 8)

### 5 Organization-Level Benefits
1. Ready-to-deploy K-5 global studies course with standards-aligned scope and sequence.
2. Structured data model (Course > Unit > Lesson > Activity) supports clean LMS ingestion.
3. Built-in assessments, rubrics, and progress signals improve teacher efficiency.
4. Cross-curricular design connects social studies, geography, literacy, SEL, and speaking.
5. Showcase-ready student outputs provide visible evidence for district and board presentations.

### 5 Equity & Cultural Literacy Benefits
1. Frames Africa as a diverse continent, not a single story.
2. Uses respectful, strengths-based language in all student-facing content.
3. Includes multiple regions, ecosystems, and community perspectives.
4. Encourages curiosity, listening, and bias-aware classroom dialogue.
5. Supports culturally responsive instruction with vetted media and teacher guidance.

### 5 Measurable Academic Outcomes
1. Increased map literacy measured via pre/post labeling checks.
2. Growth in geography vocabulary usage across speaking and writing tasks.
3. Improved informational text comprehension through evidence-based responses.
4. Higher student confidence in oral presentation using grade-band rubrics.
5. Demonstrated synthesis of concepts in culminating projects and cumulative assessments.

### 3 Parent Engagement Extensions
1. Family geography night with student project gallery walk.
2. Take-home mini-book reading and discussion prompts in multiple languages.
3. Monthly "Global Learning Snapshot" showing student growth and upcoming inquiry topics.

