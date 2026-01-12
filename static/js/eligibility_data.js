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
    // IELTS-specific scores
    { id: 'ielts_speaking', category: 'Language Proficiency', step: 5,
      question: 'What is your IELTS Speaking band score?',
      condition: ans => ans.english_test === 'ielts',
      options: [
        { value: '4.0', label: '4.0', desc: 'CLB 4' },
        { value: '5.0', label: '5.0', desc: 'CLB 5' },
        { value: '5.5', label: '5.5', desc: 'CLB 6' },
        { value: '6.0', label: '6.0', desc: 'CLB 7' },
        { value: '6.5', label: '6.5', desc: 'CLB 8' },
        { value: '7.0', label: '7.0', desc: 'CLB 9' },
        { value: '7.5', label: '7.5', desc: 'CLB 9' },
        { value: '8.0+', label: '8.0 or higher', desc: 'CLB 10+' }
      ]
    },
    { id: 'ielts_listening', category: 'Language Proficiency', step: 5,
      question: 'What is your IELTS Listening band score?',
      condition: ans => ans.english_test === 'ielts',
      options: [
        { value: '4.5', label: '4.5', desc: 'CLB 4' },
        { value: '5.0', label: '5.0', desc: 'CLB 5' },
        { value: '5.5', label: '5.5', desc: 'CLB 6' },
        { value: '6.0', label: '6.0', desc: 'CLB 7' },
        { value: '7.5', label: '7.5', desc: 'CLB 8' },
        { value: '8.0', label: '8.0', desc: 'CLB 9' },
        { value: '8.5+', label: '8.5 or higher', desc: 'CLB 10+' }
      ]
    },
    { id: 'ielts_reading', category: 'Language Proficiency', step: 5,
      question: 'What is your IELTS Reading band score?',
      condition: ans => ans.english_test === 'ielts',
      options: [
        { value: '3.5', label: '3.5', desc: 'CLB 4' },
        { value: '4.0', label: '4.0', desc: 'CLB 5' },
        { value: '5.0', label: '5.0', desc: 'CLB 6' },
        { value: '6.0', label: '6.0', desc: 'CLB 7' },
        { value: '6.5', label: '6.5', desc: 'CLB 8' },
        { value: '7.0', label: '7.0', desc: 'CLB 9' },
        { value: '8.0+', label: '8.0 or higher', desc: 'CLB 10+' }
      ]
    },
    { id: 'ielts_writing', category: 'Language Proficiency', step: 5,
      question: 'What is your IELTS Writing band score?',
      condition: ans => ans.english_test === 'ielts',
      options: [
        { value: '4.0', label: '4.0', desc: 'CLB 4' },
        { value: '5.0', label: '5.0', desc: 'CLB 5' },
        { value: '5.5', label: '5.5', desc: 'CLB 6' },
        { value: '6.0', label: '6.0', desc: 'CLB 7' },
        { value: '6.5', label: '6.5', desc: 'CLB 8' },
        { value: '7.0', label: '7.0', desc: 'CLB 9' },
        { value: '7.5+', label: '7.5 or higher', desc: 'CLB 10+' }
      ]
    },
    // CELPIP-specific scores
    { id: 'celpip_speaking', category: 'Language Proficiency', step: 5,
      question: 'What is your CELPIP Speaking score?',
      condition: ans => ans.english_test === 'celpip',
      options: [
        { value: '4', label: 'Level 4', desc: 'CLB 4' },
        { value: '5', label: 'Level 5', desc: 'CLB 5' },
        { value: '6', label: 'Level 6', desc: 'CLB 6' },
        { value: '7', label: 'Level 7', desc: 'CLB 7' },
        { value: '8', label: 'Level 8', desc: 'CLB 8' },
        { value: '9', label: 'Level 9', desc: 'CLB 9' },
        { value: '10+', label: 'Level 10-12', desc: 'CLB 10+' }
      ]
    },
    { id: 'celpip_listening', category: 'Language Proficiency', step: 5,
      question: 'What is your CELPIP Listening score?',
      condition: ans => ans.english_test === 'celpip',
      options: [
        { value: '4', label: 'Level 4', desc: 'CLB 4' },
        { value: '5', label: 'Level 5', desc: 'CLB 5' },
        { value: '6', label: 'Level 6', desc: 'CLB 6' },
        { value: '7', label: 'Level 7', desc: 'CLB 7' },
        { value: '8', label: 'Level 8', desc: 'CLB 8' },
        { value: '9', label: 'Level 9', desc: 'CLB 9' },
        { value: '10+', label: 'Level 10-12', desc: 'CLB 10+' }
      ]
    },
    { id: 'celpip_reading', category: 'Language Proficiency', step: 5,
      question: 'What is your CELPIP Reading score?',
      condition: ans => ans.english_test === 'celpip',
      options: [
        { value: '4', label: 'Level 4', desc: 'CLB 4' },
        { value: '5', label: 'Level 5', desc: 'CLB 5' },
        { value: '6', label: 'Level 6', desc: 'CLB 6' },
        { value: '7', label: 'Level 7', desc: 'CLB 7' },
        { value: '8', label: 'Level 8', desc: 'CLB 8' },
        { value: '9', label: 'Level 9', desc: 'CLB 9' },
        { value: '10+', label: 'Level 10-12', desc: 'CLB 10+' }
      ]
    },
    { id: 'celpip_writing', category: 'Language Proficiency', step: 5,
      question: 'What is your CELPIP Writing score?',
      condition: ans => ans.english_test === 'celpip',
      options: [
        { value: '4', label: 'Level 4', desc: 'CLB 4' },
        { value: '5', label: 'Level 5', desc: 'CLB 5' },
        { value: '6', label: 'Level 6', desc: 'CLB 6' },
        { value: '7', label: 'Level 7', desc: 'CLB 7' },
        { value: '8', label: 'Level 8', desc: 'CLB 8' },
        { value: '9', label: 'Level 9', desc: 'CLB 9' },
        { value: '10+', label: 'Level 10-12', desc: 'CLB 10+' }
      ]
    },
    // PTE Core scores
    { id: 'pte_speaking', category: 'Language Proficiency', step: 5,
      question: 'What is your PTE Core Speaking score?',
      condition: ans => ans.english_test === 'pte',
      options: [
        { value: '42-50', label: '42-50', desc: 'CLB 4' },
        { value: '51-58', label: '51-58', desc: 'CLB 5' },
        { value: '59-67', label: '59-67', desc: 'CLB 6' },
        { value: '68-75', label: '68-75', desc: 'CLB 7' },
        { value: '76-83', label: '76-83', desc: 'CLB 8' },
        { value: '84-88', label: '84-88', desc: 'CLB 9' },
        { value: '89+', label: '89-90', desc: 'CLB 10+' }
      ]
    },
    { id: 'pte_listening', category: 'Language Proficiency', step: 5,
      question: 'What is your PTE Core Listening score?',
      condition: ans => ans.english_test === 'pte',
      options: [
        { value: '28-32', label: '28-32', desc: 'CLB 4' },
        { value: '33-38', label: '33-38', desc: 'CLB 5' },
        { value: '39-49', label: '39-49', desc: 'CLB 6' },
        { value: '50-59', label: '50-59', desc: 'CLB 7' },
        { value: '60-70', label: '60-70', desc: 'CLB 8' },
        { value: '71-81', label: '71-81', desc: 'CLB 9' },
        { value: '82+', label: '82-90', desc: 'CLB 10+' }
      ]
    },
    { id: 'pte_reading', category: 'Language Proficiency', step: 5,
      question: 'What is your PTE Core Reading score?',
      condition: ans => ans.english_test === 'pte',
      options: [
        { value: '33-40', label: '33-40', desc: 'CLB 4' },
        { value: '41-50', label: '41-50', desc: 'CLB 5' },
        { value: '51-59', label: '51-59', desc: 'CLB 6' },
        { value: '60-68', label: '60-68', desc: 'CLB 7' },
        { value: '69-77', label: '69-77', desc: 'CLB 8' },
        { value: '78-87', label: '78-87', desc: 'CLB 9' },
        { value: '88+', label: '88-90', desc: 'CLB 10+' }
      ]
    },
    { id: 'pte_writing', category: 'Language Proficiency', step: 5,
      question: 'What is your PTE Core Writing score?',
      condition: ans => ans.english_test === 'pte',
      options: [
        { value: '41-50', label: '41-50', desc: 'CLB 4' },
        { value: '51-59', label: '51-59', desc: 'CLB 5' },
        { value: '60-68', label: '60-68', desc: 'CLB 6' },
        { value: '69-78', label: '69-78', desc: 'CLB 7' },
        { value: '79-87', label: '79-87', desc: 'CLB 8' },
        { value: '88-89', label: '88-89', desc: 'CLB 9' },
        { value: '90', label: '90', desc: 'CLB 10' }
      ]
    },
    // French language tests
    { id: 'french_test', category: 'Language Proficiency', step: 5,
      question: 'Have you taken a French language test?',
      options: [
        { value: 'tef', label: 'TEF Canada' },
        { value: 'tcf', label: 'TCF Canada' },
        { value: 'none', label: 'No French test / Not applicable' }
      ]
    },
    { id: 'french_level', category: 'Language Proficiency', step: 5,
      question: 'What is your French proficiency level (NCLC)?',
      condition: ans => ans.french_test !== 'none',
      helpText: 'NCLC 7+ qualifies you for French category draws with lower cutoffs',
      options: [
        { value: 'nclc7_plus', label: 'NCLC 7+ (Strong)', desc: 'All abilities NCLC 7 or higher' },
        { value: 'nclc5_6', label: 'NCLC 5-6 (Moderate)', desc: 'Basic to intermediate French' },
        { value: 'below5', label: 'Below NCLC 5', desc: 'Beginner French' }
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
      helpText: 'Not sure? <a href="/tools/noc-finder" target="_blank">Use our NOC Finder</a> to find your job\'s TEER level',
      options: [
        { value: '0', label: 'TEER 0 - Senior Management', desc: '+200 CRS points' },
        { value: '1', label: 'TEER 1 - Professional', desc: '+50 CRS points' },
        { value: '2', label: 'TEER 2 - Technical', desc: '+50 CRS points' },
        { value: '3', label: 'TEER 3 - Skilled Trades', desc: '+50 CRS points' },
        { value: '4_5', label: 'TEER 4 or 5', desc: 'No CRS points for job offer' },
        { value: 'not_sure', label: 'Not sure', desc: 'Use NOC Finder to check' }
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
      question: 'Do you have any connections to a specific province? (Select all that apply)',
      multiSelect: true,
      helpText: 'Multiple connections strengthen your PNP application',
      options: [
        { value: 'work', label: 'Previous work experience in province' },
        { value: 'study', label: 'Previous education/study in province' },
        { value: 'family', label: 'Family members (PR/citizen) in province' },
        { value: 'living', label: 'Currently living in province' },
        { value: 'job_offer', label: 'Job offer from employer in province' },
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

// Comprehensive NOC Database - All Major Occupations
const NOC_DATABASE = [
    // TEER 0 - Management
    { code: '00010', title: 'Senior Managers - Finance', teer: 0, category: 'Management' },
    { code: '00012', title: 'Senior Managers - Trade', teer: 0, category: 'Management' },
    { code: '00013', title: 'Senior Managers - Construction', teer: 0, category: 'Management' },
    { code: '00014', title: 'Senior Managers - Manufacturing', teer: 0, category: 'Management' },
    { code: '00015', title: 'Senior Managers - Transportation', teer: 0, category: 'Management' },
    { code: '10010', title: 'Financial Managers', teer: 0, category: 'Management' },
    { code: '10011', title: 'Human Resources Managers', teer: 0, category: 'Management' },
    { code: '10012', title: 'Purchasing Managers', teer: 0, category: 'Management' },
    { code: '10019', title: 'Other Business Managers', teer: 0, category: 'Management' },
    { code: '10020', title: 'Telecommunications Managers', teer: 0, category: 'Management' },
    { code: '20010', title: 'Engineering Managers', teer: 0, category: 'Management' },
    { code: '20011', title: 'Architecture Managers', teer: 0, category: 'Management' },
    { code: '20012', title: 'IT Managers', teer: 0, category: 'Management' },
    { code: '30010', title: 'Healthcare Managers', teer: 0, category: 'Management' },
    { code: '40010', title: 'Government Managers - Policy', teer: 0, category: 'Management' },
    { code: '40020', title: 'Administrators - Post-secondary', teer: 0, category: 'Management' },
    { code: '60010', title: 'Restaurant/Food Service Managers', teer: 0, category: 'Management' },
    { code: '60020', title: 'Accommodation Service Managers', teer: 0, category: 'Management' },
    { code: '60030', title: 'Retail/Wholesale Trade Managers', teer: 0, category: 'Management' },
    { code: '70010', title: 'Construction Managers', teer: 0, category: 'Management' },
    { code: '70012', title: 'Facility Operations Managers', teer: 0, category: 'Management' },
    { code: '80010', title: 'Agricultural Managers', teer: 0, category: 'Management' },

    // TEER 1 - Professional
    // STEM & Tech
    { code: '21231', title: 'Software Engineers', teer: 1, category: 'STEM' },
    { code: '21232', title: 'Software Developers', teer: 1, category: 'STEM' },
    { code: '21211', title: 'Data Scientists', teer: 1, category: 'STEM' },
    { code: '21210', title: 'Mathematicians/Statisticians', teer: 1, category: 'STEM' },
    { code: '21220', title: 'Cybersecurity Analysts', teer: 1, category: 'STEM' },
    { code: '21221', title: 'Business Systems Specialists', teer: 1, category: 'STEM' },
    { code: '21222', title: 'Information Systems Specialists', teer: 1, category: 'STEM' },
    { code: '21223', title: 'Database Analysts', teer: 1, category: 'STEM' },
    { code: '21230', title: 'Computer Systems Developers', teer: 1, category: 'STEM' },
    { code: '21300', title: 'Civil Engineers', teer: 1, category: 'STEM' },
    { code: '21301', title: 'Mechanical Engineers', teer: 1, category: 'STEM' },
    { code: '21310', title: 'Electrical/Electronics Engineers', teer: 1, category: 'STEM' },
    { code: '21311', title: 'Computer Engineers', teer: 1, category: 'STEM' },
    { code: '21320', title: 'Chemical Engineers', teer: 1, category: 'STEM' },
    { code: '21330', title: 'Mining Engineers', teer: 1, category: 'STEM' },
    { code: '21340', title: 'Petroleum Engineers', teer: 1, category: 'STEM' },
    { code: '21390', title: 'Aerospace Engineers', teer: 1, category: 'STEM' },
    { code: '22100', title: 'Chemical Technologists', teer: 1, category: 'STEM' },
    { code: '21100', title: 'Physicists/Astronomers', teer: 1, category: 'STEM' },
    { code: '21101', title: 'Chemists', teer: 1, category: 'STEM' },
    { code: '21102', title: 'Geoscientists', teer: 1, category: 'STEM' },
    { code: '21110', title: 'Biologists', teer: 1, category: 'STEM' },
    { code: '21112', title: 'Agricultural Scientists', teer: 1, category: 'STEM' },
    { code: '22110', title: 'Biological Technologists', teer: 1, category: 'STEM' },

    // Healthcare
    { code: '31100', title: 'Physicians - Specialists', teer: 0, category: 'Healthcare' },
    { code: '31101', title: 'Physicians - General Practitioners', teer: 0, category: 'Healthcare' },
    { code: '31102', title: 'Family Physicians', teer: 0, category: 'Healthcare' },
    { code: '31110', title: 'Dentists', teer: 0, category: 'Healthcare' },
    { code: '31111', title: 'Veterinarians', teer: 1, category: 'Healthcare' },
    { code: '31112', title: 'Optometrists', teer: 1, category: 'Healthcare' },
    { code: '31120', title: 'Pharmacists', teer: 1, category: 'Healthcare' },
    { code: '31121', title: 'Dietitians/Nutritionists', teer: 1, category: 'Healthcare' },
    { code: '31200', title: 'Psychologists', teer: 1, category: 'Healthcare' },
    { code: '31201', title: 'Chiropractors', teer: 1, category: 'Healthcare' },
    { code: '31202', title: 'Physiotherapists', teer: 1, category: 'Healthcare' },
    { code: '31203', title: 'Occupational Therapists', teer: 1, category: 'Healthcare' },
    { code: '31204', title: 'Audiologists/Speech Pathologists', teer: 1, category: 'Healthcare' },
    { code: '31301', title: 'Registered Nurses', teer: 1, category: 'Healthcare' },
    { code: '31302', title: 'Nurse Practitioners', teer: 1, category: 'Healthcare' },
    { code: '31303', title: 'Physician Assistants', teer: 1, category: 'Healthcare' },
    { code: '32101', title: 'Licensed Practical Nurses', teer: 2, category: 'Healthcare' },
    { code: '32102', title: 'Paramedics', teer: 2, category: 'Healthcare' },
    { code: '32103', title: 'Respiratory Therapists', teer: 2, category: 'Healthcare' },
    { code: '32109', title: 'Other Therapy Professionals', teer: 2, category: 'Healthcare' },
    { code: '32110', title: 'Dental Hygienists', teer: 2, category: 'Healthcare' },
    { code: '32111', title: 'Dental Technologists', teer: 2, category: 'Healthcare' },
    { code: '32120', title: 'Medical Lab Technologists', teer: 2, category: 'Healthcare' },
    { code: '32121', title: 'Medical Radiation Technologists', teer: 2, category: 'Healthcare' },
    { code: '32122', title: 'Medical Sonographers', teer: 2, category: 'Healthcare' },
    { code: '32123', title: 'Cardiology Technologists', teer: 2, category: 'Healthcare' },
    { code: '33100', title: 'Dental Assistants', teer: 3, category: 'Healthcare' },
    { code: '33101', title: 'Medical Lab Assistants', teer: 3, category: 'Healthcare' },
    { code: '33102', title: 'Nurse Aides/Patient Care Aides', teer: 3, category: 'Healthcare' },
    { code: '33103', title: 'Pharmacy Technicians', teer: 3, category: 'Healthcare' },
    { code: '44101', title: 'Home Support Workers', teer: 4, category: 'Healthcare' },

    // Business & Finance
    { code: '11100', title: 'Financial Auditors/Accountants', teer: 1, category: 'Business' },
    { code: '11101', title: 'Financial/Investment Analysts', teer: 1, category: 'Business' },
    { code: '11102', title: 'Financial Advisors', teer: 1, category: 'Business' },
    { code: '11103', title: 'Securities Agents/Investment Dealers', teer: 1, category: 'Business' },
    { code: '11200', title: 'Human Resources Professionals', teer: 1, category: 'Business' },
    { code: '11201', title: 'Business Management Consultants', teer: 1, category: 'Business' },
    { code: '11202', title: 'Advertising/Marketing Professionals', teer: 1, category: 'Business' },
    { code: '12010', title: 'Supervisors - Finance/Insurance', teer: 2, category: 'Business' },
    { code: '12011', title: 'Supervisors - Administrative', teer: 2, category: 'Business' },
    { code: '12013', title: 'Supervisors - Library/Correspondence', teer: 2, category: 'Business' },
    { code: '12100', title: 'Executive Assistants', teer: 2, category: 'Business' },
    { code: '12101', title: 'Human Resources Officers', teer: 2, category: 'Business' },
    { code: '12102', title: 'Purchasing Agents', teer: 2, category: 'Business' },
    { code: '12103', title: 'Insurance Adjusters/Claims Examiners', teer: 2, category: 'Business' },
    { code: '12110', title: 'Court Reporters', teer: 2, category: 'Business' },
    { code: '12111', title: 'Medical Transcriptionists', teer: 2, category: 'Business' },
    { code: '12200', title: 'Accounting Technicians', teer: 2, category: 'Business' },
    { code: '13100', title: 'Administrative Officers', teer: 2, category: 'Business' },
    { code: '13101', title: 'Property Administrators', teer: 2, category: 'Business' },
    { code: '13110', title: 'Administrative Assistants', teer: 3, category: 'Business' },
    { code: '13111', title: 'Legal Administrative Assistants', teer: 3, category: 'Business' },
    { code: '13112', title: 'Medical Administrative Assistants', teer: 3, category: 'Business' },
    { code: '14100', title: 'General Office Workers', teer: 4, category: 'Business' },
    { code: '14101', title: 'Receptionists', teer: 4, category: 'Business' },
    { code: '14110', title: 'Data Entry Clerks', teer: 4, category: 'Business' },

    // Education
    { code: '41200', title: 'University Professors', teer: 1, category: 'Education' },
    { code: '41201', title: 'Post-secondary Assistants/Instructors', teer: 1, category: 'Education' },
    { code: '41210', title: 'College Instructors', teer: 1, category: 'Education' },
    { code: '41220', title: 'Secondary School Teachers', teer: 1, category: 'Education' },
    { code: '41221', title: 'Elementary School Teachers', teer: 1, category: 'Education' },
    { code: '41300', title: 'Social Workers', teer: 1, category: 'Education' },
    { code: '41301', title: 'Therapists - Counselling', teer: 1, category: 'Education' },
    { code: '41310', title: 'Police Officers', teer: 2, category: 'Education' },
    { code: '41311', title: 'Firefighters', teer: 2, category: 'Education' },
    { code: '42100', title: 'Paralegals', teer: 2, category: 'Education' },
    { code: '42201', title: 'Early Childhood Educators', teer: 2, category: 'Education' },
    { code: '42202', title: 'Educational Assistants', teer: 3, category: 'Education' },

    // TEER 2 - Technical / Skilled Trades
    // Construction & Trades
    { code: '72010', title: 'Contractors/Supervisors - Electrical', teer: 2, category: 'Trades' },
    { code: '72011', title: 'Contractors/Supervisors - Pipefitting', teer: 2, category: 'Trades' },
    { code: '72012', title: 'Contractors/Supervisors - Metal Trades', teer: 2, category: 'Trades' },
    { code: '72013', title: 'Contractors/Supervisors - Carpentry', teer: 2, category: 'Trades' },
    { code: '72014', title: 'Contractors/Supervisors - Other Trades', teer: 2, category: 'Trades' },
    { code: '72020', title: 'Contractors/Supervisors - Mechanic Trades', teer: 2, category: 'Trades' },
    { code: '72021', title: 'Contractors/Supervisors - Heavy Equipment', teer: 2, category: 'Trades' },
    { code: '72100', title: 'Machinists', teer: 2, category: 'Trades' },
    { code: '72101', title: 'Tool and Die Makers', teer: 2, category: 'Trades' },
    { code: '72102', title: 'Sheet Metal Workers', teer: 2, category: 'Trades' },
    { code: '72103', title: 'Boilermakers', teer: 2, category: 'Trades' },
    { code: '72104', title: 'Structural Metal Fabricators', teer: 2, category: 'Trades' },
    { code: '72105', title: 'Ironworkers', teer: 2, category: 'Trades' },
    { code: '72106', title: 'Welders', teer: 2, category: 'Trades' },
    { code: '72200', title: 'Electricians (Except Industrial)', teer: 2, category: 'Trades' },
    { code: '72201', title: 'Industrial Electricians', teer: 2, category: 'Trades' },
    { code: '72300', title: 'Plumbers', teer: 2, category: 'Trades' },
    { code: '72301', title: 'Steamfitters/Pipefitters', teer: 2, category: 'Trades' },
    { code: '72302', title: 'Gas Fitters', teer: 2, category: 'Trades' },
    { code: '72310', title: 'Carpenters', teer: 2, category: 'Trades' },
    { code: '72311', title: 'Cabinetmakers', teer: 2, category: 'Trades' },
    { code: '72320', title: 'Bricklayers', teer: 2, category: 'Trades' },
    { code: '72321', title: 'Concrete Finishers', teer: 2, category: 'Trades' },
    { code: '72400', title: 'Construction Millwrights', teer: 2, category: 'Trades' },
    { code: '72401', title: 'Industrial Mechanics', teer: 2, category: 'Trades' },
    { code: '72402', title: 'Heavy Duty Equipment Mechanics', teer: 2, category: 'Trades' },
    { code: '72403', title: 'Refrigeration Mechanics (HVAC)', teer: 2, category: 'Trades' },
    { code: '72410', title: 'Automotive Service Technicians', teer: 2, category: 'Trades' },
    { code: '72411', title: 'Auto Body Technicians', teer: 2, category: 'Trades' },
    { code: '72420', title: 'Oil/Gas Well Drillers', teer: 2, category: 'Trades' },
    { code: '72421', title: 'Oil/Gas Well Servicers', teer: 2, category: 'Trades' },
    { code: '72500', title: 'Crane Operators', teer: 2, category: 'Trades' },
    { code: '72501', title: 'Drillers/Blasters', teer: 2, category: 'Trades' },
    { code: '73100', title: 'Concrete/Tile Setters', teer: 3, category: 'Trades' },
    { code: '73101', title: 'Plasterers/Drywall Installers', teer: 3, category: 'Trades' },
    { code: '73102', title: 'Roofers', teer: 3, category: 'Trades' },
    { code: '73110', title: 'Glaziers', teer: 3, category: 'Trades' },
    { code: '73111', title: 'Painters/Decorators', teer: 3, category: 'Trades' },
    { code: '73112', title: 'Floor Covering Installers', teer: 3, category: 'Trades' },
    { code: '73200', title: 'Residential/Commercial Installers', teer: 3, category: 'Trades' },
    { code: '73201', title: 'Pest Control Technicians', teer: 3, category: 'Trades' },

    // Transport
    { code: '72600', title: 'Air Pilots/Flight Engineers', teer: 2, category: 'Transport' },
    { code: '72601', title: 'Air Traffic Controllers', teer: 2, category: 'Transport' },
    { code: '72602', title: 'Deck Officers - Water Transport', teer: 2, category: 'Transport' },
    { code: '72603', title: 'Engineer Officers - Water Transport', teer: 2, category: 'Transport' },
    { code: '72604', title: 'Railway Conductors', teer: 2, category: 'Transport' },
    { code: '73300', title: 'Transport Truck Drivers', teer: 3, category: 'Transport' },
    { code: '73301', title: 'Bus Drivers/Subway Operators', teer: 3, category: 'Transport' },
    { code: '73310', title: 'Delivery/Courier Drivers', teer: 4, category: 'Transport' },
    { code: '73311', title: 'Taxi/Ride-share Drivers', teer: 4, category: 'Transport' },

    // Food & Hospitality
    { code: '62100', title: 'Chefs', teer: 2, category: 'Hospitality' },
    { code: '62200', title: 'Cooks', teer: 3, category: 'Hospitality' },
    { code: '62020', title: 'Food Service Supervisors', teer: 2, category: 'Hospitality' },
    { code: '63200', title: 'Bakers', teer: 3, category: 'Hospitality' },
    { code: '63201', title: 'Butchers/Meat Cutters', teer: 3, category: 'Hospitality' },
    { code: '63202', title: 'Fish/Seafood Plant Workers', teer: 4, category: 'Hospitality' },
    { code: '64300', title: 'Bartenders', teer: 4, category: 'Hospitality' },
    { code: '65200', title: 'Food Counter Attendants', teer: 5, category: 'Hospitality' },
    { code: '65201', title: 'Food Preparers/Kitchen Helpers', teer: 5, category: 'Hospitality' },
    { code: '65202', title: 'Dishwashers', teer: 5, category: 'Hospitality' },
    { code: '64301', title: 'Food/Beverage Servers', teer: 4, category: 'Hospitality' },
    { code: '64310', title: 'Hotel Front Desk Clerks', teer: 4, category: 'Hospitality' },
    { code: '64311', title: 'Tour Guides', teer: 4, category: 'Hospitality' },
    { code: '64312', title: 'Casino Dealers', teer: 4, category: 'Hospitality' },
    { code: '64320', title: 'Maids/Housekeepers', teer: 4, category: 'Hospitality' },
    { code: '63210', title: 'Hairstylists/Barbers', teer: 3, category: 'Hospitality' },
    { code: '63211', title: 'Estheticians', teer: 3, category: 'Hospitality' },

    // Retail & Sales
    { code: '62010', title: 'Retail Sales Supervisors', teer: 2, category: 'Sales' },
    { code: '62021', title: 'Technical Sales Specialists', teer: 2, category: 'Sales' },
    { code: '62022', title: 'Retail Buyers', teer: 2, category: 'Sales' },
    { code: '62023', title: 'Insurance Agents/Brokers', teer: 2, category: 'Sales' },
    { code: '62024', title: 'Real Estate Agents', teer: 2, category: 'Sales' },
    { code: '62100', title: 'Sales Representatives - Wholesale', teer: 2, category: 'Sales' },
    { code: '64100', title: 'Retail Salespersons', teer: 4, category: 'Sales' },
    { code: '64101', title: 'Cashiers', teer: 5, category: 'Sales' },

    // Agriculture & Farming
    { code: '82010', title: 'Supervisors - Logging/Forestry', teer: 2, category: 'Agriculture' },
    { code: '82011', title: 'Contractors - Landscaping', teer: 2, category: 'Agriculture' },
    { code: '82020', title: 'Supervisors - Agriculture', teer: 2, category: 'Agriculture' },
    { code: '82021', title: 'Supervisors - Aquaculture', teer: 2, category: 'Agriculture' },
    { code: '82030', title: 'Supervisors - Mining/Quarrying', teer: 2, category: 'Agriculture' },
    { code: '82031', title: 'Supervisors - Oil/Gas Drilling', teer: 2, category: 'Agriculture' },
    { code: '84120', title: 'Specialized Livestock Workers', teer: 4, category: 'Agriculture' },
    { code: '85100', title: 'Livestock Labourers', teer: 5, category: 'Agriculture' },
    { code: '85101', title: 'Harvesting Labourers', teer: 5, category: 'Agriculture' },
    { code: '85102', title: 'Nursery/Greenhouse Workers', teer: 5, category: 'Agriculture' },
    { code: '85103', title: 'Aquaculture/Marine Workers', teer: 5, category: 'Agriculture' },
    { code: '84100', title: 'Agricultural Equipment Operators', teer: 4, category: 'Agriculture' },
    { code: '83100', title: 'General Farm Workers', teer: 4, category: 'Agriculture' },

    // Manufacturing & Processing
    { code: '92010', title: 'Supervisors - Mineral Processing', teer: 2, category: 'Manufacturing' },
    { code: '92011', title: 'Supervisors - Petroleum Processing', teer: 2, category: 'Manufacturing' },
    { code: '92012', title: 'Supervisors - Chemical Processing', teer: 2, category: 'Manufacturing' },
    { code: '92020', title: 'Supervisors - Food Processing', teer: 2, category: 'Manufacturing' },
    { code: '92021', title: 'Supervisors - Plastics/Rubber', teer: 2, category: 'Manufacturing' },
    { code: '92100', title: 'Power Engineers', teer: 2, category: 'Manufacturing' },
    { code: '92101', title: 'Water Treatment Operators', teer: 2, category: 'Manufacturing' },
    { code: '93100', title: 'Central Control Operators - Petroleum', teer: 3, category: 'Manufacturing' },
    { code: '93101', title: 'Central Control Operators - Minerals', teer: 3, category: 'Manufacturing' },
    { code: '94100', title: 'Machine Operators - Metalworking', teer: 4, category: 'Manufacturing' },
    { code: '94101', title: 'Machine Operators - Plastics', teer: 4, category: 'Manufacturing' },
    { code: '94102', title: 'Machine Operators - Wood Processing', teer: 4, category: 'Manufacturing' },
    { code: '94103', title: 'Machine Operators - Textile', teer: 4, category: 'Manufacturing' },
    { code: '94104', title: 'Machine Operators - Printing', teer: 4, category: 'Manufacturing' },
    { code: '94105', title: 'Machine Operators - Food/Beverage', teer: 4, category: 'Manufacturing' },
    { code: '94140', title: 'Process Control Operators - Pulp', teer: 4, category: 'Manufacturing' },
    { code: '95100', title: 'Labourers - Mineral Processing', teer: 5, category: 'Manufacturing' },
    { code: '95101', title: 'Labourers - Metal Processing', teer: 5, category: 'Manufacturing' },
    { code: '95102', title: 'Labourers - Chemical Processing', teer: 5, category: 'Manufacturing' },
    { code: '95103', title: 'Labourers - Wood Processing', teer: 5, category: 'Manufacturing' },
    { code: '95104', title: 'Labourers - Rubber/Plastic', teer: 5, category: 'Manufacturing' },
    { code: '95105', title: 'Labourers - Textile Processing', teer: 5, category: 'Manufacturing' },
    { code: '95106', title: 'Labourers - Food/Beverage Processing', teer: 5, category: 'Manufacturing' },

    // IT & Tech (continued)
    { code: '21234', title: 'Web Developers', teer: 2, category: 'STEM' },
    { code: '21233', title: 'Web Designers', teer: 2, category: 'STEM' },
    { code: '22220', title: 'Computer Network Technicians', teer: 2, category: 'STEM' },
    { code: '22221', title: 'User Support Technicians', teer: 2, category: 'STEM' },
    { code: '22222', title: 'Information Systems Testing', teer: 2, category: 'STEM' },

    // Security & Protective
    { code: '64410', title: 'Security Guards', teer: 4, category: 'Security' },
    { code: '65310', title: 'Light Duty Cleaners', teer: 5, category: 'Security' },
    { code: '65311', title: 'Specialized Cleaners', teer: 4, category: 'Security' },
    { code: '65312', title: 'Janitors/Caretakers', teer: 4, category: 'Security' },

    // Arts & Media
    { code: '51111', title: 'Authors/Writers', teer: 1, category: 'Arts' },
    { code: '51112', title: 'Technical Writers', teer: 1, category: 'Arts' },
    { code: '51120', title: 'Journalists', teer: 1, category: 'Arts' },
    { code: '52100', title: 'Film/Video Camera Operators', teer: 2, category: 'Arts' },
    { code: '52110', title: 'Graphic Designers', teer: 2, category: 'Arts' },
    { code: '52111', title: 'Illustrators', teer: 2, category: 'Arts' },
    { code: '52112', title: 'Interior Designers', teer: 2, category: 'Arts' },
    { code: '52113', title: 'Theatre/Fashion Designers', teer: 2, category: 'Arts' },
    { code: '52119', title: 'Artisans/Craftspersons', teer: 2, category: 'Arts' },
    { code: '51100', title: 'Librarians', teer: 1, category: 'Arts' },
    { code: '51101', title: 'Archivists', teer: 1, category: 'Arts' },
    { code: '51102', title: 'Curators', teer: 1, category: 'Arts' },

    // Customer Service
    { code: '64409', title: 'Other Customer/Information Services', teer: 4, category: 'Service' },
    { code: '65100', title: 'Cashiers', teer: 5, category: 'Service' },
    { code: '65109', title: 'Other Sales Support', teer: 5, category: 'Service' },

    // Caregiving
    { code: '44100', title: 'Home Child Care Providers', teer: 4, category: 'Caregiving' },
    { code: '44101', title: 'Home Support Workers', teer: 4, category: 'Caregiving' },
    { code: '65220', title: 'Elementary/Secondary School Teacher Assistants', teer: 5, category: 'Caregiving' }
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

// Alternative Pathways - With conditions based on user profile
const ALTERNATIVE_PATHWAYS = [
    {
        id: 'study_pgwp_cec',
        name: 'Study → PGWP → CEC',
        description: 'Study in Canada for 2 years, get 3-year PGWP, work 1 year, apply via CEC',
        timeline: '3-4 years to PR',
        pros: ['Canadian education bonus', 'Canadian experience', 'Lower CRS competition'],
        cons: ['Tuition costs ($15-40k/year)', 'Longer timeline'],
        // Only show if they DON'T have Canadian education or PGWP already
        condition: ans => ans.education_country !== 'canada' && ans.canada_status !== 'work_open'
    },
    {
        id: 'cec_direct',
        name: 'Canadian Experience Class (CEC)',
        description: 'You already have PGWP and Canadian work experience - apply directly via Express Entry CEC',
        timeline: '6-8 months',
        pros: ['No minimum education', 'Canadian experience counts', 'No job offer required', 'Direct pathway'],
        cons: ['Need 1+ year Canadian skilled work experience', 'CLB 7 for TEER 0/1, CLB 5 for TEER 2/3'],
        // Show if they have PGWP/open work permit and Canadian experience
        condition: ans => ans.canada_status === 'work_open' && ans.canadian_experience && ans.canadian_experience !== 'none'
    },
    {
        id: 'aip',
        name: 'Atlantic Immigration Program (AIP)',
        description: 'Employer-driven program for NS, NB, PEI, NL - no CRS competition',
        timeline: '6-12 months',
        pros: ['No CRS needed', 'Fast processing', 'Employer support', 'Settlement plan included'],
        cons: ['Must stay in Atlantic Canada', 'Job offer required'],
        condition: ans => true // Always show
    },
    {
        id: 'rnip',
        name: 'Rural & Northern Immigration Pilot',
        description: 'Community-driven program for smaller towns and rural areas',
        timeline: '6-18 months',
        pros: ['Lower competition', 'Community support', 'Lower cost of living'],
        cons: ['Limited locations', 'Must stay in community 2+ years'],
        condition: ans => true // Always show
    },
    {
        id: 'bc_pnp_tech',
        name: 'BC PNP Tech',
        description: 'Fast-track for tech workers in BC with weekly draws and expedited processing',
        timeline: '3-6 months',
        pros: ['+600 CRS points', 'Weekly draws', 'No BC job offer required for some streams'],
        cons: ['Tech occupations only', 'Must intend to live in BC'],
        condition: ans => selectedOccupation?.category === 'STEM' || ans.field_of_study === 'tech'
    },
    {
        id: 'oinp_tech',
        name: 'Ontario OINP Tech Draw',
        description: 'Ontario targets tech workers through specific Express Entry draws',
        timeline: '4-8 months',
        pros: ['+600 CRS points', 'Access to Toronto job market', 'Strong tech sector'],
        cons: ['Tech occupations only', 'Competitive'],
        condition: ans => selectedOccupation?.category === 'STEM' || ans.field_of_study === 'tech'
    },
    {
        id: 'quebec_peg',
        name: 'Quebec Experience Program (PEQ)',
        description: 'For those who studied or worked in Quebec - French proficiency required',
        timeline: '6-12 months',
        pros: ['Faster than regular Quebec immigration', 'No points system', 'Study or work stream'],
        cons: ['French B2 required', 'Must stay in Quebec'],
        condition: ans => ans.target_province === 'quebec' || (ans.french_level && ans.french_level !== 'none')
    },
    {
        id: 'healthcare_draw',
        name: 'Healthcare Category Draw',
        description: 'Category-based Express Entry draws for healthcare workers with lower CRS cutoffs',
        timeline: '4-8 months',
        pros: ['Lower CRS cutoffs (400-450)', 'High demand occupation', 'No PNP needed'],
        cons: ['Healthcare occupations only', 'May need credential recognition'],
        condition: ans => selectedOccupation?.category === 'Healthcare' || ans.field_of_study === 'healthcare'
    },
    {
        id: 'trades_draw',
        name: 'Trade Occupations Category Draw',
        description: 'Category-based draws for skilled trades with lower CRS requirements',
        timeline: '4-8 months',
        pros: ['Lower CRS cutoffs', 'Red Seal advantage', 'High demand'],
        cons: ['Trade occupations only', 'May need certification'],
        condition: ans => selectedOccupation?.category === 'Trades' || ans.field_of_study === 'trades'
    },
    {
        id: 'french_draw',
        name: 'French Language Proficiency Draw',
        description: 'Category-based draws for French speakers with significantly lower CRS cutoffs',
        timeline: '4-8 months',
        pros: ['Very low CRS cutoffs (350-400)', 'Bonus CRS points for French', 'Less competitive'],
        cons: ['Need NCLC 7+ in French', 'May require French test'],
        condition: ans => ans.french_level === 'nclc7_plus' || ans.french_level === 'nclc5_6'
    },
    {
        id: 'startup_visa',
        name: 'Start-up Visa Program',
        description: 'For entrepreneurs with innovative business ideas supported by designated organizations',
        timeline: '12-18 months',
        pros: ['No CRS needed', 'Can bring business partners', 'Path to PR while building business'],
        cons: ['Need designated organization support', 'Business must be innovative', 'Competitive pitch process'],
        condition: ans => true // Always show as option
    },
    {
        id: 'self_employed',
        name: 'Self-Employed Persons Program',
        description: 'For those with experience in cultural activities, athletics, or farm management',
        timeline: '24-36 months',
        pros: ['No CRS needed', 'No job offer required', 'Self-employment focus'],
        cons: ['Very specific criteria', 'Long processing time', 'Cultural/athletic/farm experience required'],
        condition: ans => ans.field_of_study === 'arts' || ans.field_of_study === 'agriculture'
    },
    {
        id: 'caregiver',
        name: 'Home Child Care / Home Support Worker Pilots',
        description: 'Pathways for caregivers with Canadian work experience',
        timeline: '12-18 months',
        pros: ['No CRS needed', 'Clear pathway after 2 years work', 'Can bring family'],
        cons: ['Specific caregiver occupations only', 'Need 2 years Canadian experience'],
        condition: ans => selectedOccupation?.category === 'Caregiving' || selectedOccupation?.category === 'Healthcare'
    },
    {
        id: 'agri_food',
        name: 'Agri-Food Pilot',
        description: 'For workers in meat processing, mushroom/greenhouse crop production, and livestock',
        timeline: '12-18 months',
        pros: ['No CRS needed', 'TEER 4/5 eligible', 'Clear pathway to PR'],
        cons: ['Specific occupations only', 'Need 1 year Canadian experience', 'Specific industries'],
        condition: ans => selectedOccupation?.category === 'Agriculture' || ans.field_of_study === 'agriculture'
    }
];
