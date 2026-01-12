// Eligibility Engine - Question Rendering & Recommendation Logic

let currentQuestion = 0;
let answers = {};
let selectedOccupation = null;
let formError = null;

// Initialize on page load
document.addEventListener('DOMContentLoaded', () => {
    try {
        // Check if QUESTIONS is loaded
        if (typeof QUESTIONS === 'undefined' || !QUESTIONS || QUESTIONS.length === 0) {
            console.error('QUESTIONS not loaded');
            document.getElementById('questionContainer').innerHTML = `
                <div class="question-card">
                    <div class="question-header">
                        <h2>Loading Error</h2>
                        <div class="help-text">Unable to load questions. Please refresh the page.</div>
                    </div>
                </div>
            `;
            return;
        }
        renderQuestion();
    } catch (error) {
        console.error('Error initializing eligibility checker:', error);
    }
});

function renderQuestion() {
    try {
        // Find next applicable question
        while (currentQuestion < QUESTIONS.length) {
            const q = QUESTIONS[currentQuestion];
            if (!q.condition || q.condition(answers)) break;
            currentQuestion++;
        }

        if (currentQuestion >= QUESTIONS.length) {
            showResults();
            return;
        }

        const q = QUESTIONS[currentQuestion];
        const container = document.getElementById('questionContainer');

        if (!container) {
            console.error('Question container not found');
            return;
        }

    let inputHtml = '';
    if (q.type === 'search') {
        inputHtml = `
            <div class="search-container">
                <input type="text" class="search-input" id="occupationSearch"
                    placeholder="${q.placeholder || 'Search...'}"
                    onkeyup="searchOccupations(this.value)" autocomplete="off">
                <div class="search-results" id="searchResults"></div>
            </div>
            <div id="selectedOccupation" style="display:none; padding: 1rem; background: var(--bg); border-radius: 8px; margin-bottom: 1rem;">
                <strong id="selectedOccTitle"></strong>
                <span id="selectedOccDetails" style="color: var(--text-muted); font-size: 0.9rem;"></span>
            </div>
        `;
    } else if (q.type === 'email') {
        inputHtml = `
            <div class="text-input-container">
                <input type="email" class="text-input" id="emailInput"
                    placeholder="${q.placeholder || ''}"
                    value="${answers[q.id] || ''}"
                    oninput="answers['${q.id}'] = this.value">
            </div>
        `;
    } else if (q.type === 'phone') {
        inputHtml = `
            <div class="text-input-container">
                <input type="tel" class="text-input" id="phoneInput"
                    placeholder="${q.placeholder || ''}"
                    value="${answers[q.id] || ''}"
                    oninput="answers['${q.id}'] = this.value">
                ${q.optional ? '<p class="input-hint">This field is optional</p>' : ''}
            </div>
        `;
    } else if (q.type === 'salary' || q.type === 'funds') {
        inputHtml = `
            <div class="currency-input-container">
                <span class="currency-prefix">CAD $</span>
                <input type="number" class="currency-input" id="numberInput"
                    placeholder="${q.placeholder || '0'}"
                    value="${answers[q.id] || ''}"
                    min="0"
                    oninput="answers['${q.id}'] = this.value">
            </div>
        `;
    } else if (q.type === 'date') {
        inputHtml = `
            <div class="text-input-container">
                <input type="date" class="date-input" id="dateInput"
                    value="${answers[q.id] || ''}"
                    oninput="answers['${q.id}'] = this.value; checkDateValidity('${q.id}', this.value)">
                <div id="dateWarning" class="date-warning" style="display: none;"></div>
            </div>
        `;
    } else if (q.multiSelect) {
        const selectedValues = answers[q.id] || [];
        inputHtml = `
            <div class="multi-select-hint"><i class="bi bi-info-circle"></i> Select all that apply</div>
            <div class="options-grid">
            ${q.options.map(opt => `
                <button class="option-btn checkbox ${selectedValues.includes(opt.value) ? 'selected' : ''}"
                    onclick="toggleMultiOption('${q.id}', '${opt.value}', this)">
                    <div class="radio"></div>
                    <div class="option-text">
                        <div class="option-title">${opt.label}</div>
                        ${opt.desc ? `<div class="option-desc">${opt.desc}</div>` : ''}
                    </div>
                </button>
            `).join('')}
        </div>`;
    } else {
        inputHtml = `<div class="options-grid">
            ${q.options.map(opt => `
                <button class="option-btn ${answers[q.id] === opt.value ? 'selected' : ''}"
                    onclick="selectOption('${q.id}', '${opt.value}', this)">
                    <div class="radio"></div>
                    <div class="option-text">
                        <div class="option-title">${opt.label}</div>
                        ${opt.desc ? `<div class="option-desc">${opt.desc}</div>` : ''}
                    </div>
                </button>
            `).join('')}
        </div>`;
    }

    container.innerHTML = `
        <div class="question-card">
            <div class="question-header">
                <div class="category">Step ${q.step} - ${q.category}</div>
                <h2>${q.question}</h2>
                ${q.helpText ? `<div class="help-text">${q.helpText}</div>` : ''}
            </div>
            <div id="errorNotification" class="error-notification" style="display: none;">
                <i class="bi bi-exclamation-circle"></i>
                <span id="errorMessage"></span>
            </div>
            ${inputHtml}
            <div class="nav-buttons">
                <button class="nav-btn back" onclick="prevQuestion()" ${currentQuestion === 0 ? 'style="visibility:hidden"' : ''}>
                    <i class="bi bi-arrow-left"></i> Back
                </button>
                <button class="nav-btn next" onclick="nextQuestion()" id="nextBtn">
                    ${currentQuestion >= QUESTIONS.length - 1 ? 'See Results' : 'Next'} <i class="bi bi-arrow-right"></i>
                </button>
            </div>
        </div>
    `;

    // Show error if there was one
    if (formError) {
        showInlineError(formError);
        formError = null;
    }

    updateProgress();
    } catch (error) {
        console.error('Error rendering question:', error);
        const container = document.getElementById('questionContainer');
        if (container) {
            container.innerHTML = `
                <div class="question-card">
                    <div class="question-header">
                        <h2>Error Loading Question</h2>
                        <div class="help-text">An error occurred: ${error.message}. Please refresh the page.</div>
                    </div>
                    <button class="nav-btn next" onclick="location.reload()">
                        <i class="bi bi-arrow-clockwise"></i> Refresh Page
                    </button>
                </div>
            `;
        }
    }
}

function showInlineError(message) {
    const errorDiv = document.getElementById('errorNotification');
    const errorMsg = document.getElementById('errorMessage');
    if (errorDiv && errorMsg) {
        errorMsg.textContent = message;
        errorDiv.style.display = 'flex';
        errorDiv.classList.add('shake');
        setTimeout(() => errorDiv.classList.remove('shake'), 500);
    }
}

function hideInlineError() {
    const errorDiv = document.getElementById('errorNotification');
    if (errorDiv) {
        errorDiv.style.display = 'none';
    }
}

function selectOption(questionId, value, element) {
    answers[questionId] = value;
    element.parentElement.querySelectorAll('.option-btn').forEach(btn => btn.classList.remove('selected'));
    element.classList.add('selected');
    document.getElementById('nextBtn').disabled = false;
}

function toggleMultiOption(questionId, value, element) {
    if (!answers[questionId]) answers[questionId] = [];

    const index = answers[questionId].indexOf(value);
    if (index > -1) {
        answers[questionId].splice(index, 1);
        element.classList.remove('selected');
    } else {
        // If selecting "none", clear other selections
        if (value === 'none') {
            answers[questionId] = ['none'];
            element.parentElement.querySelectorAll('.option-btn').forEach(btn => btn.classList.remove('selected'));
            element.classList.add('selected');
        } else {
            // Remove "none" if selecting something else
            const noneIndex = answers[questionId].indexOf('none');
            if (noneIndex > -1) {
                answers[questionId].splice(noneIndex, 1);
                element.parentElement.querySelector('[onclick*="none"]')?.classList.remove('selected');
            }
            answers[questionId].push(value);
            element.classList.add('selected');
        }
    }
}

function searchOccupations(query) {
    const results = document.getElementById('searchResults');
    if (query.length < 2) { results.classList.remove('show'); return; }

    const matches = NOC_DATABASE.filter(noc =>
        noc.title.toLowerCase().includes(query.toLowerCase()) ||
        noc.code.includes(query)
    ).slice(0, 8);

    if (matches.length === 0) {
        results.innerHTML = '<div class="search-result-item">No matching occupations found</div>';
    } else {
        results.innerHTML = matches.map(noc => `
            <div class="search-result-item" onclick="selectOccupation('${noc.code}', '${noc.title}', ${noc.teer}, '${noc.category}')">
                <span class="noc-code">${noc.code}</span>
                <span class="noc-title"> - ${noc.title}</span>
                <div class="noc-teer">TEER ${noc.teer} | ${noc.category}</div>
            </div>
        `).join('');
    }
    results.classList.add('show');
}

function selectOccupation(code, title, teer, category) {
    selectedOccupation = { code, title, teer, category };
    answers['occupation'] = code;
    answers['occupation_teer'] = teer;
    answers['occupation_category'] = category;

    document.getElementById('searchResults').classList.remove('show');
    document.getElementById('occupationSearch').value = title;
    document.getElementById('selectedOccupation').style.display = 'block';
    document.getElementById('selectedOccTitle').textContent = `${title} (NOC ${code})`;
    document.getElementById('selectedOccDetails').textContent = ` - TEER ${teer}, ${category}`;
    document.getElementById('nextBtn').disabled = false;
}

function nextQuestion() {
    // Validate current question
    const q = QUESTIONS[currentQuestion];
    if (q) {
        // Skip validation for optional fields
        if (q.optional && !answers[q.id]) {
            hideInlineError();
            currentQuestion++;
            renderQuestion();
            return;
        }

        // Check if this question requires an answer
        if (q.type === 'search') {
            if (!answers['occupation']) {
                showInlineError('Please select your occupation from the list');
                return;
            }
        } else if (q.type === 'email') {
            const email = answers[q.id] || '';
            if (!email) {
                showInlineError('Please enter your email address');
                return;
            }
            const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
            if (!emailRegex.test(email)) {
                showInlineError('Please enter a valid email address');
                return;
            }
        } else if (q.type === 'phone') {
            // Phone is typically optional, but validate format if provided
            const phone = answers[q.id] || '';
            if (phone && phone.length < 7) {
                showInlineError('Please enter a valid phone number');
                return;
            }
        } else if (q.type === 'salary' || q.type === 'funds') {
            const amount = answers[q.id] || '';
            if (!q.optional && !amount) {
                showInlineError('Please enter an amount');
                return;
            }
            if (amount && (isNaN(amount) || parseFloat(amount) < 0)) {
                showInlineError('Please enter a valid amount');
                return;
            }
        } else if (q.type === 'date') {
            const date = answers[q.id] || '';
            if (!q.optional && !date) {
                showInlineError('Please select a date');
                return;
            }
        } else if (q.multiSelect) {
            // Multi-select is optional, allow continuing without selection
        } else if (!answers[q.id]) {
            showInlineError('Please select an option to continue');
            return;
        }
    }

    hideInlineError();
    currentQuestion++;
    renderQuestion();
}

