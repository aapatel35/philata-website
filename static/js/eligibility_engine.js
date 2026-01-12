// Eligibility Engine - Question Rendering & Recommendation Logic

let currentQuestion = 0;
let answers = {};
let selectedOccupation = null;
let formError = null;

// Initialize on page load
document.addEventListener('DOMContentLoaded', () => renderQuestion());

function renderQuestion() {
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
        // Check if this question requires an answer
        if (q.type === 'search') {
            if (!answers['occupation']) {
                showInlineError('Please select your occupation from the list');
                return;
            }
        } else if (!q.multiSelect && !answers[q.id]) {
            showInlineError('Please select an option to continue');
            return;
        } else if (q.multiSelect && (!answers[q.id] || answers[q.id].length === 0)) {
            // Multi-select is optional, allow continuing without selection
        }
    }

    hideInlineError();
    currentQuestion++;
    renderQuestion();
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
    renderProgramEligibility(crsScore);
    renderProvincialPathways();
    renderImprovements(crsScore);
    renderAlternativePathways();
    renderCareerTransitions();
}

function renderProfileSummary() {
    const grid = document.getElementById('profileGrid');
    const clb = getLowestCLB();

    // Format language display based on test type
    let langDisplay = 'No test';
    if (clb > 0) {
        const testName = answers.english_test === 'ielts' ? 'IELTS' : answers.english_test === 'celpip' ? 'CELPIP' : answers.english_test === 'pte' ? 'PTE' : '';
        langDisplay = `${testName} (CLB ${clb})`;
    }

    const items = [
        { label: 'Age', value: answers.age || 'N/A' },
        { label: 'Education', value: answers.education_level?.replace('_', ' ') || 'N/A' },
        { label: 'Field', value: answers.field_of_study || 'N/A' },
        { label: 'Canadian Exp', value: answers.canadian_experience || 'None' },
        { label: 'English', value: langDisplay },
        { label: 'Target Province', value: answers.target_province || 'Any' }
    ];
    grid.innerHTML = items.map(i => `
        <div class="profile-item"><div class="label">${i.label}</div><div class="value">${i.value}</div></div>
    `).join('');
}

