// Database Seed Script - IELTS Master Platform
// Run: node seed.js
// This script generates 1000+ test questions for all IELTS sections

require('dotenv').config();
const mongoose = require('mongoose');
const { v4: uuidv4 } = require('uuid');

// MongoDB connection
const MONGODB_URI = process.env.MONGODB_URI || 'mongodb://localhost:27017/ielts-platform';

// ============================================
// MongoDB Schemas
// ============================================

const readingTestSchema = new mongoose.Schema({
  id: { type: String, default: uuidv4 },
  title: String,
  difficulty: { type: String, enum: ['easy', 'medium', 'hard'] },
  topic: String,
  passage: String,
  wordCount: Number,
  timeLimit: { type: Number, default: 20 },
  questions: [{
    id: String,
    type: { type: String, enum: ['multiple-choice', 'true-false-ng', 'fill-blank', 'matching', 'short-answer'] },
    question: String,
    options: [String],
    correctAnswer: mongoose.Schema.Types.Mixed,
    explanation: String
  }],
  createdAt: { type: Date, default: Date.now }
});

const listeningTestSchema = new mongoose.Schema({
  id: { type: String, default: uuidv4 },
  title: String,
  difficulty: { type: String, enum: ['easy', 'medium', 'hard'] },
  section: { type: Number, min: 1, max: 4 },
  audioUrl: String,
  transcript: String,
  duration: Number,
  questions: [{
    id: String,
    type: { type: String, enum: ['multiple-choice', 'fill-blank', 'matching', 'map-labeling', 'note-completion'] },
    question: String,
    options: [String],
    correctAnswer: mongoose.Schema.Types.Mixed,
    timestamp: String
  }],
  createdAt: { type: Date, default: Date.now }
});

const writingTaskSchema = new mongoose.Schema({
  id: { type: String, default: uuidv4 },
  title: String,
  taskType: { type: String, enum: ['task1', 'task2'] },
  category: String,
  prompt: String,
  imageUrl: String,
  wordLimit: { min: Number, max: Number },
  timeLimit: Number,
  sampleAnswer: String,
  tips: [String],
  createdAt: { type: Date, default: Date.now }
});

const speakingTestSchema = new mongoose.Schema({
  id: { type: String, default: uuidv4 },
  title: String,
  part: { type: Number, min: 1, max: 3 },
  topic: String,
  questions: [{
    id: String,
    question: String,
    followUp: [String],
    tips: String,
    sampleAnswer: String,
    timeLimit: Number
  }],
  createdAt: { type: Date, default: Date.now }
});

const ReadingTest = mongoose.model('ReadingTest', readingTestSchema);
const ListeningTest = mongoose.model('ListeningTest', listeningTestSchema);
const WritingTask = mongoose.model('WritingTask', writingTaskSchema);
const SpeakingTest = mongoose.model('SpeakingTest', speakingTestSchema);

// ============================================
// Test Data Generators
// ============================================

// Reading Topics and Passages
const readingTopics = [
  { topic: 'Technology', themes: ['AI Revolution', 'Space Exploration', 'Renewable Energy', 'Cybersecurity', 'Biotechnology', 'Quantum Computing', 'Internet of Things', 'Virtual Reality'] },
  { topic: 'Environment', themes: ['Climate Change', 'Ocean Conservation', 'Wildlife Protection', 'Sustainable Agriculture', 'Deforestation', 'Pollution Control', 'Green Architecture', 'Renewable Resources'] },
  { topic: 'History', themes: ['Ancient Civilizations', 'Industrial Revolution', 'World Wars', 'Scientific Discoveries', 'Cultural Movements', 'Archaeological Finds', 'Colonial Era', 'Medieval Times'] },
  { topic: 'Science', themes: ['Genetics', 'Astronomy', 'Neuroscience', 'Chemistry Advances', 'Physics Theories', 'Marine Biology', 'Microbiology', 'Earth Sciences'] },
  { topic: 'Society', themes: ['Urbanization', 'Education Systems', 'Healthcare Evolution', 'Social Media Impact', 'Migration Patterns', 'Economic Trends', 'Cultural Diversity', 'Gender Equality'] },
  { topic: 'Psychology', themes: ['Memory Studies', 'Behavioral Patterns', 'Cognitive Development', 'Emotional Intelligence', 'Social Psychology', 'Learning Theories', 'Mental Health', 'Decision Making'] },
  { topic: 'Business', themes: ['Global Trade', 'Entrepreneurship', 'Corporate Ethics', 'Market Dynamics', 'Innovation Management', 'Leadership Styles', 'Economic Policy', 'Digital Marketing'] },
  { topic: 'Arts', themes: ['Modern Art Movements', 'Music Evolution', 'Literary Analysis', 'Film Industry', 'Architecture Trends', 'Cultural Heritage', 'Performing Arts', 'Digital Arts'] }
];