// Check date validity for language test expiry (2 year validity)
function checkDateValidity(questionId, dateValue) {
    const warningDiv = document.getElementById('dateWarning');
    if (!warningDiv || !dateValue) {
        if (warningDiv) warningDiv.style.display = 'none';
        return;
    }

    const testDate = new Date(dateValue);
    const today = new Date();
    const twoYearsAgo = new Date();
    twoYearsAgo.setFullYear(today.getFullYear() - 2);

    const expiryDate = new Date(testDate);
    expiryDate.setFullYear(testDate.getFullYear() + 2);

    if (testDate > today) {
        warningDiv.className = 'date-warning';
        warningDiv.innerHTML = '<i class="bi bi-exclamation-circle"></i> Future date entered - please enter when you took the test';
        warningDiv.style.display = 'flex';
    } else if (testDate < twoYearsAgo) {
        warningDiv.className = 'date-warning expired';
        warningDiv.innerHTML = '<i class="bi bi-exclamation-triangle"></i> Your test has EXPIRED. Language tests are valid for 2 years only. You need to retake the test.';
        warningDiv.style.display = 'flex';
        answers['test_expired'] = true;
    } else {
        const monthsRemaining = Math.floor((expiryDate - today) / (1000 * 60 * 60 * 24 * 30));
        answers['test_expired'] = false;
        if (monthsRemaining <= 3) {
            warningDiv.className = 'date-warning';
            warningDiv.innerHTML = `<i class="bi bi-exclamation-circle"></i> Your test expires in ${monthsRemaining} month${monthsRemaining !== 1 ? 's' : ''}. Submit your application soon or book a new test.`;
            warningDiv.style.display = 'flex';
        } else if (monthsRemaining <= 6) {
            warningDiv.className = 'date-warning valid';
            warningDiv.innerHTML = `<i class="bi bi-check-circle"></i> Valid for ${monthsRemaining} more months (expires ${expiryDate.toLocaleDateString()})`;
            warningDiv.style.display = 'flex';
        } else {
            warningDiv.className = 'date-warning valid';
            warningDiv.innerHTML = `<i class="bi bi-check-circle"></i> Valid until ${expiryDate.toLocaleDateString()}`;
            warningDiv.style.display = 'flex';
        }
    }
}

function prevQuestion() {
    if (currentQuestion > 0) { currentQuestion--; renderQuestion(); }
}

function updateProgress() {
    const steps = document.querySelectorAll('.step');
    const currentStep = QUESTIONS[currentQuestion]?.step || 10;

    steps.forEach((step, i) => {
        const stepNum = i + 1;
        step.classList.remove('active', 'completed');
        if (stepNum < currentStep) step.classList.add('completed');
        else if (stepNum === currentStep) step.classList.add('active');
    });
}

// Helper: Convert test scores to CLB
function getLowestCLB() {
    const test = answers.english_test;
    if (!test || test === 'none') return 0;

    // Map test scores to CLB
    const ieltsToClb = { '4.0': 4, '4.5': 4, '5.0': 5, '5.5': 6, '6.0': 7, '6.5': 8, '7.0': 9, '7.5': 9, '8.0': 10, '8.0+': 10, '8.5+': 10, '3.5': 4 };
    const celpipToClb = { '4': 4, '5': 5, '6': 6, '7': 7, '8': 8, '9': 9, '10+': 10 };
    const pteToClb = {
        // Speaking
        '42-50': 4, '51-58': 5, '59-67': 6, '68-75': 7, '76-83': 8, '84-88': 9, '89+': 10,
        // Listening
        '28-32': 4, '33-38': 5, '39-49': 6, '50-59': 7, '60-70': 8, '71-81': 9, '82+': 10,
        // Reading
        '33-40': 4, '41-50': 5, '51-59': 6, '60-68': 7, '69-77': 8, '78-87': 9, '88+': 10,
        // Writing
        '41-50': 4, '51-59': 5, '60-68': 6, '69-78': 7, '79-87': 8, '88-89': 9, '90': 10
    };

    let clbScores = [];

    if (test === 'ielts') {
        const scores = [answers.ielts_speaking, answers.ielts_listening, answers.ielts_reading, answers.ielts_writing];
        clbScores = scores.map(s => ieltsToClb[s] || 0).filter(s => s > 0);
    } else if (test === 'celpip') {
        const scores = [answers.celpip_speaking, answers.celpip_listening, answers.celpip_reading, answers.celpip_writing];
        clbScores = scores.map(s => celpipToClb[s] || 0).filter(s => s > 0);
    } else if (test === 'pte') {
        const scores = [answers.pte_speaking, answers.pte_listening, answers.pte_reading, answers.pte_writing];
        clbScores = scores.map(s => pteToClb[s] || 0).filter(s => s > 0);
    }

    return clbScores.length === 4 ? Math.min(...clbScores) : 0;
}

// Calculate CRS Score
function calculateCRS() {
    let score = 0;
    const hasSpouse = answers.spouse_coming === 'yes';
    const clb = getLowestCLB();

    // Age points
    const agePoints = { '18-24': hasSpouse ? 90 : 99, '25-29': hasSpouse ? 100 : 110,
        '30-34': hasSpouse ? 95 : 105, '35-39': hasSpouse ? 77 : 85,
        '40-44': hasSpouse ? 45 : 50, '45-49': hasSpouse ? 20 : 25, '50+': 0 };
    score += agePoints[answers.age] || 0;

    // Education points
    const eduPoints = { none: 0, highschool: hasSpouse ? 28 : 30, oneyear: hasSpouse ? 84 : 90,
        twoyear: hasSpouse ? 91 : 98, bachelors: hasSpouse ? 112 : 120,
        two_degrees: hasSpouse ? 119 : 128, masters: hasSpouse ? 126 : 135, phd: hasSpouse ? 140 : 150 };
    score += eduPoints[answers.education_level] || 0;

    // Language points (based on lowest CLB from all abilities)
    const langPoints = { 4: 24, 5: 32, 6: 40, 7: 60, 8: 76, 9: 100, 10: 124 };
    score += langPoints[clb] || 0;

    // Canadian experience
    const canExpPoints = { none: 0, '1': 40, '2': 53, '3': 64, '4': 72, '5_plus': 80 };
    score += canExpPoints[answers.canadian_experience] || 0;

    // Spouse factors
    if (hasSpouse) {
        const spouseEduPoints = { highschool: 0, oneyear: 2, twoyear: 4, bachelors: 6, masters_plus: 10 };
        score += spouseEduPoints[answers.spouse_education] || 0;
        const spouseLangPoints = { none: 0, '4': 0, '5_6': 3, '7_8': 5, '9_plus': 10 };
        score += spouseLangPoints[answers.spouse_language] || 0;
        const spouseExpPoints = { none: 0, '1': 5, '2_plus': 10 };
        score += spouseExpPoints[answers.spouse_experience] || 0;
    }

    // Bonus: Sibling in Canada
    if (answers.family_in_canada === 'sibling') score += 15;

    // Bonus: Canadian education
    if (answers.education_country === 'canada') {
        const canEduBonus = { oneyear: 15, twoyear: 15, threeyear: 30, masters: 30, phd: 30 };
        score += canEduBonus[answers.canadian_edu_level] || 0;
    }

    // Bonus: French
    if (answers.french_level === 'nclc7_plus') score += 50;
    else if (answers.french_level === 'nclc5_6') score += 25;

    // Job offer bonus
    if (answers.job_offer === 'yes' && (answers.job_lmia === 'lmia_approved' || answers.job_lmia === 'lmia_exempt')) {
        score += answers.job_noc_teer === '0' ? 200 : 50;
    }

    return Math.min(score, 1200);
}

function showResults() {
    document.getElementById('questionContainer').style.display = 'none';
    document.querySelector('.progress-container').style.display = 'none';
    document.getElementById('resultsSection').classList.add('show');

    const crsScore = calculateCRS();
    document.getElementById('crsScore').textContent = crsScore;

    renderProfileSummary();
    renderWarnings();
    renderCategoryDraws();          // Category-based Express Entry draws
    renderNOCPathways();            // NOC-specific pathway recommendations
    renderFamilySponsorship();      // Family sponsorship options
    renderProgramEligibility(crsScore);
    renderProvincialPathways();
    renderImprovements(crsScore);
    renderAlternativePathways();
    renderCareerTransitions();
    renderCostCalculator();         // NEW: Government fees breakdown
    renderDocumentChecklist();      // NEW: Required documents per program
    renderTimeline();               // NEW: Processing timeline estimator
    renderAllPathways();            // NEW: Comprehensive pathways overview
}

function renderProfileSummary() {
    const grid = document.getElementById('profileGrid');
    const clb = getLowestCLB();

    // Format language display based on test type
    let langDisplay = 'No test';
    if (clb > 0) {
        const testName = answers.english_test === 'ielts' ? 'IELTS' : answers.english_test === 'celpip' ? 'CELPIP' : answers.english_test === 'pte' ? 'PTE' : '';
        langDisplay = `${testName} (CLB ${clb})`;
        if (answers.test_expired) langDisplay += ' (EXPIRED)';
    }

    // Format job offer display
    let jobOfferDisplay = 'None';
    if (answers.job_offer === 'yes') {
        const lmiaStatus = answers.job_lmia === 'lmia_approved' ? 'LMIA' :
                          answers.job_lmia === 'lmia_exempt' ? 'Exempt' : 'No LMIA';
        jobOfferDisplay = `Yes (${lmiaStatus})`;
        if (answers.job_salary) {
            jobOfferDisplay += ` - $${parseInt(answers.job_salary).toLocaleString()}/yr`;
        }
    } else if (answers.job_offer === 'in_progress') {
        jobOfferDisplay = 'In progress';
    }

    // Format occupation display
    let occupationDisplay = answers.occupation_category || 'N/A';
    if (selectedOccupation) {
        occupationDisplay = `${selectedOccupation.title} (TEER ${selectedOccupation.teer})`;
    }

    const items = [
        { label: 'Age', value: answers.age || 'N/A' },
        { label: 'Education', value: formatEducation(answers.education_level) },
        { label: 'Occupation', value: occupationDisplay },
        { label: 'Canadian Exp', value: formatExperience(answers.canadian_experience) },
        { label: 'Foreign Exp', value: formatExperience(answers.foreign_experience) },
        { label: 'English', value: langDisplay },
        { label: 'French', value: formatFrench(answers.french_level) },
        { label: 'Job Offer', value: jobOfferDisplay },
        { label: 'Target Province', value: formatProvince(answers.target_province) }
    ];

    // Add email if provided (for lead capture display)
    if (answers.email) {
        items.unshift({ label: 'Email', value: answers.email });
    }

    grid.innerHTML = items.map(i => `
        <div class="profile-item"><div class="label">${i.label}</div><div class="value">${i.value}</div></div>
    `).join('');
}

function formatEducation(level) {
    const labels = {
        none: 'Less than high school',
        highschool: 'High school',
        oneyear: '1-year certificate',
        twoyear: '2-year diploma',
        bachelors: "Bachelor's degree",
        two_degrees: 'Two degrees',
        masters: "Master's degree",
        phd: 'Doctoral (PhD)'
    };
    return labels[level] || level || 'N/A';
}

function formatExperience(exp) {
    if (!exp || exp === 'none') return 'None';
    if (exp === '5_plus' || exp === '6_plus') return '5+ years';
    return `${exp} year${exp !== '1' ? 's' : ''}`;
}

function formatFrench(level) {
    const labels = {
        nclc7_plus: 'NCLC 7+ (Strong)',
        nclc5_6: 'NCLC 5-6 (Moderate)',
        below_nclc5: 'Below NCLC 5',
        none: 'None'
    };
    return labels[level] || 'Not tested';
}

function formatProvince(prov) {
    const labels = {
        bc: 'British Columbia',
        ontario: 'Ontario',
        alberta: 'Alberta',
        saskatchewan: 'Saskatchewan',
        manitoba: 'Manitoba',
        nova_scotia: 'Nova Scotia',
        new_brunswick: 'New Brunswick',
        pei: 'Prince Edward Island',
        newfoundland: 'Newfoundland & Labrador',
        any: 'Open to any'
    };
    return labels[prov] || prov || 'Any';
}

