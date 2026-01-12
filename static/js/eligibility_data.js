// RCIC-Style Eligibility Checker Data
// All questions, NOC database, and recommendation data

const QUESTIONS = [
    // Step 1: Personal Information
    { id: 'age', category: 'Personal Information', step: 1,
      question: 'What is your age?',
      options: [
        { value: '18-24', label: '18-24 years old' },
        { value: '25-29', label: '25-29 years old' },
        { value: '30-34', label: '30-34 years old' },
        { value: '35-39', label: '35-39 years old' },
        { value: '40-44', label: '40-44 years old' },
        { value: '45-49', label: '45-49 years old' },
        { value: '50+', label: '50 years or older' }
      ]
    },
    { id: 'marital_status', category: 'Personal Information', step: 1,
      question: 'What is your marital status?',
      options: [
        { value: 'single', label: 'Single / Never Married' },
        { value: 'married', label: 'Married or Common-law Partner' },
        { value: 'divorced', label: 'Divorced / Separated / Widowed' }
      ]
    },
    { id: 'spouse_coming', category: 'Personal Information', step: 1,
      question: 'Will your spouse/partner be included in your application?',
      condition: ans => ans.marital_status === 'married',
      options: [
        { value: 'yes', label: 'Yes, applying together' },
        { value: 'no', label: 'No, applying alone' }
      ]
    },
    { id: 'current_location', category: 'Personal Information', step: 1,
      question: 'Where do you currently live?',
      options: [
        { value: 'in_canada', label: 'Currently in Canada' },
        { value: 'outside', label: 'Outside Canada' }
      ]
    },

    // Step 2: Canadian Status (if in Canada)
    { id: 'canada_status', category: 'Current Status', step: 2,
      question: 'What is your current immigration status in Canada?',
      condition: ans => ans.current_location === 'in_canada',
      options: [
        { value: 'work_employer', label: 'Work Permit (Employer-specific)', desc: 'LMIA-based or employer-tied' },
        { value: 'work_open', label: 'Work Permit (Open/PGWP)', desc: 'Post-graduation or spouse open work permit' },
        { value: 'study', label: 'Study Permit', desc: 'Currently studying in Canada' },
        { value: 'visitor', label: 'Visitor Status', desc: 'Tourist or visitor record' },
        { value: 'implied', label: 'Implied Status', desc: 'Applied for extension, waiting' },
        { value: 'no_status', label: 'No Valid Status', desc: 'Overstayed or no permit' }
      ]
    },
    { id: 'time_in_canada', category: 'Current Status', step: 2,
      question: 'How long have you been living in Canada?',
      condition: ans => ans.current_location === 'in_canada',
      options: [
        { value: 'less_6', label: 'Less than 6 months' },
        { value: '6_12', label: '6-12 months' },
        { value: '1_2', label: '1-2 years' },
        { value: '2_3', label: '2-3 years' },
        { value: '3_plus', label: '3+ years' }
      ]
    },
    { id: 'target_province', category: 'Current Status', step: 2,
      question: 'Which province would you prefer to live in?',
      options: [
        { value: 'ontario', label: 'Ontario' },
        { value: 'bc', label: 'British Columbia' },
        { value: 'alberta', label: 'Alberta' },
        { value: 'quebec', label: 'Quebec' },
        { value: 'manitoba', label: 'Manitoba' },
        { value: 'saskatchewan', label: 'Saskatchewan' },
        { value: 'nova_scotia', label: 'Nova Scotia' },
        { value: 'new_brunswick', label: 'New Brunswick' },
        { value: 'pei', label: 'Prince Edward Island' },
        { value: 'newfoundland', label: 'Newfoundland & Labrador' },
        { value: 'any', label: 'Open to any province' }
      ]
    },

    // Step 3: Education
    { id: 'education_level', category: 'Education', step: 3,
      question: 'What is your highest completed education?',
      options: [
        { value: 'none', label: 'Less than high school' },
        { value: 'highschool', label: 'High school diploma' },
        { value: 'oneyear', label: 'One-year post-secondary diploma/certificate' },
        { value: 'twoyear', label: 'Two-year post-secondary diploma' },
        { value: 'bachelors', label: "Bachelor's degree (3+ years)" },
        { value: 'two_degrees', label: 'Two or more degrees (one 3+ years)' },
        { value: 'masters', label: "Master's degree" },
        { value: 'phd', label: 'Doctoral degree (PhD)' }
      ]
    },
    { id: 'education_country', category: 'Education', step: 3,
      question: 'Where did you complete your highest education?',
      options: [
        { value: 'canada', label: 'In Canada' },
        { value: 'foreign', label: 'Outside Canada' }
      ]
    },
    { id: 'canadian_edu_level', category: 'Education', step: 3,
      question: 'What Canadian credential do you have?',
      condition: ans => ans.education_country === 'canada',
      options: [
        { value: 'oneyear', label: 'One-year certificate/diploma' },
        { value: 'twoyear', label: 'Two-year diploma' },
        { value: 'threeyear', label: "Three-year bachelor's degree" },
        { value: 'masters', label: "Master's degree" },
        { value: 'phd', label: 'PhD/Doctoral degree' }
      ]
    },
    { id: 'eca_status', category: 'Education', step: 3,
      question: 'Do you have an Educational Credential Assessment (ECA)?',
      condition: ans => ans.education_country === 'foreign',
      helpText: 'ECA is required for Express Entry to verify foreign credentials',
      options: [
        { value: 'yes', label: 'Yes, completed and valid', desc: 'Valid for 5 years from issue date' },
        { value: 'in_progress', label: 'In progress', desc: 'Applied, waiting for results' },
        { value: 'no', label: 'No, not started', desc: 'Takes 4-8 weeks to complete' }
      ]
    },
    { id: 'field_of_study', category: 'Education', step: 3,
      question: 'What field did you study?',
      options: [
        { value: 'tech', label: 'Computer Science / IT / Software' },
        { value: 'engineering', label: 'Engineering (Civil, Mechanical, Electrical)' },
        { value: 'healthcare', label: 'Healthcare / Nursing / Medicine' },
        { value: 'trades', label: 'Skilled Trades (Electrical, Plumbing, Welding)' },
        { value: 'business', label: 'Business / Finance / Accounting' },
        { value: 'science', label: 'Science (Biology, Chemistry, Physics, Math)' },
        { value: 'education', label: 'Education / Teaching' },
        { value: 'agriculture', label: 'Agriculture / Agri-food' },
        { value: 'transport', label: 'Transport / Logistics' },
        { value: 'hospitality', label: 'Hospitality / Tourism' },
        { value: 'arts', label: 'Arts / Design / Media' },
        { value: 'social', label: 'Social Sciences / Humanities' },
        { value: 'other', label: 'Other' }
      ]
    },

    // Step 4: Work Experience & Occupation
    { id: 'occupation', category: 'Work Experience', step: 4,
      question: 'What is your current or most recent occupation?',
      type: 'search',
      placeholder: 'Start typing: Software Engineer, Nurse, Accountant...'
    },
    { id: 'foreign_experience', category: 'Work Experience', step: 4,
      question: 'How many years of skilled work experience do you have OUTSIDE Canada?',
      helpText: 'Skilled work = NOC TEER 0, 1, 2, or 3 occupations only',
      options: [
        { value: 'none', label: 'None or less than 1 year' },
        { value: '1', label: '1 year' },
        { value: '2', label: '2 years' },
        { value: '3', label: '3 years' },
        { value: '4_5', label: '4-5 years' },
        { value: '6_plus', label: '6+ years' }
      ]
    },
    { id: 'canadian_experience', category: 'Work Experience', step: 4,
      question: 'How many years of skilled work experience do you have IN Canada?',
      helpText: 'Must be legal work with valid work permit',
      options: [
        { value: 'none', label: 'None' },
        { value: '1', label: '1 year' },
        { value: '2', label: '2 years' },
        { value: '3', label: '3 years' },
        { value: '4', label: '4 years' },
        { value: '5_plus', label: '5+ years' }
      ]
    },
    { id: 'trade_cert', category: 'Work Experience', step: 4,
      question: 'Do you have a Canadian trade certificate?',
      options: [
        { value: 'red_seal', label: 'Yes, Red Seal certified', desc: 'Nationally recognized trade qualification' },
        { value: 'provincial', label: 'Yes, provincial certification', desc: 'Province-specific trade license' },
        { value: 'no', label: 'No trade certification' }
      ]
    },

    // Step 5: Language Proficiency
    { id: 'english_test', category: 'Language Proficiency', step: 5,
      question: 'Have you taken an English language test?',
      options: [
        { value: 'ielts', label: 'IELTS General Training' },
        { value: 'celpip', label: 'CELPIP General' },
        { value: 'pte', label: 'PTE Core' },
        { value: 'none', label: 'Not yet / No valid test' }
      ]
    },
    { id: 'english_clb', category: 'Language Proficiency', step: 5,
      question: 'What is your overall English CLB level?',
      condition: ans => ans.english_test !== 'none',
      helpText: 'CLB 7 = IELTS 6.0 each | CLB 9 = IELTS 7.0-7.5 each',
      options: [
        { value: '4', label: 'CLB 4', desc: 'IELTS 4.0-4.5' },
        { value: '5', label: 'CLB 5', desc: 'IELTS 5.0' },
        { value: '6', label: 'CLB 6', desc: 'IELTS 5.5' },
        { value: '7', label: 'CLB 7', desc: 'IELTS 6.0' },
        { value: '8', label: 'CLB 8', desc: 'IELTS 6.5' },
        { value: '9', label: 'CLB 9', desc: 'IELTS 7.0-7.5' },
        { value: '10', label: 'CLB 10+', desc: 'IELTS 8.0+' }
      ]
    },
    { id: 'french_level', category: 'Language Proficiency', step: 5,
      question: 'Do you have French language proficiency?',
      options: [
        { value: 'nclc7_plus', label: 'NCLC 7+ (Strong)', desc: 'TEF/TCF with strong scores' },
        { value: 'nclc5_6', label: 'NCLC 5-6 (Moderate)', desc: 'Basic to intermediate French' },
        { value: 'below5', label: 'Below NCLC 5', desc: 'Beginner French' },
        { value: 'none', label: 'No French / Not tested' }
      ]
    },

    // Step 6: Job Offer & Provincial Connections
    { id: 'job_offer', category: 'Job Offer', step: 6,
      question: 'Do you have a valid job offer from a Canadian employer?',
      options: [
        { value: 'yes', label: 'Yes, I have a job offer' },
        { value: 'in_progress', label: 'In discussions / interviewing' },
        { value: 'no', label: 'No job offer' }
      ]
    },
    { id: 'job_lmia', category: 'Job Offer', step: 6,
      question: 'Is the job offer LMIA-supported or LMIA-exempt?',
      condition: ans => ans.job_offer === 'yes',
      options: [
        { value: 'lmia_approved', label: 'LMIA-approved', desc: 'Employer has positive LMIA' },
        { value: 'lmia_exempt', label: 'LMIA-exempt', desc: 'CUSMA, intra-company, etc.' },
        { value: 'not_sure', label: 'Not sure / In progress' },
        { value: 'no_lmia', label: 'No LMIA', desc: 'Job offer without LMIA' }
      ]
    },
    { id: 'job_noc_teer', category: 'Job Offer', step: 6,
      question: 'What NOC TEER level is the job offer?',
      condition: ans => ans.job_offer === 'yes',
      options: [
        { value: '0', label: 'TEER 0 - Senior Management', desc: '+200 CRS points' },
        { value: '1', label: 'TEER 1 - Professional', desc: '+50 CRS points' },
        { value: '2', label: 'TEER 2 - Technical', desc: '+50 CRS points' },
        { value: '3', label: 'TEER 3 - Skilled Trades', desc: '+50 CRS points' },
        { value: '4_5', label: 'TEER 4 or 5', desc: 'No CRS points for job offer' }
      ]
    },
    { id: 'job_province', category: 'Job Offer', step: 6,
      question: 'Which province is the job offer in?',
      condition: ans => ans.job_offer === 'yes',
      options: [
        { value: 'ontario', label: 'Ontario' },
        { value: 'bc', label: 'British Columbia' },
        { value: 'alberta', label: 'Alberta' },
        { value: 'manitoba', label: 'Manitoba' },
        { value: 'saskatchewan', label: 'Saskatchewan' },
        { value: 'nova_scotia', label: 'Nova Scotia' },
        { value: 'new_brunswick', label: 'New Brunswick' },
        { value: 'pei', label: 'Prince Edward Island' },
        { value: 'newfoundland', label: 'Newfoundland & Labrador' },
        { value: 'other', label: 'Other territory' }
      ]
    },
    { id: 'provincial_connection', category: 'Job Offer', step: 6,
      question: 'Do you have any connections to a specific province?',
      options: [
        { value: 'work', label: 'Previous work experience in a province' },
        { value: 'study', label: 'Previous study in a province' },
        { value: 'family', label: 'Family members (PR/citizen) in a province' },
        { value: 'living', label: 'Currently living in a province' },
        { value: 'none', label: 'No provincial connections' }
      ]
    },

    // Step 7: Family & Financial
    { id: 'family_in_canada', category: 'Family & Financial', step: 7,
      question: 'Do you have close family members who are Canadian citizens or PRs?',
      options: [
        { value: 'sibling', label: 'Sibling (brother/sister)', desc: '+15 CRS points' },
        { value: 'parent', label: 'Parent or grandparent' },
        { value: 'child', label: 'Adult child (18+)' },
        { value: 'extended', label: 'Aunt / Uncle / Cousin' },
        { value: 'none', label: 'No family in Canada' }
      ]
    },
    { id: 'settlement_funds', category: 'Family & Financial', step: 7,
      question: 'Do you have proof of settlement funds?',
      helpText: 'Single: ~$14,690 CAD | Family of 4: ~$27,315 CAD',
      options: [
        { value: 'yes', label: 'Yes, I meet the requirement' },
        { value: 'exceed', label: 'Yes, I exceed the requirement' },
        { value: 'can_arrange', label: 'No, but I can arrange it' },
        { value: 'difficult', label: 'No, it will be difficult' }
      ]
    },

    // Step 8: Spouse/Partner Details
    { id: 'spouse_education', category: 'Spouse Details', step: 8,
      question: "What is your spouse's highest education level?",
      condition: ans => ans.spouse_coming === 'yes',
      options: [
        { value: 'highschool', label: 'High school or less' },
        { value: 'oneyear', label: 'One-year diploma' },
        { value: 'twoyear', label: 'Two-year diploma' },
        { value: 'bachelors', label: "Bachelor's degree" },
        { value: 'masters_plus', label: "Master's or PhD" }
      ]
    },
    { id: 'spouse_language', category: 'Spouse Details', step: 8,
      question: "What is your spouse's English CLB level?",
      condition: ans => ans.spouse_coming === 'yes',
      options: [
        { value: 'none', label: 'No test / Below CLB 4' },
        { value: '4', label: 'CLB 4' },
        { value: '5_6', label: 'CLB 5-6' },
        { value: '7_8', label: 'CLB 7-8' },
        { value: '9_plus', label: 'CLB 9+' }
      ]
    },
    { id: 'spouse_experience', category: 'Spouse Details', step: 8,
      question: 'Does your spouse have Canadian work experience?',
      condition: ans => ans.spouse_coming === 'yes',
      options: [
        { value: 'none', label: 'None' },
        { value: '1', label: '1 year' },
        { value: '2_plus', label: '2+ years' }
      ]
    },

    // Step 9: Previous Applications & Admissibility
    { id: 'previous_refusal', category: 'Admissibility', step: 9,
      question: 'Have you ever been refused a Canadian visa or permit?',
      options: [
        { value: 'no', label: 'No, never refused' },
        { value: 'once', label: 'Yes, once' },
        { value: 'multiple', label: 'Yes, multiple times' }
      ]
    },
    { id: 'medical_issues', category: 'Admissibility', step: 9,
      question: 'Do you have any medical conditions that could affect admissibility?',
      helpText: 'Conditions requiring excessive healthcare costs may affect eligibility',
      options: [
        { value: 'no', label: 'No medical concerns' },
        { value: 'manageable', label: 'Yes, but manageable' },
        { value: 'significant', label: 'Yes, significant condition' },
        { value: 'not_sure', label: 'Not sure' }
      ]
    },
    { id: 'criminal_history', category: 'Admissibility', step: 9,
      question: 'Do you have any criminal history (including DUI)?',
      options: [
        { value: 'no', label: 'No criminal history' },
        { value: 'minor', label: 'Yes, minor offense' },
        { value: 'serious', label: 'Yes, serious offense' }
      ]
    },
    { id: 'primary_goal', category: 'Admissibility', step: 9,
      question: 'What is your primary immigration goal?',
      options: [
        { value: 'pr_fast', label: 'Permanent Residence ASAP' },
        { value: 'work_then_pr', label: 'Work first, then PR' },
        { value: 'study_then_pr', label: 'Study first, then work & PR' },
        { value: 'not_sure', label: 'Not sure - need guidance' }
      ]
    }
];