function generateReadingPassage(topic, theme, difficulty) {
  const wordCounts = { easy: 600, medium: 800, hard: 1000 };
  const wordCount = wordCounts[difficulty];
  
  const passages = {
    'AI Revolution': `The advent of artificial intelligence represents one of the most significant technological transformations in human history. From its theoretical foundations in the mid-20th century to today's sophisticated machine learning systems, AI has evolved from a speculative concept into a technology that permeates virtually every aspect of modern life.

The journey began in 1956 at Dartmouth College, where researchers first coined the term "artificial intelligence." Early pioneers envisioned machines that could reason, learn, and solve problems much like humans. However, progress was slower than anticipated, leading to periods of reduced funding known as "AI winters."

The contemporary AI renaissance began around 2012, when deep learning techniques achieved breakthrough results in image recognition. This success was enabled by three converging factors: exponentially more powerful computing hardware, vast amounts of digital data for training, and algorithmic innovations in neural network architectures.

Today, AI applications span an remarkable range of domains. In healthcare, machine learning algorithms analyze medical images with accuracy rivaling expert radiologists. Natural language processing enables virtual assistants to understand and respond to spoken queries. Autonomous vehicles use computer vision and decision-making algorithms to navigate complex environments.

The economic implications are profound. Management consulting firm McKinsey estimates that AI could contribute up to $15.7 trillion to the global economy by 2030. Industries from manufacturing to financial services are being transformed by automation and intelligent decision support systems.

However, this transformation raises significant concerns. Questions about job displacement, algorithmic bias, privacy, and the long-term implications of increasingly autonomous systems demand serious consideration. Researchers and policymakers are grappling with how to ensure AI development benefits humanity while mitigating potential risks.

The field continues to advance rapidly. Recent developments in large language models have demonstrated remarkable capabilities in text generation, reasoning, and even creative tasks. As AI systems become more capable, the need for thoughtful governance and ethical frameworks becomes ever more pressing.`,

    'Climate Change': `Climate change stands as the defining environmental challenge of our era, with implications that extend far beyond ecological concerns to encompass economic, social, and geopolitical dimensions. The scientific evidence documenting global warming has grown increasingly robust over decades of research.

The fundamental mechanism is well understood: human activities, primarily the burning of fossil fuels, have increased atmospheric concentrations of carbon dioxide and other greenhouse gases. These gases trap heat that would otherwise escape to space, gradually warming the planet. Since the pre-industrial era, global average temperatures have risen approximately 1.1 degrees Celsius.

The consequences are already manifesting across the globe. Glaciers and ice sheets are melting, contributing to rising sea levels. Weather patterns are shifting, with many regions experiencing more frequent and intense heat waves, droughts, and extreme precipitation events. Ecosystems are under stress as species struggle to adapt to rapidly changing conditions.

Perhaps most concerning are potential tipping points—thresholds beyond which changes become self-reinforcing and potentially irreversible. The melting of Arctic permafrost, for example, could release vast quantities of stored methane, accelerating warming further. Scientists warn that some of these tipping points may be closer than previously thought.

International efforts to address climate change have intensified since the Paris Agreement of 2015, which established a framework for countries to set and achieve emissions reduction targets. However, current commitments remain insufficient to limit warming to the agreement's aspirational goal of 1.5 degrees Celsius.

The transition to a low-carbon economy presents both challenges and opportunities. Renewable energy costs have fallen dramatically, making solar and wind increasingly competitive with fossil fuels. Electric vehicles are gaining market share. Yet transforming the global energy system requires unprecedented levels of investment and coordination.

Adaptation measures are also essential. Coastal communities must prepare for rising seas. Agricultural practices need to evolve for changing growing conditions. Infrastructure must be built or retrofitted to withstand more extreme weather.`,

    'Ancient Civilizations': `The study of ancient civilizations provides invaluable insights into human development, revealing patterns of innovation, social organization, and cultural achievement that continue to influence contemporary society. Among the most significant were the civilizations that emerged in Mesopotamia, Egypt, the Indus Valley, and China.

Mesopotamia, often called the "cradle of civilization," arose in the fertile lands between the Tigris and Euphrates rivers in present-day Iraq. Here, around 3500 BCE, the Sumerians developed one of the world's first writing systems—cuneiform—and established sophisticated urban centers. They made fundamental advances in mathematics, astronomy, and law, including the Code of Hammurabi.

Egyptian civilization flourished along the Nile River, sustained by its predictable annual floods that deposited nutrient-rich soil. The Egyptians developed hieroglyphic writing, constructed monumental architecture including the pyramids, and created elaborate systems of religion and governance. Their civilization lasted over three thousand years, leaving an enduring cultural legacy.

The Indus Valley civilization, centered in present-day Pakistan and northwest India, remains somewhat mysterious due to the undeciphered nature of its script. Archaeological evidence reveals remarkably planned cities with advanced drainage systems, standardized weights and measures, and extensive trade networks reaching as far as Mesopotamia.

Chinese civilization emerged along the Yellow River, developing distinctive traditions that would shape East Asian culture for millennia. Early Chinese achievements included bronze metallurgy, silk production, and the development of a writing system that, unlike those of other ancient civilizations, continues in use today.

These civilizations shared certain characteristics despite their geographical separation. Each developed in river valleys whose waters enabled agricultural surplus. Each created systems of writing that allowed for record-keeping and the transmission of knowledge. Each built complex social hierarchies and religious institutions.

Yet each also followed a unique trajectory shaped by local conditions and historical contingencies. Understanding both the commonalities and differences illuminates fundamental aspects of human social development.`
  };

  return passages[theme] || generateGenericPassage(topic, theme, difficulty);
}