function renderWarnings() {
    const section = document.getElementById('warningsSection');
    const warnings = [];
    const clb = getLowestCLB();

    // Language test warnings
    if (answers.english_test === 'none' || clb === 0) {
        warnings.push({ type: 'urgent', issue: 'No language test completed', action: 'Language test is REQUIRED for Express Entry. Book IELTS, CELPIP, or PTE Core immediately.' });
    } else if (answers.test_expired) {
        warnings.push({ type: 'urgent', issue: 'Your language test has EXPIRED', action: 'Language tests are valid for 2 years only. Book a new test immediately before submitting any application.' });
    } else if (answers.english_test_date) {
        // Check if test is expiring soon
        const testDate = new Date(answers.english_test_date);
        const today = new Date();
        const expiryDate = new Date(testDate);
        expiryDate.setFullYear(testDate.getFullYear() + 2);
        const monthsRemaining = Math.floor((expiryDate - today) / (1000 * 60 * 60 * 24 * 30));

        if (monthsRemaining <= 3 && monthsRemaining > 0) {
            warnings.push({
                type: 'concern',
                issue: `Your language test expires in ${monthsRemaining} month${monthsRemaining !== 1 ? 's' : ''}`,
                action: 'Submit your Express Entry profile soon, or book a new test to avoid delays in your application.'
            });
        }
    }

    // ECA warning
    if (answers.eca_status === 'no' && answers.education_country === 'foreign') {
        warnings.push({ type: 'urgent', issue: 'No ECA completed', action: 'Educational Credential Assessment is REQUIRED. Apply to WES, IQAS, or other designated organization.' });
    }

    // Criminal history with specific details
    if (answers.criminal_history && answers.criminal_history !== 'no') {
        let criminalAction = 'Consult an immigration lawyer.';
        if (answers.criminal_severity === 'minor') {
            criminalAction = 'Minor offenses may require a Rehabilitation application if >5 years have passed, or Criminal Record Suspension.';
        } else if (answers.criminal_severity === 'serious') {
            criminalAction = 'Serious offenses may make you inadmissible. You may need to apply for Criminal Rehabilitation (min 5 years since completion of sentence).';
        } else if (answers.criminal_severity === 'dui') {
            criminalAction = 'DUI is considered a serious offense in Canada. You may need a Temporary Resident Permit or Criminal Rehabilitation.';
        }
        warnings.push({ type: 'concern', issue: 'Criminal history may affect admissibility', action: criminalAction });
    }

    // Previous refusals with details
    if (answers.previous_refusal && answers.previous_refusal !== 'no') {
        let refusalAction = 'Address refusal reasons in your new application. Consider hiring a licensed RCIC.';
        if (answers.refusal_type === 'study_permit') {
            refusalAction = 'Study permit refusal usually cites insufficient ties to home country or inadequate finances. Strengthen these areas in your new application.';
        } else if (answers.refusal_type === 'work_permit') {
            refusalAction = 'Work permit refusals may be due to LMIA issues or job offer concerns. Ensure your employer follows proper procedures.';
        } else if (answers.refusal_type === 'visitor_visa') {
            refusalAction = 'Visitor visa refusals are common. Focus on proving strong ties to home country and sufficient funds for return.';
        } else if (answers.refusal_type === 'pr') {
            refusalAction = 'PR refusals are serious. Review your GCMS notes and address specific concerns with professional help.';
        }

        if (answers.refusal_recency === 'recent') {
            refusalAction += ' Recent refusals (within 6 months) may require waiting or significant profile changes.';
        }

        if (answers.other_country_refusal === 'yes') {
            refusalAction += ' Refusals from US, UK, Australia, or Schengen may be shared and could affect your Canadian application.';
        }

        warnings.push({ type: 'concern', issue: `Previous ${answers.refusal_type?.replace('_', ' ') || 'visa'} refusal on record`, action: refusalAction });
    }

    // Medical issues
    if (answers.medical_issues && answers.medical_issues !== 'no') {
        warnings.push({
            type: 'concern',
            issue: 'Medical conditions may affect admissibility',
            action: 'Conditions requiring excessive healthcare costs (>$24,057/year) may cause medical inadmissibility. Consult an immigration medical practitioner.'
        });
    }

    // Occupation TEER level
    if (answers.occupation_teer >= 4) {
        warnings.push({ type: 'info', issue: 'Your occupation (TEER 4/5) is NOT eligible for Express Entry', action: 'See Career Transition recommendations below, or consider Study → Work permit pathway.' });
    }

    // Settlement funds warning
    if (answers.settlement_funds === 'difficult' || answers.funds_source === 'loans') {
        warnings.push({
            type: 'info',
            issue: 'Settlement funds may be insufficient',
            action: 'You need proof of funds (single: ~$14,690 CAD, family of 4: ~$27,315 CAD). Loans are NOT accepted as proof of funds.'
        });
    }

    // Documents not ready warning
    const docsReady = answers.documents_ready || [];
    const criticalDocs = ['passport', 'eca', 'language_test'];
    const missingCritical = criticalDocs.filter(doc => !docsReady.includes(doc));
    if (missingCritical.length > 0 && answers.english_test && answers.english_test !== 'none') {
        const docNames = {
            passport: 'Valid passport',
            eca: 'ECA report',
            language_test: 'Language test results'
        };
        warnings.push({
            type: 'info',
            issue: 'Critical documents not ready',
            action: `Missing: ${missingCritical.map(d => docNames[d]).join(', ')}. Ensure these are ready before creating your Express Entry profile.`
        });
    }

    if (warnings.length === 0) {
        section.innerHTML = '';
        return;
    }

    section.innerHTML = `
        <h3 class="section-title"><i class="bi bi-exclamation-triangle"></i> Important Warnings</h3>
        ${warnings.map(w => `
            <div class="warning-card ${w.type}">
                <i class="bi bi-exclamation-triangle-fill warning-icon"></i>
                <div>
                    <div class="warning-issue">${w.issue}</div>
                    <div class="warning-action">${w.action}</div>
                </div>
            </div>
        `).join('')}
    `;
}

function renderProgramEligibility(crsScore) {
    const container = document.getElementById('programResults');
    const clb = getLowestCLB();
    const canExp = answers.canadian_experience !== 'none' ? parseInt(answers.canadian_experience) || 0 : 0;
    const foreignExp = answers.foreign_experience !== 'none' ? parseInt(answers.foreign_experience) || 0 : 0;
    const teer = answers.occupation_teer || 5;

    const programs = [
        {
            name: 'Federal Skilled Worker (FSW)',
            reqs: [
                { text: 'CLB 7+ in all abilities', met: clb >= 7 },
                { text: '1+ year skilled work experience', met: foreignExp >= 1 || canExp >= 1 },
                { text: 'Post-secondary education', met: answers.education_level !== 'highschool' && answers.education_level !== 'none' },
                { text: 'ECA completed (if foreign education)', met: answers.education_country === 'canada' || answers.eca_status === 'yes' },
                { text: 'Proof of settlement funds', met: answers.settlement_funds !== 'difficult' }
            ],
            tip: crsScore < 510 ? 'CRS score below recent cutoffs (~510-530). Consider PNP for +600 points.' : 'Your score is competitive for recent draws!'
        },
        {
            name: 'Canadian Experience Class (CEC)',
            reqs: [
                { text: '1+ year Canadian work experience (last 3 years)', met: canExp >= 1 },
                { text: 'CLB 7 for TEER 0/1, CLB 5 for TEER 2/3', met: (teer <= 1 && clb >= 7) || (teer >= 2 && clb >= 5) },
                { text: 'Skilled occupation (TEER 0-3)', met: teer <= 3 }
            ],
            tip: canExp >= 1 ? 'CEC is often easier than FSW if you have Canadian experience.' : 'Get Canadian work experience via PGWP or LMIA work permit.'
        },
        {
            name: 'Federal Skilled Trades (FST)',
            reqs: [
                { text: 'Trade certificate or 2 years experience', met: answers.trade_cert !== 'no' },
                { text: 'CLB 5 Speaking/Listening, CLB 4 Reading/Writing', met: clb >= 5 },
                { text: 'Job offer or certificate of qualification', met: answers.job_offer === 'yes' || answers.trade_cert !== 'no' }
            ],
            tip: 'Best for Red Seal certified tradespeople with job offers.'
        }
    ];

    container.innerHTML = programs.map(prog => {
        const metCount = prog.reqs.filter(r => r.met).length;
        const status = metCount === prog.reqs.length ? 'eligible' : metCount >= prog.reqs.length - 1 ? 'likely' : 'not-eligible';
        const statusText = status === 'eligible' ? 'Likely Eligible' : status === 'likely' ? 'May Qualify' : 'Not Eligible';

        return `
            <div class="program-card ${status}">
                <div class="program-header">
                    <div class="program-name">${prog.name}</div>
                    <span class="eligibility-badge ${status}">${statusText}</span>
                </div>
                <div class="requirements">
                    ${prog.reqs.map(r => `
                        <div class="req-item">
                            <i class="bi bi-${r.met ? 'check-circle-fill' : 'x-circle-fill'}"></i>
                            <span>${r.text}</span>
                        </div>
                    `).join('')}
                </div>
                <div class="program-recommendation">${prog.tip}</div>
            </div>
        `;
    }).join('');
}