// Simplified NOC Database
const NOC_DATABASE = [
    { code: '21231', title: 'Software Engineers', teer: 1, category: 'STEM' },
    { code: '21232', title: 'Software Developers', teer: 1, category: 'STEM' },
    { code: '21234', title: 'Web Developers', teer: 2, category: 'STEM' },
    { code: '21211', title: 'Data Scientists', teer: 1, category: 'STEM' },
    { code: '21223', title: 'Database Analysts', teer: 1, category: 'STEM' },
    { code: '21222', title: 'Cybersecurity Specialists', teer: 1, category: 'STEM' },
    { code: '21233', title: 'Web Designers', teer: 2, category: 'STEM' },
    { code: '21311', title: 'Electrical Engineers', teer: 1, category: 'STEM' },
    { code: '21310', title: 'Civil Engineers', teer: 1, category: 'STEM' },
    { code: '21321', title: 'Mechanical Engineers', teer: 1, category: 'STEM' },
    { code: '31301', title: 'Registered Nurses', teer: 1, category: 'Healthcare' },
    { code: '31302', title: 'Nurse Practitioners', teer: 1, category: 'Healthcare' },
    { code: '32101', title: 'Licensed Practical Nurses', teer: 2, category: 'Healthcare' },
    { code: '31100', title: 'Physicians - Specialists', teer: 0, category: 'Healthcare' },
    { code: '31102', title: 'General Practitioners', teer: 0, category: 'Healthcare' },
    { code: '32102', title: 'Paramedics', teer: 2, category: 'Healthcare' },
    { code: '33102', title: 'Nurse Aides', teer: 3, category: 'Healthcare' },
    { code: '11100', title: 'Financial Managers', teer: 0, category: 'Business' },
    { code: '11102', title: 'HR Managers', teer: 0, category: 'Business' },
    { code: '11201', title: 'Accountants', teer: 1, category: 'Business' },
    { code: '11200', title: 'Financial Analysts', teer: 1, category: 'Business' },
    { code: '12011', title: 'Administrative Supervisors', teer: 2, category: 'Business' },
    { code: '13100', title: 'Administrative Officers', teer: 2, category: 'Business' },
    { code: '72310', title: 'Electricians', teer: 2, category: 'Trades' },
    { code: '72311', title: 'Industrial Electricians', teer: 2, category: 'Trades' },
    { code: '72320', title: 'Plumbers', teer: 2, category: 'Trades' },
    { code: '72400', title: 'Carpenters', teer: 2, category: 'Trades' },
    { code: '72401', title: 'Cabinetmakers', teer: 2, category: 'Trades' },
    { code: '72106', title: 'Welders', teer: 2, category: 'Trades' },
    { code: '73300', title: 'Truck Drivers', teer: 3, category: 'Transport' },
    { code: '73301', title: 'Bus Drivers', teer: 3, category: 'Transport' },
    { code: '73200', title: 'Residential Painters', teer: 3, category: 'Trades' },
    { code: '63200', title: 'Cooks', teer: 3, category: 'Hospitality' },
    { code: '62200', title: 'Chefs', teer: 2, category: 'Hospitality' },
    { code: '64100', title: 'Retail Salespersons', teer: 4, category: 'Sales' },
    { code: '64101', title: 'Sales Representatives', teer: 2, category: 'Sales' },
    { code: '41200', title: 'University Professors', teer: 1, category: 'Education' },
    { code: '41220', title: 'Secondary School Teachers', teer: 1, category: 'Education' },
    { code: '41221', title: 'Elementary Teachers', teer: 1, category: 'Education' },
    { code: '00010', title: 'Senior Managers - Finance', teer: 0, category: 'Management' },
    { code: '00012', title: 'Senior Managers - Trade', teer: 0, category: 'Management' },
    { code: '00013', title: 'Senior Managers - Construction', teer: 0, category: 'Management' },
    { code: '10010', title: 'Financial Managers', teer: 0, category: 'Management' },
    { code: '10019', title: 'Other Business Managers', teer: 0, category: 'Management' },
    { code: '20010', title: 'Engineering Managers', teer: 0, category: 'Management' },
    { code: '20011', title: 'Architecture Managers', teer: 0, category: 'Management' },
    { code: '20012', title: 'IT Managers', teer: 0, category: 'Management' }
];