function generateGenericPassage(topic, theme, difficulty) {
  return `${theme} in the Context of ${topic}

The study of ${theme.toLowerCase()} represents a fascinating area of inquiry within the broader field of ${topic.toLowerCase()}. Researchers have dedicated significant effort to understanding the various factors that influence this phenomenon.

Historical development in this area began in the early twentieth century when scholars first recognized the importance of systematic investigation. Initial studies were limited by available methodologies, but subsequent technological advances enabled more sophisticated approaches.

Contemporary research has revealed several key findings. First, the relationship between various factors appears more complex than originally theorized. Second, contextual variables play a significant role in determining outcomes. Third, long-term effects may differ substantially from short-term observations.

The practical implications of this research extend to multiple domains. Policymakers have incorporated these findings into decision-making processes. Educators have revised curricula to reflect current understanding. Industry practitioners have developed new approaches based on research insights.

Methodological debates continue within the field. Some researchers advocate for quantitative approaches that enable statistical generalization. Others argue that qualitative methods provide richer understanding of underlying mechanisms. Increasingly, mixed-method designs attempt to combine the strengths of both traditions.

Future directions for research are promising. Emerging technologies offer new tools for investigation. Interdisciplinary collaboration is generating novel theoretical frameworks. Global connectivity enables comparative studies across diverse contexts.

The significance of understanding ${theme.toLowerCase()} cannot be overstated. As societies face unprecedented challenges, evidence-based knowledge becomes ever more essential. Continued investment in research will yield benefits for generations to come.`;
}