function renderProvincialPathways() {
    const container = document.getElementById('provincialResults');
    const category = answers.occupation_category || 'other';
    const province = answers.target_province || 'any';
    const provincialConnections = Array.isArray(answers.provincial_connection) ? answers.provincial_connection : [];
    const hasStudiedInProvince = provincialConnections.includes('study');
    const hasWorkedInProvince = provincialConnections.includes('work');
    const hasFamily = provincialConnections.includes('family');
    const clb = getLowestCLB();

    // Get all provincial scores
    const scores = getAllProvincialScores();

    const pathways = [];

    // British Columbia - SIRS Points System (200 max)
    const bcScore = scores.bc;
    pathways.push({
        province: 'British Columbia',
        stream: 'BC PNP Skills Immigration',
        match: `Your BC SIRS score: ${bcScore.score}/${bcScore.max} (Draws: ~${bcScore.minDraw}+)`,
        benefit: '+600 CRS, weekly Tech draws',
        eligible: bcScore.score >= bcScore.minDraw,
        score: bcScore.score,
        requirements: ['Job offer from BC employer', 'NOC TEER 0-3', 'CLB 4+'],
        scoreDetails: { current: bcScore.score, required: bcScore.minDraw, max: bcScore.max }
    });

    // Saskatchewan - 110 points (60 minimum)
    const skScore = scores.sk;
    pathways.push({
        province: 'Saskatchewan',
        stream: 'SINP International Skilled Worker',
        match: `Your SINP score: ${skScore.score}/${skScore.max} (60 required)`,
        benefit: 'Points-based, no job offer needed for OID',
        eligible: skScore.score >= skScore.minRequired,
        score: skScore.score,
        requirements: ['60+ points on grid', 'In-demand occupation OR job offer', 'CLB 4+'],
        scoreDetails: { current: skScore.score, required: skScore.minRequired, max: skScore.max }
    });

    // Manitoba - 1000 points (700+ competitive)
    const mbScore = scores.mb;
    pathways.push({
        province: 'Manitoba',
        stream: 'MPNP Skilled Worker',
        match: `Your MPNP score: ${mbScore.score}/${mbScore.max} (700+ competitive)`,
        benefit: 'Strong adaptability points for connections',
        eligible: mbScore.score >= mbScore.competitive,
        score: mbScore.score,
        requirements: ['Manitoba connection required', 'CLB 4+', '6 months work experience'],
        scoreDetails: { current: mbScore.score, required: mbScore.competitive, max: mbScore.max }
    });

    // Alberta - 100 points
    const abScore = scores.ab;
    pathways.push({
        province: 'Alberta',
        stream: 'AAIP Alberta Opportunity',
        match: `Your AAIP score: ${abScore.score}/${abScore.max} (Draws: ~${abScore.typicalDraw}+)`,
        benefit: 'Sector-driven, Alberta experience valued',
        eligible: abScore.score >= abScore.typicalDraw,
        score: abScore.score,
        requirements: ['Alberta work/study preferred', 'CLB 4+', 'Valid job offer helps'],
        scoreDetails: { current: abScore.score, required: abScore.typicalDraw, max: abScore.max }
    });

    // New Brunswick - 100 points (67 required)
    const nbScore = scores.nb;
    pathways.push({
        province: 'New Brunswick',
        stream: 'NBPNP Express Entry',
        match: `Your NBPNP score: ${nbScore.score}/${nbScore.max} (67 required)`,
        benefit: 'Atlantic province, employer-driven',
        eligible: nbScore.score >= nbScore.minRequired,
        score: nbScore.score,
        requirements: ['67+ points', 'CLB 7+', 'NB work experience preferred'],
        scoreDetails: { current: nbScore.score, required: nbScore.minRequired, max: nbScore.max }
    });

    // PEI - 100 points (67 required)
    const peiScore = scores.pei;
    pathways.push({
        province: 'Prince Edward Island',
        stream: 'PEI PNP Express Entry',
        match: `Your PEI score: ${peiScore.score}/${peiScore.max} (67 required)`,
        benefit: 'No job offer required, bilingual bonus',
        eligible: peiScore.score >= peiScore.minRequired,
        score: peiScore.score,
        requirements: ['67+ points', 'CLB 7+', 'Express Entry profile'],
        scoreDetails: { current: peiScore.score, required: peiScore.minRequired, max: peiScore.max }
    });

    // Newfoundland & Labrador - 100 points (67 required)
    const nlScore = scores.nl;
    pathways.push({
        province: 'Newfoundland & Labrador',
        stream: 'NLPNP Express Entry',
        match: `Your NLPNP score: ${nlScore.score}/${nlScore.max} (67 required)`,
        benefit: '+600 CRS, job offer required',
        eligible: nlScore.score >= nlScore.minRequired,
        score: nlScore.score,
        requirements: ['67+ points', 'Job offer from NL employer', 'CLB 4+'],
        scoreDetails: { current: nlScore.score, required: nlScore.minRequired, max: nlScore.max }
    });

    // Ontario - CRS based (no provincial points)
    pathways.push({
        province: 'Ontario',
        stream: 'OINP Human Capital Priorities',
        match: 'Based on CRS score (400+ typical)',
        benefit: 'Category draws for Tech, Healthcare, Trades',
        eligible: true,
        score: null, // Uses CRS
        requirements: ['Active Express Entry (FSW/CEC)', "Bachelor's degree", 'CLB 7+'],
        scoreDetails: null
    });

    // Nova Scotia - CRS based (no provincial points)
    pathways.push({
        province: 'Nova Scotia',
        stream: 'NSNP Labour Market Priorities',
        match: 'Letter of Interest based on occupation',
        benefit: 'Healthcare/Trades in high demand',
        eligible: category === 'Healthcare' || category === 'Trades',
        score: null,
        requirements: ['In-demand occupation', 'Express Entry profile', 'CLB 5+'],
        scoreDetails: null
    });

    // Sort by eligibility and score
    pathways.sort((a, b) => {
        // Eligible first
        if (a.eligible && !b.eligible) return -1;
        if (!a.eligible && b.eligible) return 1;
        // Then by how close to threshold
        if (a.scoreDetails && b.scoreDetails) {
            const aRatio = a.scoreDetails.current / a.scoreDetails.required;
            const bRatio = b.scoreDetails.current / b.scoreDetails.required;
            return bRatio - aRatio;
        }
        return 0;
    });

    // Filter by target province if specified
    let displayPathways = pathways;
    if (province !== 'any') {
        const provinceMap = {
            'bc': 'British Columbia', 'ontario': 'Ontario', 'alberta': 'Alberta',
            'saskatchewan': 'Saskatchewan', 'manitoba': 'Manitoba', 'nova_scotia': 'Nova Scotia',
            'new_brunswick': 'New Brunswick', 'pei': 'Prince Edward Island', 'newfoundland': 'Newfoundland & Labrador'
        };
        const targetName = provinceMap[province];
        displayPathways = pathways.filter(p => p.province === targetName || p.eligible);
    }

    container.innerHTML = displayPathways.slice(0, 6).map((p, i) => `
        <div class="pathway-card ${i === 0 && p.eligible ? 'recommended' : ''} ${!p.eligible ? 'not-eligible' : ''}">
            ${i === 0 && p.eligible ? '<div class="pathway-badge">Best Match</div>' : ''}
            <h4>${p.province}</h4>
            <div class="pathway-stream">${p.stream}</div>
            ${p.scoreDetails ? `
                <div class="pathway-score">
                    <div class="score-bar">
                        <div class="score-fill ${p.eligible ? 'eligible' : 'not-eligible'}"
                             style="width: ${Math.min((p.scoreDetails.current / p.scoreDetails.max) * 100, 100)}%"></div>
                        <div class="score-threshold" style="left: ${(p.scoreDetails.required / p.scoreDetails.max) * 100}%"></div>
                    </div>
                    <div class="score-text">${p.scoreDetails.current} / ${p.scoreDetails.max} pts (need ${p.scoreDetails.required})</div>
                </div>
            ` : ''}
            <div class="pathway-match"><i class="bi bi-${p.eligible ? 'check-circle-fill' : 'exclamation-circle'}"></i> ${p.match}</div>
            <div class="pathway-benefit"><strong>Benefit:</strong> ${p.benefit}</div>
            <div class="pathway-requirements"><strong>Requirements:</strong> ${p.requirements.join(' • ')}</div>
            <a href="/tools/pnp-calculator" class="pathway-cta">Full PNP Calculator <i class="bi bi-arrow-right"></i></a>
        </div>
    `).join('');
}

// Calculate Newfoundland & Labrador PNP Score (67 points required)
function calculateNLPNPScore() {
    let score = 0;
    const clb = getLowestCLB();

    // Age (max 12 points)
    const agePoints = { '18-24': 10, '25-29': 12, '30-34': 12, '35-39': 10, '40-44': 8, '45-49': 4, '50+': 0 };
    score += agePoints[answers.age] || 0;

    // Education (max 25 points)
    const eduPoints = { none: 0, highschool: 5, oneyear: 15, twoyear: 19, bachelors: 21, two_degrees: 23, masters: 23, phd: 25 };
    score += eduPoints[answers.education_level] || 0;

    // Language (max 25 points) - CLB 7 = 17, CLB 8 = 19, CLB 9+ = 25
    const langPoints = { 4: 6, 5: 9, 6: 13, 7: 17, 8: 19, 9: 25, 10: 25 };
    score += langPoints[clb] || 0;

    // Work Experience (max 15 points)
    const foreignExp = answers.foreign_experience !== 'none' ? parseInt(answers.foreign_experience) || 0 : 0;
    const canExp = answers.canadian_experience !== 'none' ? parseInt(answers.canadian_experience) || 0 : 0;
    const totalExp = foreignExp + canExp;
    const expPoints = totalExp >= 5 ? 15 : totalExp >= 3 ? 11 : totalExp >= 1 ? 7 : 0;
    score += expPoints;

    // Connection to NL (max 13 points for family)
    const provincialConnections = Array.isArray(answers.provincial_connection) ? answers.provincial_connection : [];
    if (provincialConnections.includes('family')) score += 13;

    // Adaptability (up to 10 points for study/work in NL)
    if (provincialConnections.includes('study')) score += 5;
    if (provincialConnections.includes('work')) score += 5;

    return score;
}

// Calculate BC PNP SIRS Score (200 points max, draws typically 138-150)
function calculateBCPNPScore() {
    let score = 0;
    const clb = getLowestCLB();
    const provincialConnections = Array.isArray(answers.provincial_connection) ? answers.provincial_connection : [];
    const foreignExp = answers.foreign_experience !== 'none' ? parseInt(answers.foreign_experience) || 0 : 0;
    const canExp = answers.canadian_experience !== 'none' ? parseInt(answers.canadian_experience) || 0 : 0;

    // Work Experience (max 40 points)
    const totalExp = foreignExp + canExp;
    const expPoints = totalExp >= 5 ? 20 : totalExp >= 4 ? 16 : totalExp >= 3 ? 12 : totalExp >= 2 ? 8 : totalExp >= 1 ? 4 : 0;
    score += expPoints;
    // Bonus: Canadian work experience
    if (canExp >= 1) score += 10;
    // Bonus: Currently working in BC
    if (provincialConnections.includes('work')) score += 10;

    // Education (max 40 points)
    const eduPoints = { none: 0, highschool: 0, oneyear: 5, twoyear: 5, bachelors: 15, two_degrees: 15, masters: 22, phd: 27 };
    score += eduPoints[answers.education_level] || 0;
    // Bonus: BC education
    if (provincialConnections.includes('study') && answers.target_province === 'bc') score += 8;
    // Bonus: Other Canadian education
    else if (answers.education_country === 'canada') score += 6;

    // Language (max 40 points)
    const langPoints = { 4: 5, 5: 10, 6: 15, 7: 20, 8: 25, 9: 30, 10: 30 };
    score += langPoints[clb] || 0;
    // Bilingual bonus
    if (answers.french_level === 'nclc7_plus' || answers.french_level === 'nclc5_6') score += 10;

    // Job offer wage is a major factor (max 55 points) - estimate based on occupation
    // Since we don't ask wage, estimate based on TEER level
    const teer = answers.occupation_teer || 5;
    const wagePoints = teer === 0 ? 45 : teer === 1 ? 35 : teer === 2 ? 25 : teer === 3 ? 15 : 5;
    score += wagePoints;

    // Regional bonus (max 25 points) - outside Metro Vancouver
    // Can't determine without asking location, estimate 5 points average
    score += 5;

    return { score, max: 200, minDraw: 138 };
}

// Calculate Saskatchewan SINP Score (110 points max, 60 minimum required)
function calculateSINPScore() {
    let score = 0;
    const clb = getLowestCLB();
    const provincialConnections = Array.isArray(answers.provincial_connection) ? answers.provincial_connection : [];
    const foreignExp = answers.foreign_experience !== 'none' ? parseInt(answers.foreign_experience) || 0 : 0;
    const canExp = answers.canadian_experience !== 'none' ? parseInt(answers.canadian_experience) || 0 : 0;

    // Education (max 23 points)
    const eduPoints = { none: 0, highschool: 0, oneyear: 12, twoyear: 15, bachelors: 20, two_degrees: 20, masters: 23, phd: 23 };
    score += eduPoints[answers.education_level] || 0;

    // Work Experience (max 15 points)
    const totalExp = foreignExp + canExp;
    // Last 5 years (max 10)
    const recentExp = Math.min(totalExp, 5);
    const recentPoints = recentExp >= 5 ? 10 : recentExp >= 4 ? 8 : recentExp >= 3 ? 6 : recentExp >= 2 ? 4 : recentExp >= 1 ? 2 : 0;
    score += recentPoints;
    // 6-10 years ago (max 5) - assume some older experience
    if (totalExp > 5) score += Math.min(totalExp - 5, 5);

    // Language (max 20 points)
    const langPoints = { 4: 12, 5: 14, 6: 16, 7: 18, 8: 20, 9: 20, 10: 20 };
    score += langPoints[clb] || 0;
    // Second language bonus
    if (answers.french_level === 'nclc7_plus') score += 10;
    else if (answers.french_level === 'nclc5_6') score += 2;

    // Age (max 12 points)
    const agePoints = { '18-24': 8, '25-29': 12, '30-34': 12, '35-39': 10, '40-44': 10, '45-49': 8, '50+': 0 };
    score += agePoints[answers.age] || 0;

    // Connection to Saskatchewan (max 30 points)
    if (answers.job_offer === 'yes' && answers.job_province === 'saskatchewan') score += 30;
    else {
        if (provincialConnections.includes('family')) score += 20;
        if (provincialConnections.includes('work')) score += 5;
        if (provincialConnections.includes('study')) score += 5;
    }

    return { score, max: 110, minRequired: 60 };
}