// Provincial In-Demand Categories
const PROVINCIAL_IN_DEMAND = {
    bc: { tech: true, healthcare: true, trades: true },
    ontario: { tech: true, healthcare: true, trades: true },
    alberta: { tech: true, healthcare: true, trades: true, transport: true },
    saskatchewan: { healthcare: true, trades: true, agriculture: true },
    manitoba: { healthcare: true, trades: true },
    nova_scotia: { healthcare: true, trades: true },
    new_brunswick: { healthcare: true, tech: true },
    pei: { healthcare: true, trades: true },
    newfoundland: { healthcare: true, trades: true }
};

// Career Transitions for TEER 4/5 workers
const CAREER_TRANSITIONS = {
    'retail_sales': {
        from: 'Retail Salesperson (TEER 4)',
        transitions: [
            { to: 'Sales Representative', teer: 2, path: 'B2B sales experience + certifications', gain: '+50-100 CRS' },
            { to: 'Purchasing Agent', teer: 2, path: 'Supply chain certification', gain: '+50-100 CRS' }
        ]
    },
    'cook': {
        from: 'Cook (TEER 3)',
        transitions: [
            { to: 'Chef', teer: 2, path: 'Red Seal certification + management experience', gain: '+25-50 CRS' }
        ]
    },
    'caregiver': {
        from: 'Caregiver (TEER 4)',
        transitions: [
            { to: 'Nurse Aide', teer: 3, path: 'Personal Support Worker certification', gain: '+30-50 CRS' },
            { to: 'Licensed Practical Nurse', teer: 2, path: 'LPN diploma (1-2 years)', gain: '+50-80 CRS' }
        ]
    }
};

// Alternative Pathways
const ALTERNATIVE_PATHWAYS = [
    {
        name: 'Study → PGWP → CEC',
        description: 'Study in Canada for 2 years, get 3-year PGWP, work 1 year, apply via CEC',
        timeline: '3-4 years to PR',
        pros: ['Canadian education bonus', 'Canadian experience', 'Lower CRS competition'],
        cons: ['Tuition costs ($15-40k/year)', 'Longer timeline']
    },
    {
        name: 'Atlantic Immigration Program (AIP)',
        description: 'Employer-driven program for NS, NB, PEI, NL - no CRS competition',
        timeline: '6-12 months',
        pros: ['No CRS needed', 'Fast processing', 'Employer support'],
        cons: ['Must stay in Atlantic Canada', 'Job offer required']
    },
    {
        name: 'Rural & Northern Immigration Pilot',
        description: 'Community-driven program for smaller towns and rural areas',
        timeline: '6-18 months',
        pros: ['Lower competition', 'Community support', 'Lower cost of living'],
        cons: ['Limited locations', 'Must stay in community']
    }
];