function generateReadingQuestions(difficulty) {
  const questionCounts = { easy: 10, medium: 13, hard: 15 };
  const count = questionCounts[difficulty];
  const questions = [];

  const questionTypes = ['multiple-choice', 'true-false-ng', 'fill-blank', 'matching', 'short-answer'];

  for (let i = 0; i < count; i++) {
    const type = questionTypes[i % questionTypes.length];
    questions.push({
      id: uuidv4(),
      type,
      question: generateQuestionText(type, i + 1),
      options: type === 'multiple-choice' ? ['Option A', 'Option B', 'Option C', 'Option D'] : 
               type === 'true-false-ng' ? ['TRUE', 'FALSE', 'NOT GIVEN'] : [],
      correctAnswer: type === 'multiple-choice' ? 'Option A' :
                    type === 'true-false-ng' ? 'TRUE' :
                    type === 'fill-blank' ? 'answer' : 'sample answer',
      explanation: `Explanation for question ${i + 1}: This answer can be found in paragraph ${(i % 5) + 1} of the passage.`
    });
  }

  return questions;
}

function generateQuestionText(type, num) {
  const templates = {
    'multiple-choice': [
      'According to the passage, which of the following is true?',
      'The author suggests that:',
      'What is the main purpose of the third paragraph?',
      'Which statement best summarizes the passage?',
      'The word "it" in line X refers to:'
    ],
    'true-false-ng': [
      'The development began in the early twentieth century.',
      'Research methods have remained unchanged since initial studies.',
      'Practical applications have been implemented in education.',
      'All researchers agree on the best methodological approach.',
      'Future research directions have been clearly defined.'
    ],
    'fill-blank': [
      'Complete the sentence: The main factor influencing the outcome was _____.',
      'Fill in the blank: Researchers discovered that _____ played a crucial role.',
      'Complete: The study concluded that _____ was essential.',
      'Fill in: According to the passage, _____ contributed to the development.',
      'Complete the summary: The most significant finding was _____.'
    ],
    'matching': [
      'Match the following terms with their definitions.',
      'Match each researcher with their contribution.',
      'Match the time periods with the developments.',
      'Match the concepts with their descriptions.',
      'Match the findings with the appropriate studies.'
    ],
    'short-answer': [
      'What was the primary finding of the research?',
      'Name TWO factors that influenced the outcome.',
      'What year did the significant development occur?',
      'Who conducted the initial study?',
      'What method was used in the research?'
    ]
  };

  return templates[type][num % templates[type].length];
}

// Listening Data Generator
function generateListeningTests(count) {
  const tests = [];
  const sections = [
    { section: 1, description: 'Social conversation between two people' },
    { section: 2, description: 'Monologue on social topic' },
    { section: 3, description: 'Academic discussion' },
    { section: 4, description: 'Academic lecture' }
  ];

  const topics = [
    'University enrollment', 'Library tour', 'Housing arrangements', 'Job interview',
    'Museum visit', 'Travel booking', 'Health clinic', 'Sports facility',
    'Environmental lecture', 'Historical overview', 'Scientific discovery', 'Business presentation',
    'Art exhibition', 'Cultural event', 'Technology seminar', 'Research findings'
  ];

  for (let i = 0; i < count; i++) {
    const sectionInfo = sections[i % 4];
    const topic = topics[i % topics.length];
    const difficulty = ['easy', 'medium', 'hard'][Math.floor(i / (count / 3)) % 3];

    tests.push({
      id: uuidv4(),
      title: `Listening Section ${sectionInfo.section}: ${topic}`,
      difficulty,
      section: sectionInfo.section,
      audioUrl: `/audio/listening_${i + 1}.mp3`,
      transcript: generateListeningTranscript(sectionInfo.section, topic),
      duration: 5 + (sectionInfo.section * 2),
      questions: generateListeningQuestions(sectionInfo.section)
    });
  }

  return tests;
}