// Calculate Manitoba MPNP Score (1000 points max, 60 minimum, 700+ competitive)
function calculateMPNPScore() {
    let score = 0;
    const clb = getLowestCLB();
    const provincialConnections = Array.isArray(answers.provincial_connection) ? answers.provincial_connection : [];
    const foreignExp = answers.foreign_experience !== 'none' ? parseInt(answers.foreign_experience) || 0 : 0;
    const canExp = answers.canadian_experience !== 'none' ? parseInt(answers.canadian_experience) || 0 : 0;

    // Language (max 125 points) - 25 per band for CLB 8+
    const langPoints = { 4: 48, 5: 68, 6: 80, 7: 88, 8: 100, 9: 100, 10: 100 };
    score += langPoints[clb] || 0;
    // Second language bonus
    if (answers.french_level === 'nclc7_plus' || answers.french_level === 'nclc5_6') score += 25;

    // Age (max 75 points)
    const agePoints = { '18-24': 60, '25-29': 75, '30-34': 75, '35-39': 75, '40-44': 75, '45-49': 55, '50+': 0 };
    score += agePoints[answers.age] || 0;

    // Work Experience (max 175 points)
    const totalExp = foreignExp + canExp;
    const expPoints = totalExp >= 4 ? 75 : totalExp >= 3 ? 60 : totalExp >= 2 ? 50 : totalExp >= 1 ? 40 : 0;
    score += expPoints;
    // Manitoba work experience bonus (+100)
    if (provincialConnections.includes('work') && answers.target_province === 'manitoba') score += 100;

    // Education (max 125 points)
    const eduPoints = { none: 0, highschool: 0, oneyear: 70, twoyear: 100, bachelors: 100, two_degrees: 115, masters: 125, phd: 125 };
    score += eduPoints[answers.education_level] || 0;

    // Adaptability (max 500 points)
    if (provincialConnections.includes('family')) score += 200;
    if (provincialConnections.includes('work')) score += 100;
    if (provincialConnections.includes('study')) {
        if (answers.education_level === 'twoyear' || answers.education_level === 'bachelors' ||
            answers.education_level === 'masters' || answers.education_level === 'phd') score += 100;
        else score += 50;
    }

    return { score, max: 1000, minRequired: 60, competitive: 700 };
}

// Calculate Alberta AAIP Score (100 points max)
function calculateAAIPScore() {
    let score = 0;
    const clb = getLowestCLB();
    const provincialConnections = Array.isArray(answers.provincial_connection) ? answers.provincial_connection : [];
    const foreignExp = answers.foreign_experience !== 'none' ? parseInt(answers.foreign_experience) || 0 : 0;
    const canExp = answers.canadian_experience !== 'none' ? parseInt(answers.canadian_experience) || 0 : 0;

    // Education (max 12 points) - flat 12 for any post-secondary
    if (['oneyear', 'twoyear', 'bachelors', 'two_degrees', 'masters', 'phd'].includes(answers.education_level)) {
        score += 12;
    }

    // Alberta education bonus (max 10 points)
    if (provincialConnections.includes('study') && answers.target_province === 'alberta') score += 10;

    // Language (max 13 points)
    if (clb >= 6) score += 10;
    else if (clb >= 5) score += 5;
    // French bonus
    if (answers.french_level === 'nclc7_plus' || answers.french_level === 'nclc5_6') score += 3;

    // Work Experience (max 21 points)
    const totalExp = foreignExp + canExp;
    if (totalExp >= 1) score += 11;
    else if (totalExp >= 0.5) score += 6;
    // Canadian/Alberta work experience bonus
    if (provincialConnections.includes('work') && answers.target_province === 'alberta') score += 10;
    else if (canExp >= 0.5) score += 5;

    // Age (max 5 points) - only 21-34 gets points
    if (['25-29', '30-34'].includes(answers.age)) score += 5;
    else if (answers.age === '18-24') score += 5;

    // Family in Alberta (max 8 points)
    if (provincialConnections.includes('family')) score += 8;

    // Job offer (max 16 points)
    if (answers.job_offer === 'yes' && answers.job_province === 'alberta') score += 10;

    return { score, max: 100, typicalDraw: 60 };
}

// Calculate New Brunswick NBPNP Score (100 points, 67 required)
function calculateNBPNPScore() {
    let score = 0;
    const clb = getLowestCLB();
    const provincialConnections = Array.isArray(answers.provincial_connection) ? answers.provincial_connection : [];
    const foreignExp = answers.foreign_experience !== 'none' ? parseInt(answers.foreign_experience) || 0 : 0;
    const canExp = answers.canadian_experience !== 'none' ? parseInt(answers.canadian_experience) || 0 : 0;

    // Education (max 25 points)
    const eduPoints = { none: 0, highschool: 5, oneyear: 15, twoyear: 19, bachelors: 21, two_degrees: 22, masters: 23, phd: 25 };
    score += eduPoints[answers.education_level] || 0;

    // Language (max 28 points) - CLB 7 minimum required
    if (clb >= 9) score += 24;
    else if (clb >= 8) score += 20;
    else if (clb >= 7) score += 16;
    // Second language
    if (answers.french_level === 'nclc7_plus' || answers.french_level === 'nclc5_6') score += 4;

    // Work Experience (max 15 points)
    const totalExp = foreignExp + canExp;
    const expPoints = totalExp >= 6 ? 15 : totalExp >= 4 ? 13 : totalExp >= 2 ? 11 : totalExp >= 1 ? 9 : 0;
    score += expPoints;

    // Age (max 12 points)
    const agePoints = { '18-24': 12, '25-29': 12, '30-34': 12, '35-39': 9, '40-44': 5, '45-49': 2, '50+': 0 };
    score += agePoints[answers.age] || 0;

    // Job offer in NB (max 10 points)
    if (answers.job_offer === 'yes' && answers.job_province === 'new_brunswick') score += 10;

    // Adaptability (max 10 points)
    let adaptability = 0;
    if (provincialConnections.includes('family')) adaptability += 5;
    if (provincialConnections.includes('work')) adaptability += 5;
    if (provincialConnections.includes('study')) adaptability += 5;
    if (answers.french_level !== 'none') adaptability += 5; // Spouse language estimate
    score += Math.min(adaptability, 10);

    return { score, max: 100, minRequired: 67 };
}

// Calculate PEI PNP Score (100 points, 67 required)
function calculatePEIPNPScore() {
    let score = 0;
    const clb = getLowestCLB();
    const provincialConnections = Array.isArray(answers.provincial_connection) ? answers.provincial_connection : [];
    const foreignExp = answers.foreign_experience !== 'none' ? parseInt(answers.foreign_experience) || 0 : 0;
    const canExp = answers.canadian_experience !== 'none' ? parseInt(answers.canadian_experience) || 0 : 0;

    // Age (max 12 points)
    const agePoints = { '18-24': 12, '25-29': 12, '30-34': 12, '35-39': 9, '40-44': 5, '45-49': 2, '50+': 0 };
    score += agePoints[answers.age] || 0;

    // Education (max 25 points)
    const eduPoints = { none: 0, highschool: 5, oneyear: 15, twoyear: 19, bachelors: 21, two_degrees: 22, masters: 23, phd: 25 };
    score += eduPoints[answers.education_level] || 0;

    // Language (max 28 points)
    if (clb >= 9) score += 24;
    else if (clb >= 8) score += 20;
    else if (clb >= 7) score += 16;
    else if (clb >= 6) score += 12;
    // Bilingual bonus
    if (answers.french_level === 'nclc7_plus' || answers.french_level === 'nclc5_6') score += 10;

    // Work Experience (max 15 points)
    const totalExp = foreignExp + canExp;
    const expPoints = totalExp >= 6 ? 15 : totalExp >= 4 ? 13 : totalExp >= 2 ? 11 : totalExp >= 1 ? 9 : 0;
    score += expPoints;

    // Job offer in PEI (max 10 points) - Note: PEI doesn't require job offer
    if (answers.job_offer === 'yes' && answers.job_province === 'pei') score += 10;

    // Adaptability (max 10 points)
    let adaptability = 0;
    if (provincialConnections.includes('family')) adaptability += 5;
    if (provincialConnections.includes('study')) adaptability += 5;
    if (canExp >= 1) adaptability += 5;
    score += Math.min(adaptability, 10);

    return { score, max: 100, minRequired: 67 };
}

// Get all provincial scores for display
function getAllProvincialScores() {
    return {
        bc: calculateBCPNPScore(),
        sk: calculateSINPScore(),
        mb: calculateMPNPScore(),
        ab: calculateAAIPScore(),
        nb: calculateNBPNPScore(),
        pei: calculatePEIPNPScore(),
        nl: { score: calculateNLPNPScore(), max: 100, minRequired: 67 }
    };
}

function renderImprovements(currentScore) {
    const container = document.getElementById('improvementResults');
    const improvements = [];

    const clb = getLowestCLB();
    if (clb < 9 && clb > 0) {
        improvements.push({ action: `Improve English to CLB ${clb + 1}`, details: '2-3 months prep, $350 test fee', gain: '+16-24 CRS' });
    }
    if (clb === 0) {
        improvements.push({ action: 'Complete a language test (IELTS/CELPIP/PTE)', details: 'Required for Express Entry', gain: 'Essential' });
    }
    if (answers.french_level === 'none' || !answers.french_level) {
        improvements.push({ action: 'Learn French to NCLC 7', details: '6-12 months study', gain: '+50 CRS + French draws' });
    }
    if (answers.canadian_experience === 'none') {
        improvements.push({ action: 'Get 1 year Canadian work experience', details: 'PGWP, LMIA, or IEC', gain: '+40 CRS' });
    }
    if (answers.job_offer !== 'yes') {
        improvements.push({ action: 'Obtain LMIA-supported job offer', details: 'Apply to Canadian employers', gain: '+50-200 CRS' });
    }
    improvements.push({ action: 'Provincial Nomination', details: 'Apply to PNP programs', gain: '+600 CRS' });

    container.innerHTML = improvements.slice(0, 5).map(imp => `
        <div class="improvement-card">
            <div>
                <div class="improvement-action">${imp.action}</div>
                <div class="improvement-details">${imp.details}</div>
            </div>
            <div class="improvement-gain">${imp.gain}</div>
        </div>
    `).join('');
}

function renderAlternativePathways() {
    const container = document.getElementById('alternativeResults');

    // Filter pathways based on user's profile
    const relevantPathways = ALTERNATIVE_PATHWAYS.filter(alt => {
        try {
            return alt.condition ? alt.condition(answers) : true;
        } catch(e) {
            return true;
        }
    });

    // Sort by relevance (CEC direct first if applicable, then others)
    relevantPathways.sort((a, b) => {
        if (a.id === 'cec_direct') return -1;
        if (b.id === 'cec_direct') return 1;
        return 0;
    });

    // Show up to 6 relevant pathways
    container.innerHTML = relevantPathways.slice(0, 6).map(alt => `
        <div class="alt-pathway ${alt.id === 'cec_direct' ? 'recommended' : ''}">
            ${alt.id === 'cec_direct' ? '<div class="badge">Recommended for You</div>' : ''}
            <h4>${alt.name}</h4>
            <div class="description">${alt.description}</div>
            <div class="timeline"><i class="bi bi-clock"></i> ${alt.timeline}</div>
            <div class="pros-cons">
                <div class="pros"><h5>Pros</h5><ul>${alt.pros.map(p => `<li>${p}</li>`).join('')}</ul></div>
                <div class="cons"><h5>Cons</h5><ul>${alt.cons.map(c => `<li>${c}</li>`).join('')}</ul></div>
            </div>
        </div>
    `).join('');

    // If no pathways match, show a message
    if (relevantPathways.length === 0) {
        container.innerHTML = '<div class="no-pathways">Based on your profile, Express Entry appears to be your best option. Consider improving your CRS score with the suggestions above.</div>';
    }
}