function renderWarnings() {
    const section = document.getElementById('warningsSection');
    const warnings = [];
    const clb = getLowestCLB();

    if (answers.english_test === 'none' || clb === 0) {
        warnings.push({ type: 'urgent', issue: 'No language test completed', action: 'Language test is REQUIRED for Express Entry. Book IELTS, CELPIP, or PTE Core immediately.' });
    }
    if (answers.eca_status === 'no' && answers.education_country === 'foreign') {
        warnings.push({ type: 'urgent', issue: 'No ECA completed', action: 'Educational Credential Assessment is REQUIRED. Apply to WES, IQAS, or other designated organization.' });
    }
    if (answers.criminal_history !== 'no') {
        warnings.push({ type: 'concern', issue: 'Criminal history may affect admissibility', action: 'Consult an immigration lawyer. You may need a Rehabilitation application or Criminal Record Suspension.' });
    }
    if (answers.previous_refusal !== 'no') {
        warnings.push({ type: 'concern', issue: 'Previous visa refusal on record', action: 'Address refusal reasons in your new application. Consider hiring a licensed RCIC.' });
    }
    if (answers.occupation_teer >= 4) {
        warnings.push({ type: 'info', issue: 'Your occupation (TEER 4/5) is NOT eligible for Express Entry', action: 'See Career Transition recommendations below, or consider Study → Work permit pathway.' });
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

    const pathways = [];

    // Newfoundland & Labrador - Has its own 67-point scoring system
    if (province === 'newfoundland' || province === 'any') {
        const nlScore = calculateNLPNPScore();
        pathways.push({
            province: 'Newfoundland & Labrador',
            stream: 'NLPNP Express Entry Skilled Worker',
            match: nlScore >= 67 ? `Your NLPNP score: ${nlScore}/100 (67+ required)` : `Your NLPNP score: ${nlScore}/100 (Need 67)`,
            benefit: '+600 CRS, job offer required',
            eligible: nlScore >= 67,
            requirements: ['67+ points on NL grid', 'Job offer from NL employer', 'CLB 4+ (higher for some NOCs)']
        });
    }

    // Check category matches with province-specific criteria
    if (category === 'STEM') {
        pathways.push({
            province: 'British Columbia',
            stream: 'BC PNP Tech',
            match: hasStudiedInProvince ? 'Studied in BC + Tech occupation = Strong match' : 'Your occupation is on the BC Tech list',
            benefit: '+600 CRS, weekly draws, fast processing',
            eligible: true,
            requirements: ['Tech occupation on BC list', 'Job offer OR valid work permit', 'CLB 4+']
        });
        pathways.push({
            province: 'Ontario',
            stream: 'OINP Tech Draw',
            match: hasStudiedInProvince ? 'Studied in ON + Tech = Priority' : 'Eligible for Ontario Tech draws',
            benefit: '+600 CRS, lower cutoffs than general',
            eligible: true,
            requirements: ['Active Express Entry profile', 'Tech occupation', 'CLB 7+']
        });
    }

    if (category === 'Healthcare') {
        pathways.push({
            province: 'Ontario',
            stream: 'OINP Health Human Capital',
            match: hasStudiedInProvince ? 'Studied in ON + Healthcare = Strong match' : 'Healthcare occupation eligible',
            benefit: '+600 CRS, priority processing',
            eligible: true,
            requirements: ['Healthcare NOC code', 'Active Express Entry profile', 'CLB 7+']
        });
        pathways.push({
            province: 'Nova Scotia',
            stream: 'NSNP Labour Market Priorities',
            match: 'Healthcare in high demand in NS',
            benefit: 'No job offer required for some streams',
            eligible: true,
            requirements: ['In-demand occupation', 'CLB 5+', 'Settlement funds']
        });
    }

    if (category === 'Trades') {
        pathways.push({
            province: 'Alberta',
            stream: 'AAIP Alberta Opportunity',
            match: hasWorkedInProvince ? 'AB work experience + Trade = Excellent' : 'Trades in demand in Alberta',
            benefit: 'No Express Entry needed, direct PR pathway',
            eligible: true,
            requirements: ['Alberta work experience', 'Valid work permit', 'CLB 4+']
        });
        pathways.push({
            province: 'Saskatchewan',
            stream: 'SINP Occupation In-Demand',
            match: 'Trades on in-demand list',
            benefit: 'Points-based system, no job offer needed',
            eligible: true,
            requirements: ['60+ points on SINP grid', 'In-demand occupation', 'CLB 4+']
        });
    }

    // Province-specific advantages based on study/work history
    if (hasStudiedInProvince) {
        if (province === 'bc' || province === 'any') {
            pathways.push({
                province: 'British Columbia',
                stream: 'BC PNP International Graduate',
                match: 'Studied in BC = Bonus points on SIRS',
                benefit: 'BC grads get higher ranking',
                eligible: true,
                requirements: ['BC post-secondary degree', 'Job offer in BC', 'CLB 4+']
            });
        }
        if (province === 'ontario' || province === 'any') {
            pathways.push({
                province: 'Ontario',
                stream: 'OINP Masters/PhD Graduate',
                match: 'Ontario degree = No job offer needed',
                benefit: 'Direct nomination without job offer',
                eligible: answers.education_level === 'masters' || answers.education_level === 'phd',
                requirements: ['Ontario Masters/PhD', 'CLB 7+', 'Lived in ON 1+ year']
            });
        }
    }

    // Add general PNP option
    pathways.push({
        province: 'Multiple Provinces',
        stream: 'Express Entry Linked PNP',
        match: 'Create EE profile, receive provincial nominations',
        benefit: '+600 CRS points instantly',
        eligible: true,
        requirements: ['Active Express Entry profile', 'Meet provincial criteria']
    });

    // Sort by eligibility and relevance
    pathways.sort((a, b) => {
        if (a.eligible && !b.eligible) return -1;
        if (!a.eligible && b.eligible) return 1;
        return 0;
    });

    container.innerHTML = pathways.slice(0, 5).map((p, i) => `
        <div class="pathway-card ${i === 0 && p.eligible ? 'recommended' : ''} ${!p.eligible ? 'not-eligible' : ''}">
            ${i === 0 && p.eligible ? '<div class="pathway-badge">Best Match</div>' : ''}
            <h4>${p.province} - ${p.stream}</h4>
            <div class="pathway-match"><i class="bi bi-${p.eligible ? 'check-circle-fill' : 'exclamation-circle'}"></i> ${p.match}</div>
            <div class="pathway-benefit"><strong>Benefit:</strong> ${p.benefit}</div>
            ${p.requirements ? `<div class="pathway-requirements"><strong>Requirements:</strong> ${p.requirements.join(' • ')}</div>` : ''}
            <a href="/tools/pnp-calculator" class="pathway-cta">Calculate PNP Score <i class="bi bi-arrow-right"></i></a>
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

function restartChecker() {
    currentQuestion = 0;
    answers = {};
    selectedOccupation = null;
    document.getElementById('questionContainer').style.display = 'block';
    document.querySelector('.progress-container').style.display = 'block';
    document.getElementById('resultsSection').classList.remove('show');
    renderQuestion();
}