function generateListeningTranscript(section, topic) {
  if (section === 1) {
    return `
A: Good morning, how can I help you today?
B: Hi, I'm interested in learning more about ${topic.toLowerCase()}.
A: Of course! Let me explain the main points...
B: That sounds helpful. Could you tell me about the requirements?
A: Yes, you'll need to complete a registration form first. Then we'll schedule an appointment.
B: And what about the fees?
A: The initial consultation is free, but subsequent services have a standard fee structure.
B: Thank you, that's very clear. When can I get started?
A: We have availability this week. Would Thursday afternoon work for you?
B: That would be perfect. I'll bring all the necessary documents.
    `.trim();
  } else if (section === 2) {
    return `
Good afternoon everyone. Today I'd like to talk to you about ${topic.toLowerCase()}.

First, let's consider the background. This topic has become increasingly important in recent years due to several factors. 

The main points I want to cover are: first, the historical development; second, current practices; and third, future directions.

Starting with the historical development, we can trace the origins back to the early twentieth century. Initial approaches were quite different from what we see today.

Moving on to current practices, there have been significant changes in recent decades. Modern methods incorporate new technologies and research findings.

Finally, looking at future directions, experts predict continued evolution in this field. Several emerging trends deserve our attention.

In conclusion, understanding ${topic.toLowerCase()} helps us appreciate both where we've been and where we're heading. Thank you for your attention.
    `.trim();
  } else {
    return `
Professor: Good afternoon. Today's seminar will focus on ${topic.toLowerCase()}.
Student 1: Could you explain the theoretical framework?
Professor: Certainly. The theoretical basis draws from multiple disciplines...
Student 2: How does this relate to practical applications?
Professor: That's an excellent question. The connection between theory and practice is crucial.
Student 1: What research methods are most commonly used?
Professor: Researchers typically employ both quantitative and qualitative approaches.
Student 2: Are there any controversies in this field?
Professor: Yes, there are ongoing debates about methodology and interpretation.
Professor: For your assignment, I'd like you to analyze a case study applying these concepts.
    `.trim();
  }
}

function generateListeningQuestions(section) {
  const questionCount = section <= 2 ? 10 : 10;
  const questions = [];
  const types = ['multiple-choice', 'fill-blank', 'matching', 'note-completion'];

  for (let i = 0; i < questionCount; i++) {
    questions.push({
      id: uuidv4(),
      type: types[i % types.length],
      question: `Question ${i + 1}: ${generateListeningQuestionText(types[i % types.length])}`,
      options: types[i % types.length] === 'multiple-choice' ? ['A', 'B', 'C'] : [],
      correctAnswer: 'A',
      timestamp: `${Math.floor(i / 2)}:${(i % 2) * 30}0`
    });
  }

  return questions;
}

function generateListeningQuestionText(type) {
  const templates = {
    'multiple-choice': 'What does the speaker say about the main topic?',
    'fill-blank': 'Complete the note: The appointment is scheduled for _____.',
    'matching': 'Match the service with its description.',
    'note-completion': 'Complete the notes below using NO MORE THAN TWO WORDS.'
  };
  return templates[type];
}