function renderCareerTransitions() {
    const section = document.getElementById('careerSection');
    const teer = answers.occupation_teer;

    if (teer < 4) { section.innerHTML = ''; return; }

    section.innerHTML = `
        <h3 class="section-title"><i class="bi bi-arrow-repeat"></i> Career Transition Recommendations</h3>
        <div class="warning-card info">
            <i class="bi bi-info-circle-fill warning-icon"></i>
            <div>
                <div class="warning-issue">Your current occupation (TEER ${teer}) is not eligible for Express Entry</div>
                <div class="warning-action">Consider transitioning to a TEER 0-3 occupation to become eligible. Here are some common paths:</div>
            </div>
        </div>
        <div class="improvement-card">
            <div>
                <div class="improvement-action">Transition to supervisory role</div>
                <div class="improvement-details">Many TEER 4 roles have TEER 2/3 supervisor equivalents</div>
            </div>
            <div class="improvement-gain">TEER 2-3</div>
        </div>
        <div class="improvement-card">
            <div>
                <div class="improvement-action">Get industry certifications</div>
                <div class="improvement-details">Professional certifications can qualify you for higher TEER roles</div>
            </div>
            <div class="improvement-gain">TEER 1-2</div>
        </div>
        <div class="improvement-card">
            <div>
                <div class="improvement-action">Study in Canada</div>
                <div class="improvement-details">Canadian diploma + PGWP in a skilled field</div>
            </div>
            <div class="improvement-gain">TEER 0-3</div>
        </div>
    `;
}

// Render Category-Based Express Entry Draws
function renderCategoryDraws() {
    const section = document.getElementById('categoryDrawsSection');
    const nocCode = answers.occupation;
    const crsScore = calculateCRS();
    const clb = getLowestCLB();

    if (!nocCode || typeof FEDERAL_CATEGORIES === 'undefined') {
        section.innerHTML = '';
        return;
    }

    const eligibleCategories = [];

    // Check each category for NOC eligibility
    for (const [catId, category] of Object.entries(FEDERAL_CATEGORIES)) {
        // French category is based on language, not NOC
        if (catId === 'french') {
            if (answers.french_level === 'nclc7_plus') {
                eligibleCategories.push({
                    id: catId,
                    ...category,
                    yourScore: crsScore,
                    eligible: true,
                    advantage: crsScore >= category.recentCutoff ? 'STRONG' : 'GOOD'
                });
            }
            continue;
        }

        // Check if user's NOC is in this category
        if (category.eligibleNOCs && category.eligibleNOCs.includes(nocCode)) {
            const advantage = crsScore >= category.recentCutoff ? 'STRONG' :
                             crsScore >= category.averageCutoff - 50 ? 'MODERATE' : 'DEVELOPING';
            eligibleCategories.push({
                id: catId,
                ...category,
                yourScore: crsScore,
                eligible: true,
                advantage
            });
        }
    }

    if (eligibleCategories.length === 0) {
        // Check if French could be an option
        if (answers.french_level !== 'nclc7_plus' && answers.french_level !== 'none') {
            section.innerHTML = `
                <h3 class="section-title"><i class="bi bi-lightning-charge"></i> Category-Based Draws</h3>
                <div class="info-card">
                    <p>Your occupation is not currently targeted by category-based draws. However, you could qualify for:</p>
                    <div class="improvement-card">
                        <div>
                            <div class="improvement-action">French Language Category</div>
                            <div class="improvement-details">Improve your French to NCLC 7+ to qualify for French draws with cutoffs as low as ${FEDERAL_CATEGORIES.french?.recentCutoff || 379}</div>
                        </div>
                        <div class="improvement-gain">CRS ${FEDERAL_CATEGORIES.french?.recentCutoff || 379}</div>
                    </div>
                </div>
            `;
        } else {
            section.innerHTML = '';
        }
        return;
    }

    // Sort by advantage (best matches first)
    eligibleCategories.sort((a, b) => {
        const order = { 'STRONG': 0, 'GOOD': 1, 'MODERATE': 2, 'DEVELOPING': 3 };
        return (order[a.advantage] || 3) - (order[b.advantage] || 3);
    });

    section.innerHTML = `
        <h3 class="section-title"><i class="bi bi-lightning-charge"></i> Category-Based Express Entry Draws</h3>
        <div class="category-info">
            <i class="bi bi-info-circle"></i>
            Category-based draws target specific occupations with <strong>lower CRS cutoffs</strong> than general draws.
            Your occupation qualifies for ${eligibleCategories.length} category draw${eligibleCategories.length !== 1 ? 's' : ''}!
        </div>
        <div class="category-draws-grid">
            ${eligibleCategories.map((cat, i) => `
                <div class="category-card ${cat.advantage.toLowerCase()} ${i === 0 ? 'best-match' : ''}">
                    ${i === 0 ? '<div class="best-badge">Best Opportunity</div>' : ''}
                    <div class="category-header">
                        <h4>${cat.name}</h4>
                        <span class="advantage-badge ${cat.advantage.toLowerCase()}">${cat.advantage}</span>
                    </div>
                    <div class="category-stats">
                        <div class="stat">
                            <div class="stat-value">${cat.recentCutoff}</div>
                            <div class="stat-label">Recent Cutoff</div>
                        </div>
                        <div class="stat">
                            <div class="stat-value">${crsScore}</div>
                            <div class="stat-label">Your CRS</div>
                        </div>
                        <div class="stat ${crsScore >= cat.recentCutoff ? 'positive' : 'negative'}">
                            <div class="stat-value">${crsScore >= cat.recentCutoff ? '+' : ''}${crsScore - cat.recentCutoff}</div>
                            <div class="stat-label">Difference</div>
                        </div>
                    </div>
                    <div class="category-details">
                        <div><i class="bi bi-calendar-event"></i> ${cat.frequency}</div>
                        <div><i class="bi bi-graph-up"></i> ${cat.trend}</div>
                    </div>
                    ${crsScore >= cat.recentCutoff
                        ? '<div class="category-verdict success"><i class="bi bi-check-circle-fill"></i> You would likely receive an ITA in a ${cat.name} draw!</div>'
                        : `<div class="category-verdict warning"><i class="bi bi-exclamation-circle"></i> ${cat.recentCutoff - crsScore} more points needed for recent cutoff</div>`
                    }
                </div>
            `).join('')}
        </div>
    `;
}

// Render NOC-Specific Pathway Recommendations
function renderNOCPathways() {
    const section = document.getElementById('nocPathwaysSection');
    const nocCode = answers.occupation;

    if (!nocCode || typeof NOC_PATHWAY_MATCHING === 'undefined') {
        section.innerHTML = '';
        return;
    }

    const nocPathway = NOC_PATHWAY_MATCHING[nocCode];

    if (!nocPathway) {
        // No specific pathway info for this NOC, but show general advice based on category
        const category = selectedOccupation?.category;
        if (category) {
            section.innerHTML = `
                <h3 class="section-title"><i class="bi bi-signpost-2"></i> Occupation-Based Recommendations</h3>
                <div class="noc-pathway-card">
                    <h4>${selectedOccupation?.title || 'Your Occupation'} (NOC ${nocCode})</h4>
                    <p>Your occupation falls under the <strong>${category}</strong> category.</p>
                    <div class="pathway-tips">
                        ${category === 'STEM' ? '<div class="tip"><i class="bi bi-laptop"></i> Consider BC PNP Tech, Ontario Tech Draws, or STEM category draws</div>' : ''}
                        ${category === 'Healthcare' ? '<div class="tip"><i class="bi bi-heart-pulse"></i> Healthcare category draws offer lower CRS cutoffs. Check Ontario\'s 2026 Priority Healthcare stream!</div>' : ''}
                        ${category === 'Trades' ? '<div class="tip"><i class="bi bi-tools"></i> Federal Skilled Trades program and Trade draws are great options. Red Seal certification helps!</div>' : ''}
                        ${category === 'Transport' ? '<div class="tip"><i class="bi bi-truck"></i> Transport category draws target your occupation. Provincial streams in Alberta and Saskatchewan also recruit heavily.</div>' : ''}
                        ${category === 'Agriculture' ? '<div class="tip"><i class="bi bi-tree"></i> Agriculture draws have the lowest CRS cutoffs. Also check Agri-Food Pilot program!</div>' : ''}
                    </div>
                </div>
            `;
        } else {
            section.innerHTML = '';
        }
        return;
    }

    const crsScore = calculateCRS();

    section.innerHTML = `
        <h3 class="section-title"><i class="bi bi-signpost-2"></i> Your Occupation's Best Pathways</h3>
        <div class="noc-pathway-card highlighted">
            <div class="noc-header">
                <h4>${nocPathway.title}</h4>
                <span class="noc-badge">NOC ${nocCode}</span>
            </div>

            <div class="recommendation-box">
                <i class="bi bi-lightbulb-fill"></i>
                <span>${nocPathway.recommendation}</span>
            </div>

            <div class="pathway-sections">
                <div class="pathway-section">
                    <h5><i class="bi bi-flag"></i> Federal Category Draws</h5>
                    <div class="category-tags">
                        ${nocPathway.federalCategories.map(cat => `
                            <span class="category-tag ${cat.toLowerCase()}">${cat}</span>
                        `).join('')}
                    </div>
                    ${nocPathway.recentDraws ? `
                        <div class="draw-comparison">
                            ${Object.entries(nocPathway.recentDraws).map(([type, cutoff]) => `
                                <div class="draw-item ${crsScore >= cutoff ? 'qualified' : ''}">
                                    <span class="draw-type">${type.charAt(0).toUpperCase() + type.slice(1)}</span>
                                    <span class="draw-cutoff">${cutoff}</span>
                                    <span class="your-status">${crsScore >= cutoff ? '<i class="bi bi-check-circle-fill"></i> Qualified' : `Need +${cutoff - crsScore}`}</span>
                                </div>
                            `).join('')}
                        </div>
                    ` : ''}
                </div>

                <div class="pathway-section">
                    <h5><i class="bi bi-geo-alt"></i> Provincial Priority Streams</h5>
                    <div class="provincial-streams">
                        ${nocPathway.provincialPriority.map(stream => {
                            const streamNames = {
                                'oinp_tech_draw': 'Ontario Tech Draw',
                                'oinp_priority_healthcare': 'Ontario Priority Healthcare',
                                'oinp_critical_sectors': 'Ontario Critical Sectors',
                                'bcpnp_tech': 'BC PNP Tech',
                                'bcpnp_healthcare': 'BC PNP Healthcare',
                                'aaip_tech': 'Alberta Tech Pathway',
                                'aaip_opportunity': 'Alberta Opportunity Stream',
                                'sinp_occupation_demand': 'Saskatchewan In-Demand',
                                'mpnp_skilled_manitoba': 'Manitoba Skilled Worker',
                                'aip_skilled': 'Atlantic Immigration Program'
                            };
                            return `<div class="stream-item"><i class="bi bi-arrow-right-circle"></i> ${streamNames[stream] || stream}</div>`;
                        }).join('')}
                    </div>
                </div>
            </div>
        </div>
    `;
}

