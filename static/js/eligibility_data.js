// RCIC-Style Eligibility Checker Data
// All questions, NOC database, and recommendation data

const QUESTIONS = [
    // Step 1: Personal Information (with lead capture)
    { id: 'email', category: 'Personal Information', step: 1,
      question: 'What is your email address?',
      type: 'email',
      placeholder: 'your@email.com',
      helpText: 'We\'ll send your personalized results and pathway recommendations to this email'
    },
    { id: 'phone', category: 'Personal Information', step: 1,
      question: 'What is your phone number? (Optional)',
      type: 'phone',
      placeholder: '+1 (555) 123-4567',
      optional: true,
      helpText: 'For priority updates on immigration draw alerts and deadline reminders'
    },
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
    { id: 'employment_status', category: 'Personal Information', step: 1,
      question: 'What is your current employment status?',
      options: [
        { value: 'employed_fulltime', label: 'Employed full-time' },
        { value: 'employed_parttime', label: 'Employed part-time' },
        { value: 'self_employed', label: 'Self-employed / Business owner' },
        { value: 'unemployed', label: 'Currently unemployed' },
        { value: 'student', label: 'Currently a student' },
        { value: 'retired', label: 'Retired' }
      ]
    },
    { id: 'dependents_count', category: 'Personal Information', step: 1,
      question: 'How many dependent children (under 22) do you have?',
      options: [
        { value: '0', label: 'No dependents' },
        { value: '1', label: '1 child' },
        { value: '2', label: '2 children' },
        { value: '3', label: '3 children' },
        { value: '4_plus', label: '4 or more children' }
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
    // Language test date & validity
    { id: 'english_test_date', category: 'Language Proficiency', step: 5,
      question: 'When did you take your English test?',
      condition: ans => ans.english_test && ans.english_test !== 'none',
      type: 'date',
      helpText: 'Language tests are valid for 2 years from the test date. We\'ll check if yours is still valid.'
    },
    { id: 'planning_to_improve_english', category: 'Language Proficiency', step: 5,
      question: 'Are you planning to retake your English test to improve your score?',
      condition: ans => ans.english_test && ans.english_test !== 'none',
      helpText: 'Higher language scores can add 20-50+ CRS points',
      options: [
        { value: 'yes_soon', label: 'Yes, within 3 months' },
        { value: 'yes_later', label: 'Yes, planning to eventually' },
        { value: 'no', label: 'No, satisfied with current score' }
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
    { id: 'job_salary', category: 'Job Offer', step: 6,
      question: 'What is the annual salary offered?',
      condition: ans => ans.job_offer === 'yes',
      type: 'salary',
      placeholder: 'e.g., 75000',
      helpText: 'Some PNP streams require minimum salary thresholds (e.g., BC PNP Tech needs median wage)'
    },
    { id: 'job_hours', category: 'Job Offer', step: 6,
      question: 'Is the job offer for full-time work (30+ hours/week)?',
      condition: ans => ans.job_offer === 'yes',
      options: [
        { value: 'fulltime', label: 'Yes, full-time (30+ hours/week)', desc: 'Required for most immigration programs' },
        { value: 'parttime', label: 'No, part-time', desc: 'May not qualify for CRS points' }
      ]
    },
    { id: 'job_permanent', category: 'Job Offer', step: 6,
      question: 'Is the job offer permanent or temporary?',
      condition: ans => ans.job_offer === 'yes',
      options: [
        { value: 'permanent', label: 'Permanent / Indeterminate', desc: 'Required for Express Entry points' },
        { value: 'contract', label: 'Fixed-term contract (1+ year)' },
        { value: 'temporary', label: 'Temporary / Seasonal', desc: 'May not qualify for points' }
      ]
    },
    { id: 'job_start_date', category: 'Job Offer', step: 6,
      question: 'When is your expected start date?',
      condition: ans => ans.job_offer === 'yes',
      options: [
        { value: 'already_working', label: 'Already working there' },
        { value: 'within_3_months', label: 'Within 3 months' },
        { value: '3_6_months', label: '3-6 months from now' },
        { value: 'over_6_months', label: 'More than 6 months away' }
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
    { id: 'funds_amount', category: 'Family & Financial', step: 7,
      question: 'Approximately how much do you have in liquid funds (CAD)?',
      type: 'funds',
      helpText: 'Bank balance + investments that can be liquidated',
      options: [
        { value: 'under_10k', label: 'Under $10,000 CAD' },
        { value: '10k_15k', label: '$10,000 - $15,000 CAD' },
        { value: '15k_25k', label: '$15,000 - $25,000 CAD' },
        { value: '25k_40k', label: '$25,000 - $40,000 CAD' },
        { value: '40k_60k', label: '$40,000 - $60,000 CAD' },
        { value: 'over_60k', label: 'Over $60,000 CAD' }
      ]
    },
    { id: 'funds_source', category: 'Family & Financial', step: 7,
      question: 'What is the main source of your settlement funds?',
      options: [
        { value: 'savings', label: 'Personal savings' },
        { value: 'salary', label: 'Current salary/income' },
        { value: 'property_sale', label: 'Property/asset sale' },
        { value: 'family_support', label: 'Family support' },
        { value: 'loan', label: 'Personal loan' },
        { value: 'investment', label: 'Investment returns' }
      ]
    },
    { id: 'bank_statements_ready', category: 'Family & Financial', step: 7,
      question: 'Do you have 6 months of recent bank statements available?',
      helpText: 'Required to prove your funds have been legitimately accumulated',
      options: [
        { value: 'yes_ready', label: 'Yes, ready to submit' },
        { value: 'partial', label: 'Some statements, not all 6 months' },
        { value: 'no', label: 'No, need to gather them' }
      ]
    },
    { id: 'documents_ready', category: 'Family & Financial', step: 7,
      question: 'Do you have these essential documents ready?',
      multiSelect: true,
      helpText: 'Select all documents you currently have',
      options: [
        { value: 'passport', label: 'Valid passport (6+ months remaining)' },
        { value: 'eca', label: 'Educational Credential Assessment (ECA)' },
        { value: 'language_test', label: 'Language test results' },
        { value: 'reference_letters', label: 'Employment reference letters' },
        { value: 'police_clearance', label: 'Police clearance certificate' },
        { value: 'medical', label: 'Medical exam completed' }
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
    { id: 'refusal_type', category: 'Admissibility', step: 9,
      question: 'What type of application was refused?',
      condition: ans => ans.previous_refusal === 'once' || ans.previous_refusal === 'multiple',
      options: [
        { value: 'visitor', label: 'Visitor Visa / TRV' },
        { value: 'study', label: 'Study Permit' },
        { value: 'work', label: 'Work Permit' },
        { value: 'pr', label: 'Permanent Residence' },
        { value: 'multiple_types', label: 'Multiple types' }
      ]
    },
    { id: 'refusal_reason', category: 'Admissibility', step: 9,
      question: 'What was the main reason for refusal?',
      condition: ans => ans.previous_refusal === 'once' || ans.previous_refusal === 'multiple',
      helpText: 'Knowing the reason helps identify if it\'s been resolved',
      options: [
        { value: 'funds', label: 'Insufficient funds', desc: 'Financial documentation issues' },
        { value: 'ties', label: 'Insufficient ties to home country', desc: 'Dual intent concerns' },
        { value: 'purpose', label: 'Purpose of travel not clear' },
        { value: 'incomplete', label: 'Incomplete application' },
        { value: 'misrep', label: 'Misrepresentation concern', desc: 'Serious - may require legal help' },
        { value: 'not_sure', label: 'Not sure / GCMS not ordered' }
      ]
    },
    { id: 'refusal_recency', category: 'Admissibility', step: 9,
      question: 'When was your most recent refusal?',
      condition: ans => ans.previous_refusal === 'once' || ans.previous_refusal === 'multiple',
      options: [
        { value: 'within_1_year', label: 'Within the last year' },
        { value: '1_2_years', label: '1-2 years ago' },
        { value: '2_5_years', label: '2-5 years ago' },
        { value: 'over_5_years', label: 'Over 5 years ago' }
      ]
    },
    { id: 'other_country_refusal', category: 'Admissibility', step: 9,
      question: 'Have you been refused a visa to any OTHER country (USA, UK, Australia, etc.)?',
      helpText: 'Canada shares biometric data with the "Migration 5" countries (US, UK, Australia, NZ)',
      options: [
        { value: 'no', label: 'No, never refused by any country' },
        { value: 'usa', label: 'Yes, USA' },
        { value: 'uk', label: 'Yes, UK' },
        { value: 'australia', label: 'Yes, Australia/NZ' },
        { value: 'schengen', label: 'Yes, Schengen/EU' },
        { value: 'multiple', label: 'Yes, multiple countries' }
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
        { value: 'dui', label: 'DUI / Impaired driving only', desc: 'Most common inadmissibility issue' },
        { value: 'minor', label: 'Minor offense (non-DUI)', desc: 'Theft, minor assault, etc.' },
        { value: 'serious', label: 'Serious offense', desc: 'Fraud, major assault, etc.' }
      ]
    },
    { id: 'dui_details', category: 'Admissibility', step: 9,
      question: 'How long ago was your DUI conviction?',
      condition: ans => ans.criminal_history === 'dui',
      helpText: 'DUI is a serious crime in Canada. Time since conviction affects rehabilitation options.',
      options: [
        { value: 'under_5', label: 'Less than 5 years ago', desc: 'May need TRP (Temporary Resident Permit)' },
        { value: '5_10', label: '5-10 years ago', desc: 'May qualify for Criminal Rehabilitation' },
        { value: 'over_10', label: 'Over 10 years ago', desc: 'May be "deemed rehabilitated"' }
      ]
    },
    { id: 'dui_sentence', category: 'Admissibility', step: 9,
      question: 'What was your DUI sentence?',
      condition: ans => ans.criminal_history === 'dui',
      options: [
        { value: 'fine_only', label: 'Fine only (no jail)', desc: 'Better rehabilitation chances' },
        { value: 'suspended', label: 'Suspended sentence', desc: 'Probation without jail time' },
        { value: 'jail_under_6', label: 'Less than 6 months jail' },
        { value: 'jail_over_6', label: '6+ months jail', desc: 'Serious inadmissibility concern' }
      ]
    },
    { id: 'rehabilitation_status', category: 'Admissibility', step: 9,
      question: 'Have you applied for Criminal Rehabilitation?',
      condition: ans => ans.criminal_history === 'dui' || ans.criminal_history === 'minor' || ans.criminal_history === 'serious',
      helpText: 'Criminal Rehabilitation removes inadmissibility permanently if approved',
      options: [
        { value: 'approved', label: 'Yes, approved', desc: 'You are no longer inadmissible' },
        { value: 'pending', label: 'Applied, waiting for decision' },
        { value: 'not_applied', label: 'Not applied yet' },
        { value: 'not_eligible', label: 'Not yet eligible (under 5 years)' }
      ]
    },
    { id: 'misrepresentation', category: 'Admissibility', step: 9,
      question: 'Have you ever been found guilty of misrepresentation to IRCC?',
      helpText: 'Misrepresentation results in a 5-year ban from Canada',
      options: [
        { value: 'no', label: 'No, never' },
        { value: 'yes_over_5', label: 'Yes, but over 5 years ago', desc: 'Ban has expired' },
        { value: 'yes_under_5', label: 'Yes, within last 5 years', desc: 'Still banned - wait required' }
      ]
    },
    { id: 'removal_order', category: 'Admissibility', step: 9,
      question: 'Have you ever been issued a removal order from Canada?',
      options: [
        { value: 'no', label: 'No, never removed from Canada' },
        { value: 'departure', label: 'Departure order (left voluntarily)' },
        { value: 'exclusion', label: 'Exclusion order', desc: '1-year ban' },
        { value: 'deportation', label: 'Deportation order', desc: 'Permanent ban without ARC' }
      ]
    },

    // Step 10: Family Sponsorship Screening (NEW)
    { id: 'canadian_spouse', category: 'Family Sponsorship', step: 10,
      question: 'Do you have a spouse or common-law partner who is a Canadian citizen or PR?',
      helpText: 'Spousal sponsorship is one of the fastest pathways to PR',
      options: [
        { value: 'yes_citizen', label: 'Yes, Canadian citizen', desc: 'Can sponsor from inside or outside Canada' },
        { value: 'yes_pr', label: 'Yes, Permanent Resident', desc: 'Must meet income requirements' },
        { value: 'no', label: 'No' }
      ]
    },
    { id: 'spouse_in_canada', category: 'Family Sponsorship', step: 10,
      question: 'Are you currently living with your Canadian spouse in Canada?',
      condition: ans => ans.canadian_spouse === 'yes_citizen' || ans.canadian_spouse === 'yes_pr',
      options: [
        { value: 'yes', label: 'Yes, living together in Canada', desc: 'Inland sponsorship + Open Work Permit' },
        { value: 'no', label: 'No, spouse is in Canada but I am not', desc: 'Outland sponsorship available' }
      ]
    },
    { id: 'relationship_duration', category: 'Family Sponsorship', step: 10,
      question: 'How long have you been in this relationship?',
      condition: ans => ans.canadian_spouse === 'yes_citizen' || ans.canadian_spouse === 'yes_pr',
      helpText: 'IRCC assesses genuineness of relationship',
      options: [
        { value: 'under_1', label: 'Less than 1 year' },
        { value: '1_2', label: '1-2 years' },
        { value: '2_5', label: '2-5 years' },
        { value: 'over_5', label: 'Over 5 years' }
      ]
    },
    { id: 'relationship_evidence', category: 'Family Sponsorship', step: 10,
      question: 'What evidence do you have of your relationship?',
      condition: ans => ans.canadian_spouse === 'yes_citizen' || ans.canadian_spouse === 'yes_pr',
      multiSelect: true,
      options: [
        { value: 'marriage_cert', label: 'Marriage certificate' },
        { value: 'cohabitation', label: 'Proof of cohabitation (lease, bills)' },
        { value: 'joint_accounts', label: 'Joint bank accounts' },
        { value: 'photos', label: 'Photos together over time' },
        { value: 'travel', label: 'Travel together' },
        { value: 'children', label: 'Children together' }
      ]
    },
    { id: 'pgp_interest', category: 'Family Sponsorship', step: 10,
      question: 'Are you interested in sponsoring your parents/grandparents to Canada?',
      helpText: 'Parent and Grandparent Program (PGP) has annual lottery',
      options: [
        { value: 'yes', label: 'Yes, interested in PGP' },
        { value: 'super_visa', label: 'Maybe Super Visa instead', desc: '10-year multiple entry visa' },
        { value: 'no', label: 'No / Not applicable' }
      ]
    },

    // Goals & Timeline (was step 9, now step 11)
    { id: 'primary_goal', category: 'Goals & Timeline', step: 11,
      question: 'What is your primary immigration goal?',
      options: [
        { value: 'pr_fast', label: 'Permanent Residence ASAP' },
        { value: 'work_then_pr', label: 'Work first, then PR' },
        { value: 'study_then_pr', label: 'Study first, then work & PR' },
        { value: 'not_sure', label: 'Not sure - need guidance' }
      ]
    }
];

// Official NOC 2021 Database - All 516 Unit Groups
// Source: Statistics Canada NOC 2021 Version 1.0
// https://www.statcan.gc.ca/en/subjects/standard/noc/2021/indexV1
const NOC_DATABASE = [
    { code: '00010', title: 'Legislators', teer: 0, category: 'Management' },
    { code: '00011', title: 'Senior government managers and officials', teer: 0, category: 'Management' },
    { code: '00012', title: 'Senior managers - financial, communications and other business services', teer: 0, category: 'Management' },
    { code: '00013', title: 'Senior managers - health, education, social and community services and membership organizations', teer: 0, category: 'Management' },
    { code: '00014', title: 'Senior managers - trade, broadcasting and other services', teer: 0, category: 'Management' },
    { code: '00015', title: 'Senior managers - construction, transportation, production and utilities', teer: 0, category: 'Management' },
    { code: '10010', title: 'Financial managers', teer: 0, category: 'Business' },
    { code: '10011', title: 'Human resources managers', teer: 0, category: 'Business' },
    { code: '10012', title: 'Purchasing managers', teer: 0, category: 'Business' },
    { code: '10019', title: 'Other administrative services managers', teer: 0, category: 'Business' },
    { code: '10020', title: 'Insurance, real estate and financial brokerage managers', teer: 0, category: 'Business' },
    { code: '10021', title: 'Banking, credit and other investment managers', teer: 0, category: 'Business' },
    { code: '10022', title: 'Advertising, marketing and public relations managers', teer: 0, category: 'Business' },
    { code: '10029', title: 'Other business services managers', teer: 0, category: 'Business' },
    { code: '10030', title: 'Telecommunication carriers managers', teer: 0, category: 'Business' },
    { code: '11100', title: 'Financial auditors and accountants', teer: 1, category: 'Business' },
    { code: '11101', title: 'Financial and investment analysts', teer: 1, category: 'Business' },
    { code: '11102', title: 'Financial advisors', teer: 1, category: 'Business' },
    { code: '11103', title: 'Securities agents, investment dealers and brokers', teer: 1, category: 'Business' },
    { code: '11109', title: 'Other financial officers', teer: 1, category: 'Business' },
    { code: '11200', title: 'Human resources professionals', teer: 1, category: 'Business' },
    { code: '11201', title: 'Professional occupations in business management consulting', teer: 1, category: 'Business' },
    { code: '11202', title: 'Professional occupations in advertising, marketing and public relations', teer: 1, category: 'Business' },
    { code: '12010', title: 'Supervisors, general office and administrative support workers', teer: 2, category: 'Business' },
    { code: '12011', title: 'Supervisors, finance and insurance office workers', teer: 2, category: 'Business' },
    { code: '12012', title: 'Supervisors, library, correspondence and related information workers', teer: 2, category: 'Business' },
    { code: '12013', title: 'Supervisors, supply chain, tracking and scheduling coordination occupations', teer: 2, category: 'Business' },
    { code: '12100', title: 'Executive assistants', teer: 2, category: 'Business' },
    { code: '12101', title: 'Human resources and recruitment officers', teer: 2, category: 'Business' },
    { code: '12102', title: 'Procurement and purchasing agents and officers', teer: 2, category: 'Business' },
    { code: '12103', title: 'Conference and event planners', teer: 2, category: 'Business' },
    { code: '12104', title: 'Employment insurance and revenue officers', teer: 2, category: 'Business' },
    { code: '12110', title: 'Court reporters, medical transcriptionists and related occupations', teer: 2, category: 'Business' },
    { code: '12111', title: 'Health information management occupations', teer: 2, category: 'Business' },
    { code: '12112', title: 'Records management technicians', teer: 2, category: 'Business' },
    { code: '12113', title: 'Statistical officers and related research support occupations', teer: 2, category: 'Business' },
    { code: '12200', title: 'Accounting technicians and bookkeepers', teer: 2, category: 'Business' },
    { code: '12201', title: 'Insurance adjusters and claims examiners', teer: 2, category: 'Business' },
    { code: '12202', title: 'Insurance underwriters', teer: 2, category: 'Business' },
    { code: '12203', title: 'Assessors, business valuators and appraisers', teer: 2, category: 'Business' },
    { code: '13100', title: 'Administrative officers', teer: 3, category: 'Business' },
    { code: '13101', title: 'Property administrators', teer: 3, category: 'Business' },
    { code: '13102', title: 'Payroll administrators', teer: 3, category: 'Business' },
    { code: '13110', title: 'Administrative assistants', teer: 3, category: 'Business' },
    { code: '13111', title: 'Legal administrative assistants', teer: 3, category: 'Business' },
    { code: '13112', title: 'Medical administrative assistants', teer: 3, category: 'Business' },
    { code: '13200', title: 'Customs, ship and other brokers', teer: 3, category: 'Business' },
    { code: '13201', title: 'Production and transportation logistics coordinators', teer: 3, category: 'Business' },
    { code: '14100', title: 'General office support workers', teer: 4, category: 'Business' },
    { code: '14101', title: 'Receptionists', teer: 4, category: 'Business' },
    { code: '14102', title: 'Personnel clerks', teer: 4, category: 'Business' },
    { code: '14103', title: 'Court clerks and related court services occupations', teer: 4, category: 'Business' },
    { code: '14110', title: 'Survey interviewers and statistical clerks', teer: 4, category: 'Business' },
    { code: '14111', title: 'Data entry clerks', teer: 4, category: 'Business' },
    { code: '14112', title: 'Desktop publishing operators and related occupations', teer: 4, category: 'Business' },
    { code: '14200', title: 'Accounting and related clerks', teer: 4, category: 'Business' },
    { code: '14201', title: 'Banking, insurance and other financial clerks', teer: 4, category: 'Business' },
    { code: '14202', title: 'Collection clerks', teer: 4, category: 'Business' },
    { code: '14300', title: 'Library assistants and clerks', teer: 4, category: 'Business' },
    { code: '14301', title: 'Correspondence, publication and regulatory clerks', teer: 4, category: 'Business' },
    { code: '14400', title: 'Shippers and receivers', teer: 4, category: 'Business' },
    { code: '14401', title: 'Storekeepers and partspersons', teer: 4, category: 'Business' },
    { code: '14402', title: 'Production logistics workers', teer: 4, category: 'Business' },
    { code: '14403', title: 'Purchasing and inventory control workers', teer: 4, category: 'Business' },
    { code: '14404', title: 'Dispatchers', teer: 4, category: 'Business' },
    { code: '14405', title: 'Transportation route and crew schedulers', teer: 4, category: 'Business' },
    { code: '20010', title: 'Engineering managers', teer: 0, category: 'STEM' },
    { code: '20011', title: 'Architecture and science managers', teer: 0, category: 'STEM' },
    { code: '20012', title: 'Computer and information systems managers', teer: 0, category: 'STEM' },
    { code: '21100', title: 'Physicists and astronomers', teer: 1, category: 'STEM' },
    { code: '21101', title: 'Chemists', teer: 1, category: 'STEM' },
    { code: '21102', title: 'Geoscientists and oceanographers', teer: 1, category: 'STEM' },
    { code: '21103', title: 'Meteorologists and climatologists', teer: 1, category: 'STEM' },
    { code: '21109', title: 'Other professional occupations in physical sciences', teer: 1, category: 'STEM' },
    { code: '21110', title: 'Biologists and related scientists', teer: 1, category: 'STEM' },
    { code: '21111', title: 'Forestry professionals', teer: 1, category: 'STEM' },
    { code: '21112', title: 'Agricultural representatives, consultants and specialists', teer: 1, category: 'STEM' },
    { code: '21120', title: 'Public and environmental health and safety professionals', teer: 1, category: 'STEM' },
    { code: '21200', title: 'Architects', teer: 1, category: 'STEM' },
    { code: '21201', title: 'Landscape architects', teer: 1, category: 'STEM' },
    { code: '21202', title: 'Urban and land use planners', teer: 1, category: 'STEM' },
    { code: '21203', title: 'Land surveyors', teer: 1, category: 'STEM' },
    { code: '21210', title: 'Mathematicians, statisticians and actuaries', teer: 1, category: 'STEM' },
    { code: '21211', title: 'Data scientists', teer: 1, category: 'STEM' },
    { code: '21220', title: 'Cybersecurity specialists', teer: 1, category: 'STEM' },
    { code: '21221', title: 'Business systems specialists', teer: 1, category: 'STEM' },
    { code: '21222', title: 'Information systems specialists', teer: 1, category: 'STEM' },
    { code: '21223', title: 'Database analysts and data administrators', teer: 1, category: 'STEM' },
    { code: '21230', title: 'Computer systems developers and programmers', teer: 1, category: 'STEM' },
    { code: '21231', title: 'Software engineers and designers', teer: 1, category: 'STEM' },
    { code: '21232', title: 'Software developers and programmers', teer: 1, category: 'STEM' },
    { code: '21233', title: 'Web designers', teer: 1, category: 'STEM' },
    { code: '21234', title: 'Web developers and programmers', teer: 1, category: 'STEM' },
    { code: '21300', title: 'Civil engineers', teer: 1, category: 'STEM' },
    { code: '21301', title: 'Mechanical engineers', teer: 1, category: 'STEM' },
    { code: '21310', title: 'Electrical and electronics engineers', teer: 1, category: 'STEM' },
    { code: '21311', title: 'Computer engineers (except software engineers and designers)', teer: 1, category: 'STEM' },
    { code: '21320', title: 'Chemical engineers', teer: 1, category: 'STEM' },
    { code: '21321', title: 'Industrial and manufacturing engineers', teer: 1, category: 'STEM' },
    { code: '21322', title: 'Metallurgical and materials engineers', teer: 1, category: 'STEM' },
    { code: '21330', title: 'Mining engineers', teer: 1, category: 'STEM' },
    { code: '21331', title: 'Geological engineers', teer: 1, category: 'STEM' },
    { code: '21332', title: 'Petroleum engineers', teer: 1, category: 'STEM' },
    { code: '21390', title: 'Aerospace engineers', teer: 1, category: 'STEM' },
    { code: '21399', title: 'Other professional engineers', teer: 1, category: 'STEM' },
    { code: '22100', title: 'Chemical technologists and technicians', teer: 2, category: 'STEM' },
    { code: '22101', title: 'Geological and mineral technologists and technicians', teer: 2, category: 'STEM' },
    { code: '22110', title: 'Biological technologists and technicians', teer: 2, category: 'STEM' },
    { code: '22111', title: 'Agricultural and fish products inspectors', teer: 2, category: 'STEM' },
    { code: '22112', title: 'Forestry technologists and technicians', teer: 2, category: 'STEM' },
    { code: '22113', title: 'Conservation and fishery officers', teer: 2, category: 'STEM' },
    { code: '22114', title: 'Landscape and horticulture technicians and specialists', teer: 2, category: 'STEM' },
    { code: '22210', title: 'Architectural technologists and technicians', teer: 2, category: 'STEM' },
    { code: '22211', title: 'Industrial designers', teer: 2, category: 'STEM' },
    { code: '22212', title: 'Drafting technologists and technicians', teer: 2, category: 'STEM' },
    { code: '22213', title: 'Land survey technologists and technicians', teer: 2, category: 'STEM' },
    { code: '22214', title: 'Technical occupations in geomatics and meteorology', teer: 2, category: 'STEM' },
    { code: '22220', title: 'Computer network and web technicians', teer: 2, category: 'STEM' },
    { code: '22221', title: 'User support technicians', teer: 2, category: 'STEM' },
    { code: '22222', title: 'Information systems testing technicians', teer: 2, category: 'STEM' },
    { code: '22230', title: 'Non-destructive testers and inspectors', teer: 2, category: 'STEM' },
    { code: '22231', title: 'Engineering inspectors and regulatory officers', teer: 2, category: 'STEM' },
    { code: '22232', title: 'Occupational health and safety specialists', teer: 2, category: 'STEM' },
    { code: '22233', title: 'Construction inspectors', teer: 2, category: 'STEM' },
    { code: '22300', title: 'Civil engineering technologists and technicians', teer: 2, category: 'STEM' },
    { code: '22301', title: 'Mechanical engineering technologists and technicians', teer: 2, category: 'STEM' },
    { code: '22302', title: 'Industrial engineering and manufacturing technologists and technicians', teer: 2, category: 'STEM' },
    { code: '22303', title: 'Construction estimators', teer: 2, category: 'STEM' },
    { code: '22310', title: 'Electrical and electronics engineering technologists and technicians', teer: 2, category: 'STEM' },
    { code: '22311', title: 'Electronic service technicians (household and business equipment)', teer: 2, category: 'STEM' },
    { code: '22312', title: 'Industrial instrument technicians and mechanics', teer: 2, category: 'STEM' },
    { code: '22313', title: 'Aircraft instrument, electrical and avionics mechanics, technicians and inspectors', teer: 2, category: 'STEM' },
    { code: '30010', title: 'Managers in health care', teer: 0, category: 'Healthcare' },
    { code: '31100', title: 'Specialists in clinical and laboratory medicine', teer: 1, category: 'Healthcare' },
    { code: '31101', title: 'Specialists in surgery', teer: 1, category: 'Healthcare' },
    { code: '31102', title: 'General practitioners and family physicians', teer: 1, category: 'Healthcare' },
    { code: '31103', title: 'Veterinarians', teer: 1, category: 'Healthcare' },
    { code: '31110', title: 'Dentists', teer: 1, category: 'Healthcare' },
    { code: '31111', title: 'Optometrists', teer: 1, category: 'Healthcare' },
    { code: '31112', title: 'Audiologists and speech-language pathologists', teer: 1, category: 'Healthcare' },
    { code: '31120', title: 'Pharmacists', teer: 1, category: 'Healthcare' },
    { code: '31121', title: 'Dietitians and nutritionists', teer: 1, category: 'Healthcare' },
    { code: '31200', title: 'Psychologists', teer: 1, category: 'Healthcare' },
    { code: '31201', title: 'Chiropractors', teer: 1, category: 'Healthcare' },
    { code: '31202', title: 'Physiotherapists', teer: 1, category: 'Healthcare' },
    { code: '31203', title: 'Occupational therapists', teer: 1, category: 'Healthcare' },
    { code: '31204', title: 'Kinesiologists and other professional occupations in therapy and assessment', teer: 1, category: 'Healthcare' },
    { code: '31209', title: 'Other professional occupations in health diagnosing and treating', teer: 1, category: 'Healthcare' },
    { code: '31300', title: 'Nursing coordinators and supervisors', teer: 1, category: 'Healthcare' },
    { code: '31301', title: 'Registered nurses and registered psychiatric nurses', teer: 1, category: 'Healthcare' },
    { code: '31302', title: 'Nurse practitioners', teer: 1, category: 'Healthcare' },
    { code: '31303', title: 'Physician assistants, midwives and allied health professionals', teer: 1, category: 'Healthcare' },
    { code: '32100', title: 'Opticians', teer: 2, category: 'Healthcare' },
    { code: '32101', title: 'Licensed practical nurses', teer: 2, category: 'Healthcare' },
    { code: '32102', title: 'Paramedical occupations', teer: 2, category: 'Healthcare' },
    { code: '32103', title: 'Respiratory therapists, clinical perfusionists and cardiopulmonary technologists', teer: 2, category: 'Healthcare' },
    { code: '32104', title: 'Animal health technologists and veterinary technicians', teer: 2, category: 'Healthcare' },
    { code: '32109', title: 'Other technical occupations in therapy and assessment', teer: 2, category: 'Healthcare' },
    { code: '32110', title: 'Denturists', teer: 2, category: 'Healthcare' },
    { code: '32111', title: 'Dental hygienists and dental therapists', teer: 2, category: 'Healthcare' },
    { code: '32112', title: 'Dental technologists and technicians', teer: 2, category: 'Healthcare' },
    { code: '32120', title: 'Medical laboratory technologists', teer: 2, category: 'Healthcare' },
    { code: '32121', title: 'Medical radiation technologists', teer: 2, category: 'Healthcare' },
    { code: '32122', title: 'Medical sonographers', teer: 2, category: 'Healthcare' },
    { code: '32123', title: 'Cardiology technologists and electrophysiological diagnostic technologists', teer: 2, category: 'Healthcare' },
    { code: '32124', title: 'Pharmacy technicians', teer: 2, category: 'Healthcare' },
    { code: '32129', title: 'Other medical technologists and technicians', teer: 2, category: 'Healthcare' },
    { code: '32200', title: 'Traditional Chinese medicine practitioners and acupuncturists', teer: 2, category: 'Healthcare' },
    { code: '32201', title: 'Massage therapists', teer: 2, category: 'Healthcare' },
    { code: '32209', title: 'Other practitioners of natural healing', teer: 2, category: 'Healthcare' },
    { code: '33100', title: 'Dental assistants and dental laboratory assistants', teer: 3, category: 'Healthcare' },
    { code: '33101', title: 'Medical laboratory assistants and related technical occupations', teer: 3, category: 'Healthcare' },
    { code: '33102', title: 'Nurse aides, orderlies and patient service associates', teer: 3, category: 'Healthcare' },
    { code: '33103', title: 'Pharmacy technical assistants and pharmacy assistants', teer: 3, category: 'Healthcare' },
    { code: '33109', title: 'Other assisting occupations in support of health services', teer: 3, category: 'Healthcare' },
    { code: '40010', title: 'Government managers - health and social policy development and program administration', teer: 0, category: 'Education' },
    { code: '40011', title: 'Government managers - economic analysis, policy development and program administration', teer: 0, category: 'Education' },
    { code: '40012', title: 'Government managers - education policy development and program administration', teer: 0, category: 'Education' },
    { code: '40019', title: 'Other managers in public administration', teer: 0, category: 'Education' },
    { code: '40020', title: 'Administrators - post-secondary education and vocational training', teer: 0, category: 'Education' },
    { code: '40021', title: 'School principals and administrators of elementary and secondary education', teer: 0, category: 'Education' },
    { code: '40030', title: 'Managers in social, community and correctional services', teer: 0, category: 'Education' },
    { code: '40040', title: 'Commissioned police officers and related occupations in public protection services', teer: 0, category: 'Education' },
    { code: '40041', title: 'Fire chiefs and senior firefighting officers', teer: 0, category: 'Education' },
    { code: '40042', title: 'Commissioned officers of the Canadian Armed Forces', teer: 0, category: 'Education' },
    { code: '41100', title: 'Judges', teer: 1, category: 'Education' },
    { code: '41101', title: 'Lawyers and Quebec notaries', teer: 1, category: 'Education' },
    { code: '41200', title: 'University professors and lecturers', teer: 1, category: 'Education' },
    { code: '41201', title: 'Post-secondary teaching and research assistants', teer: 1, category: 'Education' },
    { code: '41210', title: 'College and other vocational instructors', teer: 1, category: 'Education' },
    { code: '41220', title: 'Secondary school teachers', teer: 1, category: 'Education' },
    { code: '41221', title: 'Elementary school and kindergarten teachers', teer: 1, category: 'Education' },
    { code: '41300', title: 'Social workers', teer: 1, category: 'Education' },
    { code: '41301', title: 'Therapists in counselling and related specialized therapies', teer: 1, category: 'Education' },
    { code: '41302', title: 'Religious leaders', teer: 1, category: 'Education' },
    { code: '41310', title: 'Police investigators and other investigative occupations', teer: 1, category: 'Education' },
    { code: '41311', title: 'Probation and parole officers', teer: 1, category: 'Education' },
    { code: '41320', title: 'Educational counsellors', teer: 1, category: 'Education' },
    { code: '41321', title: 'Career development practitioners and career counsellors (except education)', teer: 1, category: 'Education' },
    { code: '41400', title: 'Natural and applied science policy researchers, consultants and program officers', teer: 1, category: 'Education' },
    { code: '41401', title: 'Economists and economic policy researchers and analysts', teer: 1, category: 'Education' },
    { code: '41402', title: 'Business development officers and market researchers and analysts', teer: 1, category: 'Education' },
    { code: '41403', title: 'Social policy researchers, consultants and program officers', teer: 1, category: 'Education' },
    { code: '41404', title: 'Health policy researchers, consultants and program officers', teer: 1, category: 'Education' },
    { code: '41405', title: 'Education policy researchers, consultants and program officers', teer: 1, category: 'Education' },
    { code: '41406', title: 'Recreation, sports and fitness policy researchers, consultants and program officers', teer: 1, category: 'Education' },
    { code: '41407', title: 'Program officers unique to government', teer: 1, category: 'Education' },
    { code: '41409', title: 'Other professional occupations in social science', teer: 1, category: 'Education' },
    { code: '42100', title: 'Police officers (except commissioned)', teer: 2, category: 'Education' },
    { code: '42101', title: 'Firefighters', teer: 2, category: 'Education' },
    { code: '42102', title: 'Specialized members of the Canadian Armed Forces', teer: 2, category: 'Education' },
    { code: '42200', title: 'Paralegals and related occupations', teer: 2, category: 'Education' },
    { code: '42201', title: 'Social and community service workers', teer: 2, category: 'Education' },
    { code: '42202', title: 'Early childhood educators and assistants', teer: 2, category: 'Education' },
    { code: '42203', title: 'Instructors of persons with disabilities', teer: 2, category: 'Education' },
    { code: '42204', title: 'Religion workers', teer: 2, category: 'Education' },
    { code: '43100', title: 'Elementary and secondary school teacher assistants', teer: 3, category: 'Education' },
    { code: '43109', title: 'Other instructors', teer: 3, category: 'Education' },
    { code: '43200', title: 'Sheriffs and bailiffs', teer: 3, category: 'Education' },
    { code: '43201', title: 'Correctional service officers', teer: 3, category: 'Education' },
    { code: '43202', title: 'By-law enforcement and other regulatory officers', teer: 3, category: 'Education' },
    { code: '43203', title: 'Border services, customs, and immigration officers', teer: 3, category: 'Education' },
    { code: '43204', title: 'Operations members of the Canadian Armed Forces', teer: 3, category: 'Education' },
    { code: '44100', title: 'Home child care providers', teer: 4, category: 'Education' },
    { code: '44101', title: 'Home support workers, caregivers and related occupations', teer: 4, category: 'Education' },
    { code: '44200', title: 'Primary combat members of the Canadian Armed Forces', teer: 4, category: 'Education' },
    { code: '45100', title: 'Student monitors, crossing guards and related occupations', teer: 5, category: 'Education' },
    { code: '50010', title: 'Library, archive, museum and art gallery managers', teer: 0, category: 'Arts' },
    { code: '50011', title: 'Managers - publishing, motion pictures, broadcasting and performing arts', teer: 0, category: 'Arts' },
    { code: '50012', title: 'Recreation, sports and fitness program and service directors', teer: 0, category: 'Arts' },
    { code: '51100', title: 'Librarians', teer: 1, category: 'Arts' },
    { code: '51101', title: 'Conservators and curators', teer: 1, category: 'Arts' },
    { code: '51102', title: 'Archivists', teer: 1, category: 'Arts' },
    { code: '51110', title: 'Editors', teer: 1, category: 'Arts' },
    { code: '51111', title: 'Authors and writers (except technical)', teer: 1, category: 'Arts' },
    { code: '51112', title: 'Technical writers', teer: 1, category: 'Arts' },
    { code: '51113', title: 'Journalists', teer: 1, category: 'Arts' },
    { code: '51114', title: 'Translators, terminologists and interpreters', teer: 1, category: 'Arts' },
    { code: '51120', title: 'Producers, directors, choreographers and related occupations', teer: 1, category: 'Arts' },
    { code: '51121', title: 'Conductors, composers and arrangers', teer: 1, category: 'Arts' },
    { code: '51122', title: 'Musicians and singers', teer: 1, category: 'Arts' },
    { code: '52100', title: 'Library and public archive technicians', teer: 2, category: 'Arts' },
    { code: '52110', title: 'Film and video camera operators', teer: 2, category: 'Arts' },
    { code: '52111', title: 'Graphic arts technicians', teer: 2, category: 'Arts' },
    { code: '52112', title: 'Broadcast technicians', teer: 2, category: 'Arts' },
    { code: '52113', title: 'Audio and video recording technicians', teer: 2, category: 'Arts' },
    { code: '52114', title: 'Announcers and other broadcasters', teer: 2, category: 'Arts' },
    { code: '52119', title: 'Other technical and coordinating occupations in motion pictures, broadcasting and the performing arts', teer: 2, category: 'Arts' },
    { code: '52120', title: 'Graphic designers and illustrators', teer: 2, category: 'Arts' },
    { code: '52121', title: 'Interior designers and interior decorators', teer: 2, category: 'Arts' },
    { code: '53100', title: 'Registrars, restorers, interpreters and other occupations related to museum and art galleries', teer: 3, category: 'Arts' },
    { code: '53110', title: 'Photographers', teer: 3, category: 'Arts' },
    { code: '53111', title: 'Motion pictures, broadcasting, photography and performing arts assistants and operators', teer: 3, category: 'Arts' },
    { code: '53120', title: 'Dancers', teer: 3, category: 'Arts' },
    { code: '53121', title: 'Actors, comedians and circus performers', teer: 3, category: 'Arts' },
    { code: '53122', title: 'Painters, sculptors and other visual artists', teer: 3, category: 'Arts' },
    { code: '53123', title: 'Theatre, fashion, exhibit and other creative designers', teer: 3, category: 'Arts' },
    { code: '53124', title: 'Artisans and craftspersons', teer: 3, category: 'Arts' },
    { code: '53125', title: 'Patternmakers - textile, leather and fur products', teer: 3, category: 'Arts' },
    { code: '53200', title: 'Athletes', teer: 3, category: 'Arts' },
    { code: '53201', title: 'Coaches', teer: 3, category: 'Arts' },
    { code: '53202', title: 'Sports officials and referees', teer: 3, category: 'Arts' },
    { code: '54100', title: 'Program leaders and instructors in recreation, sport and fitness', teer: 4, category: 'Arts' },
    { code: '55109', title: 'Other performers', teer: 5, category: 'Arts' },
    { code: '60010', title: 'Corporate sales managers', teer: 0, category: 'Sales' },
    { code: '60020', title: 'Retail and wholesale trade managers', teer: 0, category: 'Sales' },
    { code: '60030', title: 'Restaurant and food service managers', teer: 0, category: 'Sales' },
    { code: '60031', title: 'Accommodation service managers', teer: 0, category: 'Sales' },
    { code: '60040', title: 'Managers in customer and personal services', teer: 0, category: 'Sales' },
    { code: '62010', title: 'Retail sales supervisors', teer: 2, category: 'Sales' },
    { code: '62020', title: 'Food service supervisors', teer: 2, category: 'Sales' },
    { code: '62021', title: 'Executive housekeepers', teer: 2, category: 'Sales' },
    { code: '62022', title: 'Accommodation, travel, tourism and related services supervisors', teer: 2, category: 'Sales' },
    { code: '62023', title: 'Customer and information services supervisors', teer: 2, category: 'Sales' },
    { code: '62024', title: 'Cleaning supervisors', teer: 2, category: 'Sales' },
    { code: '62029', title: 'Other services supervisors', teer: 2, category: 'Sales' },
    { code: '62100', title: 'Technical sales specialists - wholesale trade', teer: 2, category: 'Sales' },
    { code: '62101', title: 'Retail and wholesale buyers', teer: 2, category: 'Sales' },
    { code: '62200', title: 'Chefs', teer: 2, category: 'Sales' },
    { code: '62201', title: 'Funeral directors and embalmers', teer: 2, category: 'Sales' },
    { code: '62202', title: 'Jewellers, jewellery and watch repairers and related occupations', teer: 2, category: 'Sales' },
    { code: '63100', title: 'Insurance agents and brokers', teer: 3, category: 'Sales' },
    { code: '63101', title: 'Real estate agents and salespersons', teer: 3, category: 'Sales' },
    { code: '63102', title: 'Financial sales representatives', teer: 3, category: 'Sales' },
    { code: '63200', title: 'Cooks', teer: 3, category: 'Sales' },
    { code: '63201', title: 'Butchers - retail and wholesale', teer: 3, category: 'Sales' },
    { code: '63202', title: 'Bakers', teer: 3, category: 'Sales' },
    { code: '63210', title: 'Hairstylists and barbers', teer: 3, category: 'Sales' },
    { code: '63211', title: 'Estheticians, electrologists and related occupations', teer: 3, category: 'Sales' },
    { code: '63220', title: 'Shoe repairers and shoemakers', teer: 3, category: 'Sales' },
    { code: '63221', title: 'Upholsterers', teer: 3, category: 'Sales' },
    { code: '64100', title: 'Retail salespersons and visual merchandisers', teer: 4, category: 'Sales' },
    { code: '64101', title: 'Sales and account representatives - wholesale trade (non-technical)', teer: 4, category: 'Sales' },
    { code: '64200', title: 'Tailors, dressmakers, furriers and milliners', teer: 4, category: 'Sales' },
    { code: '64201', title: 'Image, social and other personal consultants', teer: 4, category: 'Sales' },
    { code: '64300', title: 'Maîtres d\'hôtel and hosts/hostesses', teer: 4, category: 'Sales' },
    { code: '64301', title: 'Bartenders', teer: 4, category: 'Sales' },
    { code: '64310', title: 'Travel counsellors', teer: 4, category: 'Sales' },
    { code: '64311', title: 'Pursers and flight attendants', teer: 4, category: 'Sales' },
    { code: '64312', title: 'Airline ticket and service agents', teer: 4, category: 'Sales' },
    { code: '64313', title: 'Ground and water transport ticket agents, cargo service representatives and related clerks', teer: 4, category: 'Sales' },
    { code: '64314', title: 'Hotel front desk clerks', teer: 4, category: 'Sales' },
    { code: '64320', title: 'Tour and travel guides', teer: 4, category: 'Sales' },
    { code: '64321', title: 'Casino workers', teer: 4, category: 'Sales' },
    { code: '64322', title: 'Outdoor sport and recreational guides', teer: 4, category: 'Sales' },
    { code: '64400', title: 'Customer services representatives - financial institutions', teer: 4, category: 'Sales' },
    { code: '64401', title: 'Postal services representatives', teer: 4, category: 'Sales' },
    { code: '64409', title: 'Other customer and information services representatives', teer: 4, category: 'Sales' },
    { code: '64410', title: 'Security guards and related security service occupations', teer: 4, category: 'Sales' },
    { code: '65100', title: 'Cashiers', teer: 5, category: 'Sales' },
    { code: '65101', title: 'Service station attendants', teer: 5, category: 'Sales' },
    { code: '65102', title: 'Store shelf stockers, clerks and order fillers', teer: 5, category: 'Sales' },
    { code: '65109', title: 'Other sales related occupations', teer: 5, category: 'Sales' },
    { code: '65200', title: 'Food and beverage servers', teer: 5, category: 'Sales' },
    { code: '65201', title: 'Food counter attendants, kitchen helpers and related support occupations', teer: 5, category: 'Sales' },
    { code: '65202', title: 'Meat cutters and fishmongers - retail and wholesale', teer: 5, category: 'Sales' },
    { code: '65210', title: 'Support occupations in accommodation, travel and facilities set-up services', teer: 5, category: 'Sales' },
    { code: '65211', title: 'Operators and attendants in amusement, recreation and sport', teer: 5, category: 'Sales' },
    { code: '65220', title: 'Pet groomers and animal care workers', teer: 5, category: 'Sales' },
    { code: '65229', title: 'Other support occupations in personal services', teer: 5, category: 'Sales' },
    { code: '65310', title: 'Light duty cleaners', teer: 5, category: 'Sales' },
    { code: '65311', title: 'Specialized cleaners', teer: 5, category: 'Sales' },
    { code: '65312', title: 'Janitors, caretakers and heavy-duty cleaners', teer: 5, category: 'Sales' },
    { code: '65320', title: 'Dry cleaning, laundry and related occupations', teer: 5, category: 'Sales' },
    { code: '65329', title: 'Other service support occupations', teer: 5, category: 'Sales' },
    { code: '70010', title: 'Construction managers', teer: 0, category: 'Trades' },
    { code: '70011', title: 'Home building and renovation managers', teer: 0, category: 'Trades' },
    { code: '70012', title: 'Facility operation and maintenance managers', teer: 0, category: 'Trades' },
    { code: '70020', title: 'Managers in transportation', teer: 0, category: 'Trades' },
    { code: '70021', title: 'Postal and courier services managers', teer: 0, category: 'Trades' },
    { code: '72010', title: 'Contractors and supervisors, machining, metal forming, shaping and erecting trades and related occupations', teer: 2, category: 'Trades' },
    { code: '72011', title: 'Contractors and supervisors, electrical trades and telecommunications occupations', teer: 2, category: 'Trades' },
    { code: '72012', title: 'Contractors and supervisors, pipefitting trades', teer: 2, category: 'Trades' },
    { code: '72013', title: 'Contractors and supervisors, carpentry trades', teer: 2, category: 'Trades' },
    { code: '72014', title: 'Contractors and supervisors, other construction trades, installers, repairers and servicers', teer: 2, category: 'Trades' },
    { code: '72020', title: 'Contractors and supervisors, mechanic trades', teer: 2, category: 'Trades' },
    { code: '72021', title: 'Contractors and supervisors, heavy equipment operator crews', teer: 2, category: 'Trades' },
    { code: '72022', title: 'Supervisors, printing and related occupations', teer: 2, category: 'Trades' },
    { code: '72023', title: 'Supervisors, railway transport operations', teer: 2, category: 'Trades' },
    { code: '72024', title: 'Supervisors, motor transport and other ground transit operators', teer: 2, category: 'Trades' },
    { code: '72025', title: 'Supervisors, mail and message distribution occupations', teer: 2, category: 'Trades' },
    { code: '72100', title: 'Machinists and machining and tooling inspectors', teer: 2, category: 'Trades' },
    { code: '72101', title: 'Tool and die makers', teer: 2, category: 'Trades' },
    { code: '72102', title: 'Sheet metal workers', teer: 2, category: 'Trades' },
    { code: '72103', title: 'Boilermakers', teer: 2, category: 'Trades' },
    { code: '72104', title: 'Structural metal and platework fabricators and fitters', teer: 2, category: 'Trades' },
    { code: '72105', title: 'Ironworkers', teer: 2, category: 'Trades' },
    { code: '72106', title: 'Welders and related machine operators', teer: 2, category: 'Trades' },
    { code: '72200', title: 'Electricians (except industrial and power system)', teer: 2, category: 'Trades' },
    { code: '72201', title: 'Industrial electricians', teer: 2, category: 'Trades' },
    { code: '72202', title: 'Power system electricians', teer: 2, category: 'Trades' },
    { code: '72203', title: 'Electrical power line and cable workers', teer: 2, category: 'Trades' },
    { code: '72204', title: 'Telecommunications line and cable installers and repairers', teer: 2, category: 'Trades' },
    { code: '72205', title: 'Telecommunications equipment installation and cable television service technicians', teer: 2, category: 'Trades' },
    { code: '72300', title: 'Plumbers', teer: 2, category: 'Trades' },
    { code: '72301', title: 'Steamfitters, pipefitters and sprinkler system installers', teer: 2, category: 'Trades' },
    { code: '72302', title: 'Gas fitters', teer: 2, category: 'Trades' },
    { code: '72310', title: 'Carpenters', teer: 2, category: 'Trades' },
    { code: '72311', title: 'Cabinetmakers', teer: 2, category: 'Trades' },
    { code: '72320', title: 'Bricklayers', teer: 2, category: 'Trades' },
    { code: '72321', title: 'Insulators', teer: 2, category: 'Trades' },
    { code: '72400', title: 'Construction millwrights and industrial mechanics', teer: 2, category: 'Trades' },
    { code: '72401', title: 'Heavy-duty equipment mechanics', teer: 2, category: 'Trades' },
    { code: '72402', title: 'Heating, refrigeration and air conditioning mechanics', teer: 2, category: 'Trades' },
    { code: '72403', title: 'Railway carmen/women', teer: 2, category: 'Trades' },
    { code: '72404', title: 'Aircraft mechanics and aircraft inspectors', teer: 2, category: 'Trades' },
    { code: '72405', title: 'Machine fitters', teer: 2, category: 'Trades' },
    { code: '72406', title: 'Elevator constructors and mechanics', teer: 2, category: 'Trades' },
    { code: '72410', title: 'Automotive service technicians, truck and bus mechanics and mechanical repairers', teer: 2, category: 'Trades' },
    { code: '72411', title: 'Auto body collision, refinishing and glass technicians and damage repair estimators', teer: 2, category: 'Trades' },
    { code: '72420', title: 'Oil and solid fuel heating mechanics', teer: 2, category: 'Trades' },
    { code: '72421', title: 'Appliance servicers and repairers', teer: 2, category: 'Trades' },
    { code: '72422', title: 'Electrical mechanics', teer: 2, category: 'Trades' },
    { code: '72423', title: 'Motorcycle, all-terrain vehicle and other related mechanics', teer: 2, category: 'Trades' },
    { code: '72429', title: 'Other small engine and small equipment repairers', teer: 2, category: 'Trades' },
    { code: '72500', title: 'Crane operators', teer: 2, category: 'Trades' },
    { code: '72501', title: 'Water well drillers', teer: 2, category: 'Trades' },
    { code: '72600', title: 'Air pilots, flight engineers and flying instructors', teer: 2, category: 'Trades' },
    { code: '72601', title: 'Air traffic controllers and related occupations', teer: 2, category: 'Trades' },
    { code: '72602', title: 'Deck officers, water transport', teer: 2, category: 'Trades' },
    { code: '72603', title: 'Engineer officers, water transport', teer: 2, category: 'Trades' },
    { code: '72604', title: 'Railway traffic controllers and marine traffic regulators', teer: 2, category: 'Trades' },
    { code: '72999', title: 'Other technical trades and related occupations', teer: 2, category: 'Trades' },
    { code: '73100', title: 'Concrete finishers', teer: 3, category: 'Trades' },
    { code: '73101', title: 'Tilesetters', teer: 3, category: 'Trades' },
    { code: '73102', title: 'Plasterers, drywall installers and finishers and lathers', teer: 3, category: 'Trades' },
    { code: '73110', title: 'Roofers and shinglers', teer: 3, category: 'Trades' },
    { code: '73111', title: 'Glaziers', teer: 3, category: 'Trades' },
    { code: '73112', title: 'Painters and decorators (except interior decorators)', teer: 3, category: 'Trades' },
    { code: '73113', title: 'Floor covering installers', teer: 3, category: 'Trades' },
    { code: '73200', title: 'Residential and commercial installers and servicers', teer: 3, category: 'Trades' },
    { code: '73201', title: 'General building maintenance workers and building superintendents', teer: 3, category: 'Trades' },
    { code: '73202', title: 'Pest controllers and fumigators', teer: 3, category: 'Trades' },
    { code: '73209', title: 'Other repairers and servicers', teer: 3, category: 'Trades' },
    { code: '73300', title: 'Transport truck drivers', teer: 3, category: 'Trades' },
    { code: '73301', title: 'Bus drivers, subway operators and other transit operators', teer: 3, category: 'Trades' },
    { code: '73310', title: 'Railway and yard locomotive engineers', teer: 3, category: 'Trades' },
    { code: '73311', title: 'Railway conductors and brakemen/women', teer: 3, category: 'Trades' },
    { code: '73400', title: 'Heavy equipment operators', teer: 3, category: 'Trades' },
    { code: '73401', title: 'Printing press operators', teer: 3, category: 'Trades' },
    { code: '73402', title: 'Drillers and blasters - surface mining, quarrying and construction', teer: 3, category: 'Trades' },
    { code: '74100', title: 'Mail and parcel sorters and related occupations', teer: 4, category: 'Trades' },
    { code: '74101', title: 'Letter carriers', teer: 4, category: 'Trades' },
    { code: '74102', title: 'Couriers and messengers', teer: 4, category: 'Trades' },
    { code: '74200', title: 'Railway yard and track maintenance workers', teer: 4, category: 'Trades' },
    { code: '74201', title: 'Water transport deck and engine room crew', teer: 4, category: 'Trades' },
    { code: '74202', title: 'Air transport ramp attendants', teer: 4, category: 'Trades' },
    { code: '74203', title: 'Automotive and heavy truck and equipment parts installers and servicers', teer: 4, category: 'Trades' },
    { code: '74204', title: 'Utility maintenance workers', teer: 4, category: 'Trades' },
    { code: '74205', title: 'Public works maintenance equipment operators and related workers', teer: 4, category: 'Trades' },
    { code: '75100', title: 'Longshore workers', teer: 5, category: 'Trades' },
    { code: '75101', title: 'Material handlers', teer: 5, category: 'Trades' },
    { code: '75110', title: 'Construction trades helpers and labourers', teer: 5, category: 'Trades' },
    { code: '75119', title: 'Other trades helpers and labourers', teer: 5, category: 'Trades' },
    { code: '75200', title: 'Taxi and limousine drivers and chauffeurs', teer: 5, category: 'Trades' },
    { code: '75201', title: 'Delivery service drivers and door-to-door distributors', teer: 5, category: 'Trades' },
    { code: '75210', title: 'Boat and cable ferry operators and related occupations', teer: 5, category: 'Trades' },
    { code: '75211', title: 'Railway and motor transport labourers', teer: 5, category: 'Trades' },
    { code: '75212', title: 'Public works and maintenance labourers', teer: 5, category: 'Trades' },
    { code: '80010', title: 'Managers in natural resources production and fishing', teer: 0, category: 'Agriculture' },
    { code: '80020', title: 'Managers in agriculture', teer: 0, category: 'Agriculture' },
    { code: '80021', title: 'Managers in horticulture', teer: 0, category: 'Agriculture' },
    { code: '80022', title: 'Managers in aquaculture', teer: 0, category: 'Agriculture' },
    { code: '82010', title: 'Supervisors, logging and forestry', teer: 2, category: 'Agriculture' },
    { code: '82020', title: 'Supervisors, mining and quarrying', teer: 2, category: 'Agriculture' },
    { code: '82021', title: 'Contractors and supervisors, oil and gas drilling and services', teer: 2, category: 'Agriculture' },
    { code: '82030', title: 'Agricultural service contractors and farm supervisors', teer: 2, category: 'Agriculture' },
    { code: '82031', title: 'Contractors and supervisors, landscaping, grounds maintenance and horticulture services', teer: 2, category: 'Agriculture' },
    { code: '83100', title: 'Underground production and development miners', teer: 3, category: 'Agriculture' },
    { code: '83101', title: 'Oil and gas well drillers, servicers, testers and related workers', teer: 3, category: 'Agriculture' },
    { code: '83110', title: 'Logging machinery operators', teer: 3, category: 'Agriculture' },
    { code: '83120', title: 'Fishing masters and officers', teer: 3, category: 'Agriculture' },
    { code: '83121', title: 'Fishermen/women', teer: 3, category: 'Agriculture' },
    { code: '84100', title: 'Underground mine service and support workers', teer: 4, category: 'Agriculture' },
    { code: '84101', title: 'Oil and gas well drilling and related workers and services operators', teer: 4, category: 'Agriculture' },
    { code: '84110', title: 'Chain saw and skidder operators', teer: 4, category: 'Agriculture' },
    { code: '84111', title: 'Silviculture and forestry workers', teer: 4, category: 'Agriculture' },
    { code: '84120', title: 'Specialized livestock workers and farm machinery operators', teer: 4, category: 'Agriculture' },
    { code: '84121', title: 'Fishing vessel deckhands', teer: 4, category: 'Agriculture' },
    { code: '85100', title: 'Livestock labourers', teer: 5, category: 'Agriculture' },
    { code: '85101', title: 'Harvesting labourers', teer: 5, category: 'Agriculture' },
    { code: '85102', title: 'Aquaculture and marine harvest labourers', teer: 5, category: 'Agriculture' },
    { code: '85103', title: 'Nursery and greenhouse labourers', teer: 5, category: 'Agriculture' },
    { code: '85104', title: 'Trappers and hunters', teer: 5, category: 'Agriculture' },
    { code: '85110', title: 'Mine labourers', teer: 5, category: 'Agriculture' },
    { code: '85111', title: 'Oil and gas drilling, servicing and related labourers', teer: 5, category: 'Agriculture' },
    { code: '85120', title: 'Logging and forestry labourers', teer: 5, category: 'Agriculture' },
    { code: '85121', title: 'Landscaping and grounds maintenance labourers', teer: 5, category: 'Agriculture' },
    { code: '90010', title: 'Manufacturing managers', teer: 0, category: 'Manufacturing' },
    { code: '90011', title: 'Utilities managers', teer: 0, category: 'Manufacturing' },
    { code: '92010', title: 'Supervisors, mineral and metal processing', teer: 2, category: 'Manufacturing' },
    { code: '92011', title: 'Supervisors, petroleum, gas and chemical processing and utilities', teer: 2, category: 'Manufacturing' },
    { code: '92012', title: 'Supervisors, food and beverage processing', teer: 2, category: 'Manufacturing' },
    { code: '92013', title: 'Supervisors, plastic and rubber products manufacturing', teer: 2, category: 'Manufacturing' },
    { code: '92014', title: 'Supervisors, forest products processing', teer: 2, category: 'Manufacturing' },
    { code: '92015', title: 'Supervisors, textile, fabric, fur and leather products processing and manufacturing', teer: 2, category: 'Manufacturing' },
    { code: '92020', title: 'Supervisors, motor vehicle assembling', teer: 2, category: 'Manufacturing' },
    { code: '92021', title: 'Supervisors, electronics and electrical products manufacturing', teer: 2, category: 'Manufacturing' },
    { code: '92022', title: 'Supervisors, furniture and fixtures manufacturing', teer: 2, category: 'Manufacturing' },
    { code: '92023', title: 'Supervisors, other mechanical and metal products manufacturing', teer: 2, category: 'Manufacturing' },
    { code: '92024', title: 'Supervisors, other products manufacturing and assembly', teer: 2, category: 'Manufacturing' },
    { code: '92100', title: 'Power engineers and power systems operators', teer: 2, category: 'Manufacturing' },
    { code: '92101', title: 'Water and waste treatment plant operators', teer: 2, category: 'Manufacturing' },
    { code: '93100', title: 'Central control and process operators, mineral and metal processing', teer: 3, category: 'Manufacturing' },
    { code: '93101', title: 'Central control and process operators, petroleum, gas and chemical processing', teer: 3, category: 'Manufacturing' },
    { code: '93102', title: 'Pulping, papermaking and coating control operators', teer: 3, category: 'Manufacturing' },
    { code: '93200', title: 'Aircraft assemblers and aircraft assembly inspectors', teer: 3, category: 'Manufacturing' },
    { code: '94100', title: 'Machine operators, mineral and metal processing', teer: 4, category: 'Manufacturing' },
    { code: '94101', title: 'Foundry workers', teer: 4, category: 'Manufacturing' },
    { code: '94102', title: 'Glass forming and finishing machine operators and glass cutters', teer: 4, category: 'Manufacturing' },
    { code: '94103', title: 'Concrete, clay and stone forming operators', teer: 4, category: 'Manufacturing' },
    { code: '94104', title: 'Inspectors and testers, mineral and metal processing', teer: 4, category: 'Manufacturing' },
    { code: '94105', title: 'Metalworking and forging machine operators', teer: 4, category: 'Manufacturing' },
    { code: '94106', title: 'Machining tool operators', teer: 4, category: 'Manufacturing' },
    { code: '94107', title: 'Machine operators of other metal products', teer: 4, category: 'Manufacturing' },
    { code: '94110', title: 'Chemical plant machine operators', teer: 4, category: 'Manufacturing' },
    { code: '94111', title: 'Plastics processing machine operators', teer: 4, category: 'Manufacturing' },
    { code: '94112', title: 'Rubber processing machine operators and related workers', teer: 4, category: 'Manufacturing' },
    { code: '94120', title: 'Sawmill machine operators', teer: 4, category: 'Manufacturing' },
    { code: '94121', title: 'Pulp mill, papermaking and finishing machine operators', teer: 4, category: 'Manufacturing' },
    { code: '94122', title: 'Paper converting machine operators', teer: 4, category: 'Manufacturing' },
    { code: '94123', title: 'Lumber graders and other wood processing inspectors and graders', teer: 4, category: 'Manufacturing' },
    { code: '94124', title: 'Woodworking machine operators', teer: 4, category: 'Manufacturing' },
    { code: '94129', title: 'Other wood processing machine operators', teer: 4, category: 'Manufacturing' },
    { code: '94130', title: 'Textile fibre and yarn, hide and pelt processing machine operators and workers', teer: 4, category: 'Manufacturing' },
    { code: '94131', title: 'Weavers, knitters and other fabric making occupations', teer: 4, category: 'Manufacturing' },
    { code: '94132', title: 'Industrial sewing machine operators', teer: 4, category: 'Manufacturing' },
    { code: '94133', title: 'Inspectors and graders, textile, fabric, fur and leather products manufacturing', teer: 4, category: 'Manufacturing' },
    { code: '94140', title: 'Process control and machine operators, food and beverage processing', teer: 4, category: 'Manufacturing' },
    { code: '94141', title: 'Industrial butchers and meat cutters, poultry preparers and related workers', teer: 4, category: 'Manufacturing' },
    { code: '94142', title: 'Fish and seafood plant workers', teer: 4, category: 'Manufacturing' },
    { code: '94143', title: 'Testers and graders, food and beverage processing', teer: 4, category: 'Manufacturing' },
    { code: '94150', title: 'Plateless printing equipment operators', teer: 4, category: 'Manufacturing' },
    { code: '94151', title: 'Camera, platemaking and other prepress occupations', teer: 4, category: 'Manufacturing' },
    { code: '94152', title: 'Binding and finishing machine operators', teer: 4, category: 'Manufacturing' },
    { code: '94153', title: 'Photographic and film processors', teer: 4, category: 'Manufacturing' },
    { code: '94200', title: 'Motor vehicle assemblers, inspectors and testers', teer: 4, category: 'Manufacturing' },
    { code: '94201', title: 'Electronics assemblers, fabricators, inspectors and testers', teer: 4, category: 'Manufacturing' },
    { code: '94202', title: 'Assemblers and inspectors, electrical appliance, apparatus and equipment manufacturing', teer: 4, category: 'Manufacturing' },
    { code: '94203', title: 'Assemblers, fabricators and inspectors, industrial electrical motors and transformers', teer: 4, category: 'Manufacturing' },
    { code: '94204', title: 'Mechanical assemblers and inspectors', teer: 4, category: 'Manufacturing' },
    { code: '94205', title: 'Machine operators and inspectors, electrical apparatus manufacturing', teer: 4, category: 'Manufacturing' },
    { code: '94210', title: 'Furniture and fixture assemblers, finishers, refinishers and inspectors', teer: 4, category: 'Manufacturing' },
    { code: '94211', title: 'Assemblers and inspectors of other wood products', teer: 4, category: 'Manufacturing' },
    { code: '94212', title: 'Plastic products assemblers, finishers and inspectors', teer: 4, category: 'Manufacturing' },
    { code: '94213', title: 'Industrial painters, coaters and metal finishing process operators', teer: 4, category: 'Manufacturing' },
    { code: '94219', title: 'Other products assemblers, finishers and inspectors', teer: 4, category: 'Manufacturing' },
    { code: '95100', title: 'Labourers in mineral and metal processing', teer: 5, category: 'Manufacturing' },
    { code: '95101', title: 'Labourers in metal fabrication', teer: 5, category: 'Manufacturing' },
    { code: '95102', title: 'Labourers in chemical products processing and utilities', teer: 5, category: 'Manufacturing' },
    { code: '95103', title: 'Labourers in wood, pulp and paper processing', teer: 5, category: 'Manufacturing' },
    { code: '95104', title: 'Labourers in rubber and plastic products manufacturing', teer: 5, category: 'Manufacturing' },
    { code: '95105', title: 'Labourers in textile processing and cutting', teer: 5, category: 'Manufacturing' },
    { code: '95106', title: 'Labourers in food and beverage processing', teer: 5, category: 'Manufacturing' },
    { code: '95107', title: 'Labourers in fish and seafood processing', teer: 5, category: 'Manufacturing' },
    { code: '95109', title: 'Other labourers in processing, manufacturing and utilities', teer: 5, category: 'Manufacturing' }
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

// ============================================================================
// COMPREHENSIVE PROVINCIAL STREAMS DATA (2026 Updated)
// ============================================================================

const PROVINCIAL_STREAMS = {
    ontario: {
        name: 'Ontario Immigrant Nominee Program (OINP)',
        allocation2026: 17872,
        streams: [
            // NEW 2026 STREAMS
            {
                id: 'oinp_priority_healthcare',
                name: 'Priority Healthcare Stream',
                status: 'NEW_2026',
                launchDate: 'Spring 2026',
                jobOfferRequired: false,
                eligibleNOCs: ['31301', '31302', '31102', '32101', '32120', '32121', '32123', '33102'],
                requirements: [
                    'Valid Ontario professional registration/license',
                    'CLB 7 in each ability',
                    'Intend to live in Ontario',
                    'NO JOB OFFER REQUIRED'
                ],
                processingTime: '3-6 months (estimated)',
                highlight: 'No job offer needed for healthcare workers!'
            },
            {
                id: 'oinp_critical_sectors',
                name: 'Critical Sectors Stream',
                status: 'NEW_2026',
                launchDate: 'Spring 2026',
                jobOfferRequired: true,
                sectors: ['construction', 'manufacturing', 'agriculture'],
                requirements: [
                    'Job offer in construction, manufacturing, or agriculture',
                    'TEER 0-3 occupation',
                    'CLB 5 minimum',
                    'French speakers may get bonus points'
                ],
                processingTime: '4-6 months (estimated)'
            },
            {
                id: 'oinp_employer_job_offer',
                name: 'Employer Job Offer Stream',
                status: 'UPDATED_2026',
                jobOfferRequired: true,
                subStreams: [
                    { name: 'TEER 0-3 (Higher-Skilled)', drawFrequency: 'Regular draws' },
                    { name: 'TEER 4-5 (Entry-Level)', drawFrequency: 'Limited draws' }
                ],
                requirements: [
                    'Valid job offer from Ontario employer',
                    'Meets wage threshold for region',
                    'EOI-based selection'
                ]
            },
            // EXISTING STREAMS
            {
                id: 'oinp_human_capital',
                name: 'Human Capital Priorities',
                expressEntry: true,
                requirements: [
                    'CRS 400+ (varies by draw)',
                    'In Express Entry pool',
                    'Skilled work experience',
                    'CLB 7 in each ability'
                ],
                recentCutoff: 489,
                processingTime: '3-6 months'
            },
            {
                id: 'oinp_tech_draw',
                name: 'Tech Draw',
                expressEntry: true,
                eligibleNOCs: ['21231', '21232', '21233', '21234', '21211', '21220', '21221', '21222', '21223', '20012'],
                requirements: [
                    'In Express Entry pool',
                    'Tech occupation (software, data, cybersecurity)',
                    'CRS varies (typically 450-490)'
                ],
                drawFrequency: 'Monthly',
                processingTime: '3-6 months'
            },
            {
                id: 'oinp_french_skilled',
                name: 'French-Speaking Skilled Worker',
                expressEntry: true,
                requirements: [
                    'NCLC 7+ in French (all abilities)',
                    'CLB 6+ in English',
                    'In Express Entry pool'
                ],
                benefit: 'Lower CRS cutoffs (380-440)',
                processingTime: '3-6 months'
            }
        ]
    },

    alberta: {
        name: 'Alberta Advantage Immigration Program (AAIP)',
        allocation2026: 10140,
        streams: [
            {
                id: 'aaip_opportunity',
                name: 'Alberta Opportunity Stream',
                highlight: 'Most popular! No Express Entry required',
                expressEntry: false,
                requirements: [
                    'Currently working in Alberta on valid work permit',
                    '12 months full-time work in Alberta (last 18 months)',
                    'Job offer from Alberta employer',
                    'CLB 4 (TEER 4-5) or CLB 5 (TEER 0-3)',
                    'Meet minimum income threshold'
                ],
                processingTime: '3-6 months'
            },
            {
                id: 'aaip_express_entry',
                name: 'Alberta Express Entry Stream',
                expressEntry: true,
                requirements: [
                    'In Express Entry pool (FSW, CEC, or FST)',
                    'CRS 300+ (much lower than federal!)',
                    'Strong ties to Alberta OR occupation in demand'
                ],
                benefit: 'CRS as low as 300 accepted',
                processingTime: '3-6 months'
            },
            {
                id: 'aaip_tech',
                name: 'Accelerated Tech Pathway',
                highlight: '3-week processing!',
                eligibleNOCs: ['21231', '21232', '21233', '21234', '21211', '21220', '21222', '21223'],
                requirements: [
                    'Job offer from Alberta tech company',
                    'Tech occupation',
                    'Meet stream requirements'
                ],
                processingTime: '3 weeks',
                benefit: 'Fastest PNP processing in Canada'
            },
            {
                id: 'aaip_rural',
                name: 'Rural Renewal Stream',
                requirements: [
                    'Job offer in designated rural community',
                    'Community endorsement',
                    '12 months work experience'
                ],
                processingTime: '3-6 months'
            }
        ]
    },

    bc: {
        name: 'BC Provincial Nominee Program (BC PNP)',
        allocation2026: 8500,
        streams: [
            {
                id: 'bcpnp_tech',
                name: 'BC PNP Tech',
                highlight: 'Priority processing for tech workers',
                eligibleNOCs: ['21231', '21232', '21233', '21234', '21211', '21220', '21222', '21223', '21310', '21311', '22220', '22221'],
                requirements: [
                    'Job offer from BC tech company (1+ year)',
                    'Meets occupation requirements',
                    'SIRS score competitive'
                ],
                processingTime: '2-3 months',
                benefit: 'Weekly invitation rounds'
            },
            {
                id: 'bcpnp_healthcare',
                name: 'BC Healthcare Priority',
                eligibleNOCs: ['31301', '31302', '31102', '32101', '33102'],
                requirements: [
                    'Job offer in BC healthcare',
                    'Valid license/registration',
                    'CLB 7 for regulated professions'
                ],
                processingTime: '2-4 months'
            },
            {
                id: 'bcpnp_skilled_worker',
                name: 'Skills Immigration - Skilled Worker',
                expressEntry: false,
                requirements: [
                    'Job offer from BC employer',
                    'TEER 0-3 occupation',
                    '2+ years relevant experience',
                    'Meet SIRS threshold'
                ],
                recentCutoff: 85,
                processingTime: '4-6 months'
            },
            {
                id: 'bcpnp_ee',
                name: 'Express Entry BC',
                expressEntry: true,
                requirements: [
                    'In Express Entry pool',
                    'Job offer from BC employer',
                    'SIRS score competitive'
                ],
                benefit: '+600 CRS points on nomination',
                processingTime: '2-4 months'
            }
        ]
    },

    saskatchewan: {
        name: 'Saskatchewan Immigrant Nominee Program (SINP)',
        allocation2026: 7250,
        streams: [
            {
                id: 'sinp_occupation_demand',
                name: 'International Skilled Worker - Occupation In-Demand',
                highlight: 'No job offer OR Express Entry required!',
                expressEntry: false,
                jobOfferRequired: false,
                requirements: [
                    'Occupation on Saskatchewan In-Demand list',
                    '1 year work experience (last 10 years)',
                    'Post-secondary credential (1+ year)',
                    'CLB 4 minimum',
                    '60+ SINP points'
                ],
                processingTime: '4-8 months',
                benefit: 'Apply without job offer or EE profile'
            },
            {
                id: 'sinp_ee',
                name: 'International Skilled Worker - Express Entry',
                expressEntry: true,
                requirements: [
                    'In Express Entry pool',
                    '60-70 SINP points',
                    'Occupation eligible'
                ],
                benefit: 'Lower points than other provinces',
                processingTime: '3-6 months'
            },
            {
                id: 'sinp_hard_to_fill',
                name: 'Hard-to-Fill Skills Pilot',
                highlight: 'Guaranteed processing for specific NOCs',
                requirements: [
                    'Job offer in hard-to-fill occupation',
                    'Employer registered with SINP'
                ],
                processingTime: '3-4 months'
            }
        ]
    },

    manitoba: {
        name: 'Manitoba Provincial Nominee Program (MPNP)',
        allocation2026: 6500,
        streams: [
            {
                id: 'mpnp_skilled_manitoba',
                name: 'Skilled Worker in Manitoba',
                highlight: '6 months work = eligible',
                requirements: [
                    'Currently working in Manitoba',
                    '6+ months full-time work with current employer',
                    'Job offer from same employer',
                    'CLB 5 (TEER 4-5) or CLB 6 (TEER 0-3)'
                ],
                processingTime: '4-6 months',
                benefit: 'Fastest path if already working in MB'
            },
            {
                id: 'mpnp_skilled_overseas',
                name: 'Skilled Worker Overseas',
                requirements: [
                    'Connection to Manitoba (family, previous work/study, or ITA)',
                    '60+ MPNP assessment points',
                    'CLB 5 minimum'
                ],
                processingTime: '6-12 months'
            },
            {
                id: 'mpnp_international_education',
                name: 'International Education Stream',
                requirements: [
                    'Graduated from Manitoba institution',
                    'Job offer or working in Manitoba',
                    'Language proficiency'
                ],
                processingTime: '3-6 months',
                benefit: 'Fast-track for Manitoba graduates'
            }
        ]
    },

    atlantic: {
        name: 'Atlantic Immigration Program (AIP)',
        provinces: ['Nova Scotia', 'New Brunswick', 'Prince Edward Island', 'Newfoundland & Labrador'],
        highlight: 'Employer-driven program - No LMIA required!',
        streams: [
            {
                id: 'aip_skilled',
                name: 'Atlantic High-Skilled Program',
                requirements: [
                    'Job offer from designated Atlantic employer',
                    'TEER 0, 1, 2, or 3 occupation',
                    '1 year work experience (last 5 years)',
                    'CLB 5 minimum (CLB 4 for TEER 4-5)',
                    'Settlement funds'
                ],
                processingTime: '6-12 months total',
                benefit: 'No LMIA needed - employer designation only'
            },
            {
                id: 'aip_intermediate',
                name: 'Atlantic Intermediate-Skilled Program',
                requirements: [
                    'Job offer from designated Atlantic employer',
                    'TEER 4 occupation',
                    '1 year work experience',
                    'CLB 4 minimum'
                ],
                processingTime: '6-12 months'
            },
            {
                id: 'aip_graduate',
                name: 'Atlantic International Graduate Program',
                requirements: [
                    'Graduated from Atlantic institution (2+ years)',
                    'Job offer from designated employer',
                    'CLB 5 minimum'
                ],
                processingTime: '6-12 months'
            }
        ]
    }
};

// ============================================================================
// NOC TO PATHWAY MATCHING - Maps occupation to best pathways
// ============================================================================

const NOC_PATHWAY_MATCHING = {
    // Software & Tech (TEER 1)
    '21231': {
        title: 'Software Engineers and Designers',
        federalCategories: ['STEM'],
        provincialPriority: ['oinp_tech_draw', 'bcpnp_tech', 'aaip_tech'],
        recentDraws: { stem: 485, general: 520 },
        recommendation: 'STEM category or provincial tech streams offer best chances'
    },
    '21232': {
        title: 'Software Developers and Programmers',
        federalCategories: ['STEM'],
        provincialPriority: ['oinp_tech_draw', 'bcpnp_tech', 'aaip_tech', 'sinp_occupation_demand'],
        recentDraws: { stem: 485, general: 520 },
        recommendation: 'Multiple provincial tech streams available'
    },
    '21211': {
        title: 'Data Scientists',
        federalCategories: ['STEM'],
        provincialPriority: ['oinp_tech_draw', 'bcpnp_tech', 'aaip_tech'],
        recentDraws: { stem: 485 },
        recommendation: 'High demand - STEM draws and tech PNPs'
    },

    // Healthcare (TEER 1)
    '31301': {
        title: 'Registered Nurses',
        federalCategories: ['Healthcare'],
        provincialPriority: ['oinp_priority_healthcare', 'bcpnp_healthcare', 'aip_skilled'],
        recentDraws: { healthcare: 476, general: 520 },
        recommendation: 'Healthcare draws have lowest CRS! Ontario 2026 needs no job offer!'
    },
    '31302': {
        title: 'Nurse Practitioners',
        federalCategories: ['Healthcare'],
        provincialPriority: ['oinp_priority_healthcare', 'bcpnp_healthcare'],
        recentDraws: { healthcare: 476 },
        recommendation: 'Extremely high demand - multiple pathways available'
    },
    '31102': {
        title: 'General Practitioners and Family Physicians',
        federalCategories: ['Healthcare'],
        provincialPriority: ['oinp_priority_healthcare', 'bcpnp_healthcare'],
        recentDraws: { healthcare: 476 },
        recommendation: 'Doctors in very high demand across all provinces'
    },
    '32101': {
        title: 'Licensed Practical Nurses',
        federalCategories: ['Healthcare'],
        provincialPriority: ['oinp_priority_healthcare', 'bcpnp_healthcare', 'aip_skilled'],
        recentDraws: { healthcare: 476 },
        recommendation: 'LPNs eligible for healthcare draws and priority PNP streams'
    },

    // Skilled Trades (TEER 2-3)
    '72200': {
        title: 'Electricians',
        federalCategories: ['Trades'],
        provincialPriority: ['sinp_occupation_demand', 'aaip_opportunity', 'aip_skilled'],
        recentDraws: { trades: 441, general: 520 },
        recommendation: 'Trades draws + Saskatchewan in-demand list'
    },
    '72300': {
        title: 'Plumbers',
        federalCategories: ['Trades'],
        provincialPriority: ['sinp_occupation_demand', 'aaip_opportunity', 'aip_skilled'],
        recentDraws: { trades: 441 },
        recommendation: 'High demand in all provinces - multiple PNP options'
    },
    '72310': {
        title: 'Carpenters',
        federalCategories: ['Trades'],
        provincialPriority: ['sinp_occupation_demand', 'aaip_opportunity', 'oinp_critical_sectors'],
        recentDraws: { trades: 441 },
        recommendation: 'Ontario 2026 Critical Sectors stream for construction'
    },
    '73300': {
        title: 'Transport Truck Drivers',
        federalCategories: ['Transport'],
        provincialPriority: ['aaip_opportunity', 'sinp_occupation_demand', 'mpnp_skilled_manitoba'],
        recentDraws: { transport: 435 },
        recommendation: 'Transport draws and provincial pathways - high demand'
    },

    // Agriculture (TEER 2-4)
    '82020': {
        title: 'Supervisors - Agriculture',
        federalCategories: ['Agriculture'],
        provincialPriority: ['sinp_occupation_demand', 'aaip_opportunity', 'oinp_critical_sectors'],
        recentDraws: { agriculture: 420 },
        recommendation: 'Agriculture draws have low cutoffs'
    }
};

// ============================================================================
// FEDERAL CATEGORY-BASED DRAWS DATA
// ============================================================================

// Last updated: Jan 12, 2026 - Based on official IRCC data
const FEDERAL_CATEGORIES = {
    healthcare: {
        name: 'Healthcare',
        recentCutoff: 476,  // Dec 11, 2025 draw
        averageCutoff: 460,
        eligibleNOCs: ['31100', '31101', '31102', '31103', '31110', '31111', '31112', '31120', '31121',
                       '31200', '31201', '31202', '31203', '31204', '31209', '31300', '31301', '31302', '31303',
                       '32100', '32101', '32102', '32103', '32104', '32109', '32110', '32111', '32112',
                       '32120', '32121', '32122', '32123', '32124', '32129', '32200', '32201', '32209',
                       '33100', '33101', '33102', '33103', '33109'],
        frequency: 'Every 2-4 weeks',
        trend: 'Increasing due to healthcare worker shortage'
    },
    stem: {
        name: 'STEM (Science, Technology, Engineering, Math)',
        recentCutoff: 485,
        averageCutoff: 490,
        eligibleNOCs: ['21100', '21101', '21102', '21103', '21109', '21110', '21111', '21112', '21120',
                       '21200', '21201', '21202', '21203', '21210', '21211', '21220', '21221', '21222', '21223',
                       '21230', '21231', '21232', '21233', '21234',
                       '21300', '21301', '21310', '21311', '21320', '21321', '21322', '21330', '21331', '21332', '21390', '21399',
                       '22100', '22101', '22110', '22111', '22112', '22113', '22114', '22210', '22211', '22212', '22213', '22214',
                       '22220', '22221', '22222', '22230', '22231', '22232', '22233', '22300', '22301', '22302', '22303', '22310', '22311', '22312', '22313'],
        frequency: 'Every 2-4 weeks',
        trend: 'Stable demand for tech workers'
    },
    trades: {
        name: 'Skilled Trades',
        recentCutoff: 441,
        averageCutoff: 450,
        eligibleNOCs: ['72010', '72011', '72012', '72013', '72014', '72020', '72021', '72100', '72101', '72102', '72103', '72104', '72105', '72106',
                       '72200', '72201', '72300', '72301', '72302', '72310', '72311', '72320', '72321',
                       '72400', '72401', '72402', '72403', '72410', '72411', '72420', '72421', '72500', '72501'],
        frequency: 'Every 3-4 weeks',
        trend: 'Growing demand for construction trades'
    },
    transport: {
        name: 'Transport',
        recentCutoff: 435,
        averageCutoff: 440,
        eligibleNOCs: ['72600', '72601', '72602', '72603', '72604', '73300', '73301', '73310', '73311'],
        frequency: 'Monthly',
        trend: 'New category - steady demand'
    },
    agriculture: {
        name: 'Agriculture and Agri-Food',
        recentCutoff: 420,
        averageCutoff: 430,
        eligibleNOCs: ['82010', '82011', '82020', '82021', '82030', '82031', '84100', '84120', '85100', '85101', '85102', '85103'],
        frequency: 'Monthly',
        trend: 'Lowest cutoffs among categories'
    },
    french: {
        name: 'French Language Proficiency',
        recentCutoff: 399,  // Dec 17, 2025 draw
        averageCutoff: 405,
        requirement: 'NCLC 7+ in French (all abilities)',
        frequency: 'Every 2-3 weeks',
        trend: 'Lowest CRS cutoffs - great option for French speakers'
    }
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