// Writing Tasks Generator
function generateWritingTasks(count) {
  const tasks = [];
  
  // Task 1 Types (Academic)
  const task1Types = [
    { category: 'Line Graph', prompt: 'The graph below shows changes in the amount of waste produced in three countries between 1990 and 2020.' },
    { category: 'Bar Chart', prompt: 'The bar chart compares the number of students enrolled in different subjects at a university in 2010 and 2020.' },
    { category: 'Pie Chart', prompt: 'The pie charts below show the percentage of household expenditure in a country in 2000 and 2020.' },
    { category: 'Table', prompt: 'The table shows the proportion of people using different modes of transport in four cities.' },
    { category: 'Process Diagram', prompt: 'The diagram shows the process of manufacturing chocolate from cocoa beans.' },
    { category: 'Map', prompt: 'The maps show changes to a town between 1960 and present day.' },
    { category: 'Multiple Charts', prompt: 'The charts give information about world coffee production and consumption.' }
  ];

  // Task 2 Topics
  const task2Topics = [
    { category: 'Education', prompt: 'Some people believe that children should be taught to compete, while others think they should be taught to cooperate. Discuss both views and give your opinion.' },
    { category: 'Technology', prompt: 'The rise of artificial intelligence may lead to significant job losses across many industries. To what extent do you agree or disagree?' },
    { category: 'Environment', prompt: 'Environmental problems are too big for individual countries to solve. International cooperation is necessary to address these issues. Do you agree or disagree?' },
    { category: 'Society', prompt: 'In many countries, the proportion of older people is steadily increasing. What problems will this cause, and what solutions can you suggest?' },
    { category: 'Health', prompt: 'Some people think that public health is the responsibility of the government, while others believe individuals should take care of their own health. Discuss both views.' },
    { category: 'Work', prompt: 'Many people work from home using modern technology today. Some people think this has more advantages, while others disagree. Discuss both views and give your opinion.' },
    { category: 'Crime', prompt: 'Some people believe that the best way to reduce crime is to give longer prison sentences. Others believe there are better ways to reduce crime. Discuss both views and give your opinion.' },
    { category: 'Media', prompt: 'News stories on television and in newspapers are very often accompanied by pictures. Some people say that these pictures are more effective than words. To what extent do you agree or disagree?' }
  ];

  // Generate Task 1s
  const task1Count = Math.floor(count * 0.4);
  for (let i = 0; i < task1Count; i++) {
    const taskType = task1Types[i % task1Types.length];
    tasks.push({
      id: uuidv4(),
      title: `Task 1: ${taskType.category}`,
      taskType: 'task1',
      category: taskType.category,
      prompt: taskType.prompt + '\n\nSummarise the information by selecting and reporting the main features, and make comparisons where relevant.\n\nWrite at least 150 words.',
      wordLimit: { min: 150, max: 200 },
      timeLimit: 20,
      tips: [
        'Spend 2-3 minutes analyzing the data before writing',
        'Write an overview paragraph summarizing the main trends',
        'Include specific data to support your points',
        'Use a variety of language to describe trends and comparisons'
      ],
      sampleAnswer: generateTask1SampleAnswer(taskType.category)
    });
  }

  // Generate Task 2s
  for (let i = task1Count; i < count; i++) {
    const taskType = task2Topics[(i - task1Count) % task2Topics.length];
    tasks.push({
      id: uuidv4(),
      title: `Task 2: ${taskType.category}`,
      taskType: 'task2',
      category: taskType.category,
      prompt: taskType.prompt + '\n\nGive reasons for your answer and include any relevant examples from your own knowledge or experience.\n\nWrite at least 250 words.',
      wordLimit: { min: 250, max: 300 },
      timeLimit: 40,
      tips: [
        'Plan your essay structure before writing',
        'Include a clear introduction with your thesis statement',
        'Develop each paragraph with a topic sentence and supporting details',
        'Use linking words to connect your ideas',
        'Write a conclusion that summarizes your main points'
      ],
      sampleAnswer: generateTask2SampleAnswer(taskType.category)
    });
  }

  return tasks;
}

function generateTask1SampleAnswer(category) {
  return `The ${category.toLowerCase()} provides information about... 

Overall, it is evident that... The most significant trend is...

Looking at the details, we can see that initially... Subsequently, there was a notable change in...

In comparison, the data shows that... while... This represents a considerable difference of...

To conclude, the data reveals clear patterns in... with the most marked changes occurring in...`;
}

function generateTask2SampleAnswer(category) {
  return `The topic of ${category.toLowerCase()} has generated considerable debate in recent years. This essay will discuss both perspectives before presenting my own view.

On one hand, proponents argue that... This view is supported by evidence showing... Furthermore, many experts suggest that...

On the other hand, critics contend that... Research indicates that... Additionally, there are concerns about...

In my opinion, while both arguments have merit, I believe that... This is because... Moreover, considering the long-term implications...

In conclusion, although there are valid points on both sides, I maintain that... Governments and individuals should work together to address this issue by...`;
}