// Render Family Sponsorship Options
function renderFamilySponsorship() {
    const section = document.getElementById('familySponsorshipSection');

    const hasCanadianSpouse = answers.canadian_spouse === 'yes_citizen' || answers.canadian_spouse === 'yes_pr';
    const hasCanadianParent = answers.family_in_canada === 'parent';
    const hasCanadianChild = answers.family_in_canada === 'child';
    const interestedInPGP = answers.pgp_interest === 'yes';

    if (!hasCanadianSpouse && !hasCanadianParent && !hasCanadianChild && !interestedInPGP) {
        section.innerHTML = '';
        return;
    }

    let familyOptions = [];

    if (hasCanadianSpouse) {
        const isOutsideCanada = answers.current_country === 'outside';
        const relationshipLength = answers.relationship_duration;

        familyOptions.push({
            type: 'Spousal Sponsorship',
            icon: 'heart-fill',
            highlight: true,
            description: `Your ${answers.canadian_spouse === 'yes_citizen' ? 'Canadian citizen' : 'PR'} spouse can sponsor you for permanent residence.`,
            streams: [
                {
                    name: isOutsideCanada ? 'Outland Sponsorship' : 'Inland Sponsorship',
                    processing: isOutsideCanada ? '12-15 months' : '12-18 months',
                    benefit: isOutsideCanada ? 'Can visit Canada while processing' : 'Can apply for open work permit while waiting'
                }
            ],
            requirements: [
                'Genuine relationship (marriage certificate or 12+ months cohabitation)',
                'Sponsor meets income requirements (usually met)',
                'No criminal inadmissibility',
                'Medical examination'
            ],
            tip: relationshipLength === 'under_1year'
                ? 'Relationships under 1 year may face extra scrutiny. Gather extensive proof of genuine relationship.'
                : 'Strong pathway! Spousal sponsorship has high approval rates for genuine relationships.'
        });
    }

    if (interestedInPGP && (hasCanadianChild || answers.has_canadian_child === 'yes')) {
        familyOptions.push({
            type: 'Parents & Grandparents Program (PGP)',
            icon: 'people-fill',
            highlight: false,
            description: 'Your Canadian citizen or PR child can sponsor you.',
            streams: [
                {
                    name: 'PGP Lottery',
                    processing: '24-36 months after selection',
                    benefit: 'Direct path to PR'
                },
                {
                    name: 'Super Visa (Alternative)',
                    processing: '2-4 weeks',
                    benefit: '10-year multiple entry, 5 years per visit'
                }
            ],
            requirements: [
                'Sponsor must meet Minimum Necessary Income (MNI) for 3 years',
                'Undertaking to support for 20 years',
                'Limited spots - lottery system'
            ],
            tip: 'PGP opens once per year with limited invitations. Super Visa is a good alternative while waiting.'
        });
    }

    if (familyOptions.length === 0) {
        section.innerHTML = '';
        return;
    }

    section.innerHTML = `
        <h3 class="section-title"><i class="bi bi-house-heart"></i> Family Sponsorship Options</h3>
        <div class="family-options-grid">
            ${familyOptions.map(opt => `
                <div class="family-option-card ${opt.highlight ? 'highlighted' : ''}">
                    <div class="option-header">
                        <i class="bi bi-${opt.icon}"></i>
                        <h4>${opt.type}</h4>
                    </div>
                    <p class="option-desc">${opt.description}</p>

                    <div class="streams-list">
                        ${opt.streams.map(s => `
                            <div class="stream-option">
                                <strong>${s.name}</strong>
                                <div class="stream-details">
                                    <span><i class="bi bi-clock"></i> ${s.processing}</span>
                                    <span><i class="bi bi-check"></i> ${s.benefit}</span>
                                </div>
                            </div>
                        `).join('')}
                    </div>

                    <div class="requirements-list">
                        <strong>Key Requirements:</strong>
                        <ul>
                            ${opt.requirements.map(r => `<li>${r}</li>`).join('')}
                        </ul>
                    </div>

                    <div class="family-tip">
                        <i class="bi bi-lightbulb"></i> ${opt.tip}
                    </div>
                </div>
            `).join('')}
        </div>
    `;
}

// Render Cost Calculator - Government Fees Breakdown
function renderCostCalculator() {
    const section = document.getElementById('costCalculatorSection');
    const clb = getLowestCLB();
    const canExp = answers.canadian_experience !== 'none' ? parseInt(answers.canadian_experience) || 0 : 0;
    const hasSpouse = answers.spouse_coming === 'yes';
    const dependents = parseInt(answers.dependents_count) || 0;

    // Government fees (2025 rates)
    const fees = {
        application: 850,
        rightOfPR: 515,
        biometrics: 85,
        spouseApplication: hasSpouse ? 850 : 0,
        spouseRightOfPR: hasSpouse ? 515 : 0,
        dependentApplication: dependents * 230,
        dependentRightOfPR: dependents * 515,
        medical: hasSpouse ? 450 : 250,
        policeCheck: 50,
        eca: answers.education_country === 'foreign' && answers.eca_status !== 'yes' ? 250 : 0,
        languageTest: answers.english_test === 'none' ? 350 : 0
    };

    const governmentTotal = fees.application + fees.rightOfPR + fees.biometrics +
                           fees.spouseApplication + fees.spouseRightOfPR +
                           fees.dependentApplication + fees.dependentRightOfPR;
    const otherCosts = fees.medical + fees.policeCheck + fees.eca + fees.languageTest;
    const totalCost = governmentTotal + otherCosts;

    section.innerHTML = `
        <h3 class="section-title"><i class="bi bi-calculator"></i> Estimated Costs (CAD)</h3>
        <div class="cost-calculator">
            <div class="cost-breakdown">
                <div class="cost-item">
                    <span class="cost-label"><i class="bi bi-file-earmark-text"></i> Principal Application Fee</span>
                    <span class="cost-amount">$${fees.application}</span>
                </div>
                <div class="cost-item">
                    <span class="cost-label"><i class="bi bi-shield-check"></i> Right of PR Fee</span>
                    <span class="cost-amount">$${fees.rightOfPR}</span>
                </div>
                <div class="cost-item">
                    <span class="cost-label"><i class="bi bi-fingerprint"></i> Biometrics</span>
                    <span class="cost-amount">$${fees.biometrics}</span>
                </div>
                ${hasSpouse ? `
                <div class="cost-item">
                    <span class="cost-label"><i class="bi bi-people"></i> Spouse Application + PR Fee</span>
                    <span class="cost-amount">$${fees.spouseApplication + fees.spouseRightOfPR}</span>
                </div>
                ` : ''}
                ${dependents > 0 ? `
                <div class="cost-item">
                    <span class="cost-label"><i class="bi bi-person-hearts"></i> Dependent Children (${dependents})</span>
                    <span class="cost-amount">$${fees.dependentApplication + fees.dependentRightOfPR}</span>
                </div>
                ` : ''}
                <div class="cost-item subtotal">
                    <span class="cost-label"><strong>Government Fees Subtotal</strong></span>
                    <span class="cost-amount">$${governmentTotal.toLocaleString()}</span>
                </div>
                <div class="cost-item">
                    <span class="cost-label"><i class="bi bi-hospital"></i> Medical Exam (estimated)</span>
                    <span class="cost-amount">$${fees.medical}</span>
                </div>
                <div class="cost-item">
                    <span class="cost-label"><i class="bi bi-file-earmark-lock"></i> Police Clearance</span>
                    <span class="cost-amount">$${fees.policeCheck}</span>
                </div>
                ${fees.eca > 0 ? `
                <div class="cost-item">
                    <span class="cost-label"><i class="bi bi-mortarboard"></i> ECA (WES)</span>
                    <span class="cost-amount">$${fees.eca}</span>
                </div>
                ` : ''}
                ${fees.languageTest > 0 ? `
                <div class="cost-item">
                    <span class="cost-label"><i class="bi bi-chat-dots"></i> Language Test</span>
                    <span class="cost-amount">$${fees.languageTest}</span>
                </div>
                ` : ''}
                <div class="cost-item total">
                    <span class="cost-label"><strong>Total Estimated Cost</strong></span>
                    <span class="cost-amount">$${totalCost.toLocaleString()}</span>
                </div>
            </div>
            <div class="cost-note">
                <i class="bi bi-info-circle"></i> These are government fees only. Additional costs may include: translation services (~$50/document), photos (~$20), courier/shipping (~$50). RCIC consultation fees range from $2,000-$5,000.
            </div>
        </div>
    `;
}

// Render Document Checklist - Required Documents per Program
function renderDocumentChecklist() {
    const section = document.getElementById('documentChecklistSection');
    const docsReady = answers.documents_ready || [];

    const documents = {
        identity: [
            { name: 'Valid Passport', required: true, ready: docsReady.includes('passport') },
            { name: 'Birth Certificate', required: true, ready: false },
            { name: 'National ID Card', required: false, ready: false },
            { name: 'Travel History (last 10 years)', required: true, ready: false }
        ],
        education: [
            { name: 'Degree/Diploma Certificates', required: true, ready: false },
            { name: 'Transcripts', required: true, ready: false },
            { name: 'ECA Report', required: answers.education_country === 'foreign', ready: docsReady.includes('eca') },
            { name: 'Professional License (if applicable)', required: false, ready: false }
        ],
        language: [
            { name: 'IELTS/CELPIP/PTE Results', required: true, ready: docsReady.includes('language_test') },
            { name: 'French Test Results (TEF/TCF)', required: answers.french_level === 'nclc7_plus', ready: false }
        ],
        employment: [
            { name: 'Reference Letters', required: true, ready: docsReady.includes('reference_letters') },
            { name: 'Employment Contracts', required: false, ready: false },
            { name: 'Pay Stubs (last 3 months)', required: false, ready: false },
            { name: 'Job Offer Letter', required: answers.job_offer === 'yes', ready: false },
            { name: 'LMIA Document', required: answers.job_lmia === 'lmia_approved', ready: false }
        ],
        financial: [
            { name: 'Bank Statements (6 months)', required: true, ready: answers.bank_statements_ready === 'yes_ready' },
            { name: 'Investment Statements', required: false, ready: false },
            { name: 'Property Documents', required: false, ready: false }
        ],
        admissibility: [
            { name: 'Police Clearance Certificate', required: true, ready: docsReady.includes('police_clearance') },
            { name: 'Medical Exam Results', required: true, ready: docsReady.includes('medical') },
            { name: 'Rehabilitation Certificate', required: answers.criminal_history !== 'no', ready: false }
        ]
    };

    const renderCategory = (title, icon, items) => {
        const requiredItems = items.filter(i => i.required);
        const readyCount = requiredItems.filter(i => i.ready).length;

        return `
            <div class="checklist-category">
                <h4><i class="bi bi-${icon}"></i> ${title} <span style="font-size: 0.8rem; color: var(--text-muted);">(${readyCount}/${requiredItems.length})</span></h4>
                <div class="checklist-items">
                    ${items.filter(i => i.required).map(item => `
                        <div class="checklist-item ${item.ready ? 'ready' : 'needed'} ${!item.ready && item.required ? 'urgent' : ''}">
                            <i class="bi bi-${item.ready ? 'check-circle-fill' : 'circle'}"></i>
                            <span>${item.name}</span>
                        </div>
                    `).join('')}
                </div>
            </div>
        `;
    };

    section.innerHTML = `
        <h3 class="section-title"><i class="bi bi-list-check"></i> Document Checklist</h3>
        <div class="document-checklist">
            <div class="checklist-grid">
                ${renderCategory('Identity', 'person-badge', documents.identity)}
                ${renderCategory('Education', 'mortarboard', documents.education)}
                ${renderCategory('Language', 'chat-quote', documents.language)}
                ${renderCategory('Employment', 'briefcase', documents.employment)}
                ${renderCategory('Financial', 'bank', documents.financial)}
                ${renderCategory('Admissibility', 'shield-check', documents.admissibility)}
            </div>
            <div class="cost-note" style="margin-top: 1rem;">
                <i class="bi bi-lightbulb"></i> <strong>Tip:</strong> Start gathering documents NOW. Police clearances can take 2-3 months from some countries. Get translations done by certified translators.
            </div>
        </div>
    `;
}

// Render All Pathways - Comprehensive Overview (Researcher Perspective)
function renderAllPathways() {
    const section = document.getElementById('allPathwaysSection');
    const clb = getLowestCLB();
    const canExp = answers.canadian_experience !== 'none' ? parseInt(answers.canadian_experience) || 0 : 0;
    const forExp = answers.foreign_experience !== 'none' ? parseInt(answers.foreign_experience) || 0 : 0;
    const selectedNOC = selectedOccupation || {};

    // All permanent residence pathways
    const permanentPathways = {
        express_entry: {
            name: 'Express Entry',
            icon: 'lightning',
            programs: [
                { name: 'Federal Skilled Worker (FSW)', eligible: clb >= 7 && forExp >= 1, desc: 'CLB 7+, 1yr foreign exp' },
                { name: 'Canadian Experience Class (CEC)', eligible: clb >= 5 && canExp >= 1, desc: 'CLB 5+, 1yr Canadian exp' },
                { name: 'Federal Skilled Trades (FST)', eligible: clb >= 5 && answers.trade_cert !== 'no', desc: 'CLB 5+, trade certificate' },
            ]
        },
        pnp: {
            name: 'Provincial Nominee Programs',
            icon: 'geo-alt',
            programs: [
                { name: 'Ontario PNP (OINP)', eligible: true, desc: 'Human Capital, Employer Job Offer streams' },
                { name: 'BC PNP', eligible: true, desc: 'Skills Immigration, Express Entry BC' },
                { name: 'Alberta AAIP', eligible: true, desc: 'Alberta Opportunity, Express Entry streams' },
                { name: 'Saskatchewan SINP', eligible: true, desc: 'Occupation In-Demand, Express Entry' },
                { name: 'Manitoba MPNP', eligible: true, desc: 'Skilled Workers, International Education' },
                { name: 'Nova Scotia NSNP', eligible: true, desc: 'Labour Market Priorities, Skilled Worker' },
                { name: 'New Brunswick PNP', eligible: true, desc: 'Skilled Workers, Express Entry' },
                { name: 'PEI PNP', eligible: true, desc: 'Labour Impact, Business Impact' },
                { name: 'NL PNP', eligible: true, desc: 'Skilled Worker, Express Entry' },
            ]
        },
        pilot: {
            name: 'Pilot Programs',
            icon: 'stars',
            programs: [
                { name: 'Atlantic Immigration Program (AIP)', eligible: true, desc: 'Atlantic Canada employer-driven' },
                { name: 'Rural & Northern Immigration Pilot', eligible: true, desc: 'Community-driven PR' },
                { name: 'Agri-Food Pilot', eligible: answers.field_of_study === 'agriculture', desc: 'Agriculture sector workers' },
            ]
        },
        family: {
            name: 'Family Sponsorship',
            icon: 'people',
            programs: [
                { name: 'Spousal Sponsorship', eligible: answers.canadian_spouse === 'yes_citizen' || answers.canadian_spouse === 'yes_pr', desc: 'Spouse in Canada can sponsor' },
                { name: 'Common-Law Partner', eligible: answers.canadian_spouse === 'yes_citizen' || answers.canadian_spouse === 'yes_pr', desc: '12+ months cohabitation' },
                { name: 'Parent/Grandparent (PGP)', eligible: false, desc: 'Canadians sponsor parents' },
            ]
        },
        business: {
            name: 'Business Immigration',
            icon: 'briefcase',
            programs: [
                { name: 'Start-Up Visa', eligible: true, desc: 'Entrepreneurs with innovative business' },
                { name: 'Self-Employed Persons', eligible: answers.employment_status === 'self_employed', desc: 'Culture/athletics/farming' },
                { name: 'Quebec Investor', eligible: answers.funds_amount === 'over_60k', desc: 'Business experience + net worth' },
            ]
        },
        quebec: {
            name: 'Quebec Programs',
            icon: 'building',
            programs: [
                { name: 'Quebec Skilled Worker (QSW)', eligible: true, desc: 'Arrima selection system' },
                { name: 'Quebec Experience Program (PEQ)', eligible: canExp >= 1, desc: 'Work/study experience in QC' },
            ]
        }
    };

    // All temporary pathways
    const temporaryPathways = {
        work: {
            name: 'Work Permits',
            icon: 'briefcase',
            programs: [
                { name: 'LMIA Work Permit', eligible: true, desc: 'Employer-sponsored, most common' },
                { name: 'Intra-Company Transfer', eligible: true, desc: 'Transfer within multinational company' },
                { name: 'CUSMA Professionals', eligible: true, desc: 'US/Mexico citizens, specific occupations' },
                { name: 'International Experience Canada (IEC)', eligible: answers.age && answers.age.includes('18-') || answers.age === '25-29' || answers.age === '30-34', desc: 'Youth mobility, age 18-35' },
                { name: 'Post-Graduation Work Permit', eligible: answers.education_country === 'canada', desc: 'Canadian graduate, 1-3 years' },
                { name: 'Bridging Open Work Permit', eligible: canExp >= 1, desc: 'Between permits, PR pending' },
                { name: 'Spousal Open Work Permit', eligible: answers.canadian_spouse === 'yes_citizen' || answers.canadian_spouse === 'yes_pr', desc: 'Spouse of Canadian/PR' },
            ]
        },
        study: {
            name: 'Study Permits',
            icon: 'mortarboard',
            programs: [
                { name: 'Study Permit (DLI)', eligible: true, desc: 'Study at designated institution' },
                { name: 'Study + Work (Co-op)', eligible: true, desc: 'Program includes work term' },
                { name: 'Student Direct Stream (SDS)', eligible: true, desc: 'Faster processing, select countries' },
            ]
        },
        visitor: {
            name: 'Visitor Status',
            icon: 'airplane',
            programs: [
                { name: 'Visitor Visa (TRV)', eligible: true, desc: 'Tourism, family visit, business' },
                { name: 'Super Visa', eligible: answers.family_in_canada !== 'none', desc: 'Parents/grandparents, 5yr stay' },
                { name: 'eTA', eligible: true, desc: 'Visa-exempt countries, air travel' },
            ]
        }
    };

    const renderPathwayCategory = (category, data, type) => {
        const eligibleCount = data.programs.filter(p => p.eligible).length;
        return `
            <div class="pathway-type-card">
                <h4>
                    <i class="bi bi-${data.icon}"></i> ${data.name}
                    <span class="badge ${type}">${type === 'pr' ? 'PR' : 'Temp'}</span>
                    <span style="font-size: 0.75rem; color: var(--text-muted); margin-left: auto;">${eligibleCount}/${data.programs.length} potential</span>
                </h4>
                <div class="pathway-list">
                    ${data.programs.map(p => `
                        <div class="pathway-item ${p.eligible ? 'eligible' : 'not-eligible'}">
                            <span>${p.name}</span>
                            <span style="font-size: 0.75rem; color: var(--text-muted);">${p.desc}</span>
                        </div>
                    `).join('')}
                </div>
            </div>
        `;
    };

    section.innerHTML = `
        <h3 class="section-title"><i class="bi bi-map"></i> All Immigration Pathways to Canada</h3>
        <p style="color: var(--text-muted); margin-bottom: 1.5rem;">Comprehensive overview of 40+ immigration programs. Eligible pathways highlighted based on your profile.</p>

        <h4 style="color: var(--primary); margin-bottom: 1rem;"><i class="bi bi-house-door"></i> Permanent Residence Programs</h4>
        <div class="pathways-grid" style="margin-bottom: 2rem;">
            ${Object.entries(permanentPathways).map(([key, data]) => renderPathwayCategory(key, data, 'pr')).join('')}
        </div>

        <h4 style="color: var(--primary); margin-bottom: 1rem;"><i class="bi bi-clock-history"></i> Temporary Programs</h4>
        <div class="pathways-grid">
            ${Object.entries(temporaryPathways).map(([key, data]) => renderPathwayCategory(key, data, 'temp')).join('')}
        </div>

        <div class="cost-note" style="margin-top: 1.5rem;">
            <i class="bi bi-lightbulb"></i> <strong>Strategic Tip:</strong> Many people combine temporary and permanent pathways. Common strategy: Study Permit → PGWP → CEC PR. Or: LMIA Work Permit → Canadian Experience → Express Entry. Choose based on your timeline and financial situation.
        </div>
    `;
}

// Render Timeline Estimator - Processing Time Breakdown
function renderTimeline() {
    const section = document.getElementById('timelineSection');
    const hasECA = answers.eca_status === 'yes';
    const hasLanguageTest = answers.english_test && answers.english_test !== 'none';
    const canExp = answers.canadian_experience !== 'none' ? parseInt(answers.canadian_experience) || 0 : 0;

    // Determine primary pathway
    let primaryPathway = 'FSW';
    if (canExp >= 1) primaryPathway = 'CEC';
    if (answers.trade_cert !== 'no') primaryPathway = 'FST';

    const steps = [];

    // Pre-Express Entry steps
    if (!hasLanguageTest) {
        steps.push({
            name: 'Take Language Test',
            duration: '2-3 months',
            description: 'Book test, prepare, get results',
            status: 'future'
        });
    }

    if (!hasECA && answers.education_country === 'foreign') {
        steps.push({
            name: 'Get ECA Report',
            duration: '4-8 weeks',
            description: 'Apply to WES/IQAS, wait for assessment',
            status: hasECA ? 'completed' : 'future'
        });
    }

    // Express Entry steps
    steps.push({
        name: 'Create Express Entry Profile',
        duration: '1-2 weeks',
        description: 'Submit profile, enter pool',
        status: 'future'
    });

    steps.push({
        name: 'Wait for ITA',
        duration: '2-12 months',
        description: 'Based on CRS score and draw frequency',
        status: 'future'
    });

    steps.push({
        name: 'Submit PR Application',
        duration: '60 days',
        description: 'Submit all documents after receiving ITA',
        status: 'future'
    });

    steps.push({
        name: 'Application Processing',
        duration: '5-8 months',
        description: primaryPathway === 'CEC' ? 'CEC typically 5-6 months' : 'FSW typically 6-8 months',
        status: 'future'
    });

    steps.push({
        name: 'COPR & Landing',
        duration: '1-2 months',
        description: 'Receive COPR, complete landing',
        status: 'future'
    });

    // Calculate total time range
    const minMonths = 8;
    const maxMonths = 24;

    section.innerHTML = `
        <h3 class="section-title"><i class="bi bi-calendar-event"></i> Estimated Timeline</h3>
        <div class="timeline-estimator">
            <div class="timeline-visual">
                <div class="timeline-line"></div>
                ${steps.map((step, i) => `
                    <div class="timeline-step">
                        <div class="timeline-dot ${step.status}"></div>
                        <div class="timeline-content">
                            <h5>${step.name}</h5>
                            <p>${step.description}</p>
                        </div>
                        <span class="timeline-duration">${step.duration}</span>
                    </div>
                `).join('')}
            </div>
            <div class="total-timeline">
                <div class="time">${minMonths} - ${maxMonths} months</div>
                <div class="label">Estimated total time to PR</div>
            </div>
            <div class="cost-note" style="margin-top: 1rem;">
                <i class="bi bi-info-circle"></i> Timeline varies based on your CRS score, draw frequency, and document readiness. Provincial nomination can add 2-4 months but provides +600 CRS points.
            </div>
        </div>
    `;
}

function restartChecker() {
    currentQuestion = 0;
    answers = {};
    selectedOccupation = null;
    document.getElementById('questionContainer').style.display = 'block';
    document.querySelector('.progress-container').style.display = 'block';
    document.getElementById('resultsSection').classList.remove('show');
    renderQuestion();
}