// Speaking Tests Generator
function generateSpeakingTests(count) {
  const tests = [];

  const part1Topics = [
    'Work', 'Studies', 'Hometown', 'Home', 'Family', 'Hobbies', 'Music', 'Reading',
    'Sports', 'Travel', 'Food', 'Weather', 'Technology', 'Friends', 'Daily Routine', 'Holidays'
  ];

  const part2Topics = [
    { topic: 'A memorable journey', questions: ['Where did you go?', 'Who did you go with?', 'What did you do there?', 'Why was it memorable?'] },
    { topic: 'A person who influenced you', questions: ['Who is this person?', 'How do you know them?', 'What qualities do they have?', 'How did they influence you?'] },
    { topic: 'A skill you learned', questions: ['What skill is it?', 'How did you learn it?', 'Who helped you?', 'How do you use this skill?'] },
    { topic: 'A book you enjoyed', questions: ['What book is it?', 'What is it about?', 'Why did you enjoy it?', 'Would you recommend it?'] },
    { topic: 'A place you like to visit', questions: ['Where is it?', 'What is special about it?', 'How often do you go?', 'What do you do there?'] },
    { topic: 'An important decision', questions: ['What was the decision?', 'When did you make it?', 'How did you decide?', 'What was the outcome?'] },
    { topic: 'A childhood memory', questions: ['What is the memory?', 'How old were you?', 'Who was involved?', 'Why do you remember it?'] },
    { topic: 'A goal you achieved', questions: ['What was the goal?', 'How long did it take?', 'What challenges did you face?', 'How did you feel?'] }
  ];

  const part3Topics = [
    { topic: 'Education and Learning', questions: ['How has education changed?', 'What role does technology play?', 'What skills are most important?'] },
    { topic: 'Work and Career', questions: ['How has work changed?', 'What makes a good workplace?', 'How important is work-life balance?'] },
    { topic: 'Environment', questions: ['What environmental issues matter most?', 'Whose responsibility is it?', 'What can individuals do?'] },
    { topic: 'Technology', questions: ['How has technology changed life?', 'What are the disadvantages?', 'What will the future bring?'] },
    { topic: 'Society', questions: ['How has society changed?', 'What challenges do we face?', 'How can communities improve?'] },
    { topic: 'Culture', questions: ['How important is cultural identity?', 'How do cultures change?', 'Should cultures be preserved?'] }
  ];

  const testsPerPart = Math.floor(count / 3);

  // Part 1 Tests
  for (let i = 0; i < testsPerPart; i++) {
    const topic = part1Topics[i % part1Topics.length];
    tests.push({
      id: uuidv4(),
      title: `Part 1: ${topic}`,
      part: 1,
      topic,
      questions: generatePart1Questions(topic)
    });
  }

  // Part 2 Tests
  for (let i = 0; i < testsPerPart; i++) {
    const topicData = part2Topics[i % part2Topics.length];
    tests.push({
      id: uuidv4(),
      title: `Part 2: ${topicData.topic}`,
      part: 2,
      topic: topicData.topic,
      questions: [{
        id: uuidv4(),
        question: `Describe ${topicData.topic.toLowerCase()}. You should say:\n- ${topicData.questions.join('\n- ')}`,
        followUp: ['Can you tell me more about that?', 'How did that make you feel?'],
        tips: 'Speak for 1-2 minutes. Use the preparation time to make notes.',
        sampleAnswer: `I would like to talk about ${topicData.topic.toLowerCase()}...`,
        timeLimit: 120
      }]
    });
  }

  // Part 3 Tests
  for (let i = 0; i < testsPerPart; i++) {
    const topicData = part3Topics[i % part3Topics.length];
    tests.push({
      id: uuidv4(),
      title: `Part 3: ${topicData.topic}`,
      part: 3,
      topic: topicData.topic,
      questions: topicData.questions.map(q => ({
        id: uuidv4(),
        question: q,
        followUp: ['Why do you think that?', 'Can you give an example?'],
        tips: 'Give detailed answers with examples and explanations.',
        sampleAnswer: `That is an interesting question. In my view...`,
        timeLimit: 60
      }))
    });
  }

  return tests;
}

function generatePart1Questions(topic) {
  const genericQuestions = [
    `Do you enjoy ${topic.toLowerCase()}?`,
    `How often do you engage with ${topic.toLowerCase()}?`,
    `Has your interest in ${topic.toLowerCase()} changed over time?`,
    `What do you like most about ${topic.toLowerCase()}?`
  ];

  return genericQuestions.map(q => ({
    id: uuidv4(),
    question: q,
    followUp: ['Why is that?', 'Can you explain more?'],
    tips: 'Give natural, conversational answers of 2-3 sentences.',
    sampleAnswer: `Yes, I find ${topic.toLowerCase()} quite interesting because...`,
    timeLimit: 30
  }));
}

// Generate Reading Tests
function generateReadingTests(count) {
  const tests = [];
  const difficulties = ['easy', 'medium', 'hard'];

  for (let i = 0; i < count; i++) {
    const topicData = readingTopics[i % readingTopics.length];
    const theme = topicData.themes[Math.floor(i / readingTopics.length) % topicData.themes.length];
    const difficulty = difficulties[i % 3];

    tests.push({
      id: uuidv4(),
      title: `${theme}`,
      difficulty,
      topic: topicData.topic,
      passage: generateReadingPassage(topicData.topic, theme, difficulty),
      wordCount: { easy: 600, medium: 800, hard: 1000 }[difficulty],
      timeLimit: 20,
      questions: generateReadingQuestions(difficulty)
    });
  }

  return tests;
}

// ============================================
// Main Seeding Function
// ============================================

async function seedDatabase() {
  try {
    console.log('🌱 Connecting to MongoDB...');
    await mongoose.connect(MONGODB_URI);
    console.log('✅ Connected to MongoDB');

    // Clear existing data
    console.log('🗑️  Clearing existing data...');
    await Promise.all([
      ReadingTest.deleteMany({}),
      ListeningTest.deleteMany({}),
      WritingTask.deleteMany({}),
      SpeakingTest.deleteMany({})
    ]);

    // Generate and insert data
    console.log('📝 Generating reading tests...');
    const readingTests = generateReadingTests(300);
    await ReadingTest.insertMany(readingTests);
    console.log(`   ✅ Created ${readingTests.length} reading tests`);

    console.log('🎧 Generating listening tests...');
    const listeningTests = generateListeningTests(400);
    await ListeningTest.insertMany(listeningTests);
    console.log(`   ✅ Created ${listeningTests.length} listening tests`);

    console.log('✍️  Generating writing tasks...');
    const writingTasks = generateWritingTasks(200);
    await WritingTask.insertMany(writingTasks);
    console.log(`   ✅ Created ${writingTasks.length} writing tasks`);

    console.log('🎤 Generating speaking tests...');
    const speakingTests = generateSpeakingTests(150);
    await SpeakingTest.insertMany(speakingTests);
    console.log(`   ✅ Created ${speakingTests.length} speaking tests`);

    const total = readingTests.length + listeningTests.length + writingTasks.length + speakingTests.length;
    console.log(`\n🎉 Database seeded successfully with ${total} total tests!`);

    // Summary
    console.log('\n📊 Summary:');
    console.log(`   Reading Tests: ${readingTests.length}`);
    console.log(`   Listening Tests: ${listeningTests.length}`);
    console.log(`   Writing Tasks: ${writingTasks.length}`);
    console.log(`   Speaking Tests: ${speakingTests.length}`);
    console.log(`   TOTAL: ${total}`);

  } catch (error) {
    console.error('❌ Error seeding database:', error);
    process.exit(1);
  } finally {
    await mongoose.disconnect();
    console.log('\n👋 Disconnected from MongoDB');
  }
}

// Run seeding
seedDatabase();
