const API_BASE_URL = window.__API_BASE_URL__ || 'http://localhost:8000';

const elements = {
    chatLog: document.getElementById('chat-log'),
    consentScreen: document.getElementById('consent-screen'),
    consentYes: document.getElementById('consent-yes'),
    consentNo: document.getElementById('consent-no'),
    suggestionsBar: document.getElementById('suggestions-bar'),
    chatForm: document.getElementById('chat-form'),
    chatInput: document.getElementById('chat-input'),
    sendButton: document.getElementById('send-button'),
    languageSelect: document.getElementById('language-select'),
    consentTitle: document.getElementById('consent-title'),
    consentDescription: document.getElementById('consent-description'),
    consentNoButton: document.getElementById('consent-no'),
    consentYesButton: document.getElementById('consent-yes'),
};

const LOCALIZED_TEXT = {
    english: {
        consentTitle: 'Help Improve Rural Services',
        consentDescription: 'Would you be willing to participate in a brief, anonymous survey about local governance and services? Your feedback is valuable.',
        consentYes: "Yes, I'll help",
        consentNo: 'No, take me to the FAQ',
        introMessage: 'Welcome to the National Rural Services Assistant.',
        thankYou: 'Thank you for your valuable feedback. You can now ask me questions about government services.',
        summaryIntro: 'Here is a summary of what we recorded:',
        faqWelcome: 'Welcome! How can I help you today? Ask me about government schemes, health facilities, or local representatives.',
        textPlaceholder: 'Type your answer...',
        questionPlaceholder: 'Ask a question...'
    },
    hindi: {
        consentTitle: 'ग्रामीण सेवाओं में सुधार में मदद करें',
        consentDescription: 'क्या आप स्थानीय शासन और सेवाओं पर एक संक्षिप्त, गुमनाम सर्वेक्षण में भाग लेने के लिए तैयार हैं? आपकी प्रतिक्रिया महत्वपूर्ण है।',
        consentYes: 'हाँ, मैं मदद करूंगा',
        consentNo: 'नहीं, मुझे FAQ पर ले जाएँ',
        introMessage: 'राष्ट्रीय ग्रामीण सेवा सहायक में आपका स्वागत है।',
        thankYou: 'आपकी मूल्यवान प्रतिक्रिया के लिए धन्यवाद। अब आप सरकारी सेवाओं के बारे में प्रश्न पूछ सकते हैं।',
        summaryIntro: 'यहाँ हमने क्या दर्ज किया है:',
        faqWelcome: 'नमस्ते! मैं आपकी कैसे मदद कर सकता हूँ? सरकारी योजनाओं, स्वास्थ्य सुविधाओं या जन प्रतिनिधियों के बारे में पूछें।',
        textPlaceholder: 'अपना उत्तर लिखें...',
        questionPlaceholder: 'अपना प्रश्न पूछें...'
    },
    telugu: {
        consentTitle: 'గ్రామీణ సేవలను మెరుగుపరచడానికి సహాయపడండి',
        consentDescription: 'స్థానిక పాలన మరియు సేవలపై చిన్న, గోప్య సర్వేలో పాల్గొనడానికి మీరు సిద్ధంగా ఉన్నారా? మీ అభిప్రాయం ఎంతో విలువైనది.',
        consentYes: 'అవును, నేను సహాయపడతాను',
        consentNo: 'వద్దు, నన్ను FAQ కు తీసుకెళ్లండి',
        introMessage: 'జాతీయ గ్రామీణ సేవా సహాయకుడికి స్వాగతం.',
        thankYou: 'మీ విలువైన అభిప్రాయం కోసం ధన్యవాదాలు. ఇప్పుడు మీరు ప్రభుత్వ సేవల గురించి ప్రశ్నలు అడగవచ్చు.',
        summaryIntro: 'మేము నమోదు చేసిన వివరాలు ఇవి:',
        faqWelcome: 'నమస్కారం! నేను మీకు ఎలా సహాయపడగలను? ప్రభుత్వ పథకాలు, ఆరోగ్య సదుపాయాలు లేదా ప్రజా ప్రతినిధుల గురించి అడగండి.',
        textPlaceholder: 'మీ సమాధానం టైప్ చేయండి...',
        questionPlaceholder: 'మీ ప్రశ్నను అడగండి...'
    }
};

const LOCALIZED_FAQ_SUGGESTIONS = {
    english: ['What is PMAY scheme?', 'Find hospitals near me', 'Who is my MLA?'],
    hindi: ['PMAY योजना क्या है?', 'मेरे पास अस्पताल खोजें', 'मेरा MLA कौन है?'],
    telugu: ['PMAY పథకం ఏమిటి?', 'నా దగ్గర ఆసుపత్రులు కనుగొనండి', 'నా MLA ఎవరు?']
};

const SURVEY_QUESTIONS = [
    {
        id: 'pincode',
        text: 'To begin, please provide your 6-digit pincode.',
        type: 'text',
        pattern: '^\\d{6}$',
        samples: ['560001', '400001', '110001']
    },
    {
        id: 'mla_opinion',
        text: 'How satisfied are you with the work of your local MLA? Please describe your opinion.',
        type: 'textarea',
        samples: [
            'Road repairs have improved but we still need better street lights.',
            'MLA has been responsive to health camp requests in our village.',
            'We need more focus on irrigation support for farmers.'
        ]
    },
    {
        id: 'mp_opinion',
        text: 'How satisfied are you with the work of your MP? Please describe your opinion.',
        type: 'textarea',
        samples: [
            'MP has helped set up a new Jan Aushadhi Kendra recently.',
            'We would like more visits from the MP office to our block.',
            'Employment programs need stronger implementation from the MP.'
        ]
    },
    {
        id: 'satisfaction_score',
        text: 'Overall, how would you rate the local governance on a scale of 1 (Poor) to 5 (Excellent)?',
        type: 'buttons',
        options: ['1', '2', '3', '4', '5']
    },
];

const LOCALIZED_SURVEYS = {
    english: {
        samples: {
            pincode: ['560001', '400001', '110001'],
            mla_opinion: [
                'Road repairs have improved but we still need better street lights.',
                'MLA has been responsive to health camp requests in our village.',
                'We need more focus on irrigation support for farmers.'
            ],
            mp_opinion: [
                'MP has helped set up a new Jan Aushadhi Kendra recently.',
                'We would like more visits from the MP office to our block.',
                'Employment programs need stronger implementation from the MP.'
            ]
        }
    },
    hindi: {
        samples: {
            pincode: ['560001', '400001', '110001'],
            mla_opinion: [
                'सड़क की मरम्मत बेहतर हुई है लेकिन अभी और स्ट्रीट लाइट्स की जरूरत है।',
                'MLA स्वास्थ्य शिविर की मांग पर तेजी से प्रतिक्रिया देते हैं।',
                'किसानों के लिए सिंचाई सहायता पर अधिक ध्यान देने की जरूरत है।'
            ],
            mp_opinion: [
                'MP ने हाल ही में नया जन औषधि केंद्र शुरू करने में मदद की है।',
                'हम चाहते हैं कि सांसद कार्यालय हमारे ब्लॉक का अधिक दौरा करे।',
                'रोजगार कार्यक्रमों के बेहतर कार्यान्वयन की आवश्यकता है।'
            ]
        }
    },
    telugu: {
        samples: {
            pincode: ['560001', '400001', '110001'],
            mla_opinion: [
                'రోడ్డు మరమ్మతులు మెరుగుపడ్డాయి కానీ ఇంకా వీధి లైట్లు కావాలి.',
                'గ్రామంలో ఆరోగ్య శిబిరం కోసం MLA స్పందించారు.',
                'రైతులకు నీటి పారుదల సహాయంపై మరింత దృష్టి పెట్టాలి.'
            ],
            mp_opinion: [
                'MP కొత్త జన ఔషధి కేంద్రాన్ని ఏర్పాటు చేయడంలో సహాయం చేశారు.',
                'మాకు MP కార్యాలయం మరిన్ని సందర్శనలు చేయాలని ఉంది.',
                'ఉద్యోగ కార్యక్రమాల అమలు మరింత బలోపేతం కావాలి.'
            ]
        }
    }
};

let appState = {
    mode: 'consent', // 'consent', 'survey', 'faq'
    surveyStep: 0,
    surveyData: {},
    language: 'english',
};

const addMessage = (text, sender) => {
    const bubble = document.createElement('div');
    bubble.classList.add('chat-bubble', sender);
    bubble.textContent = text;
    elements.chatLog.appendChild(bubble);
    elements.chatLog.scrollTop = elements.chatLog.scrollHeight;
};

const setInputEnabled = (enabled, placeholder = 'Type your message...') => {
    elements.chatInput.disabled = !enabled;
    elements.sendButton.disabled = !enabled;
    elements.chatInput.placeholder = placeholder;
    if (enabled) elements.chatInput.focus();
};

const startSurvey = () => {
    appState.mode = 'survey';
    elements.consentScreen.style.display = 'none';
    addMessage('Thank you for participating! I will ask a few questions. Your responses are anonymous.', 'bot');
    askNextSurveyQuestion();
};

const showSuggestionChips = (suggestions, clickHandler) => {
    elements.suggestionsBar.innerHTML = '';
    suggestions.forEach(text => {
        const chip = document.createElement('button');
        chip.classList.add('suggestion-chip');
        chip.textContent = text;
        chip.onclick = () => clickHandler(text);
        elements.suggestionsBar.appendChild(chip);
    });
};

const askNextSurveyQuestion = () => {
    elements.suggestionsBar.innerHTML = '';
    if (appState.surveyStep < SURVEY_QUESTIONS.length) {
        const question = SURVEY_QUESTIONS[appState.surveyStep];
        addMessage(question.text, 'bot');

        if (question.type === 'buttons') {
            setInputEnabled(false, 'Please select an option above');
            showSuggestionChips(question.options, (choice) => {
                addMessage(`Rating: ${choice}`, 'user');
                handleSurveyResponse(choice);
            });
        } else {
            setInputEnabled(true, LOCALIZED_TEXT[appState.language].textPlaceholder);
            elements.chatInput.type = question.type === 'textarea' ? 'text' : (question.type || 'text');
            if (question.pattern) elements.chatInput.pattern = question.pattern;
            const localizedSamples = LOCALIZED_SURVEYS[appState.language]?.samples?.[question.id] || question.samples;
            if (localizedSamples && localizedSamples.length) {
                showSuggestionChips(localizedSamples, (sample) => {
                    elements.chatInput.value = sample;
                    handleUserInput();
                });
            }
        }
    } else {
        endSurvey();
    }
};

const endSurvey = () => {
    addMessage(LOCALIZED_TEXT[appState.language].thankYou, 'bot');
    console.log('Final Survey Data:', appState.surveyData);
    renderSurveySummary();
    startFaqMode();
};

const startFaqMode = () => {
    appState.mode = 'faq';
    elements.consentScreen.style.display = 'none';
    if (Object.keys(appState.surveyData).length === 0) { // Only show if consent was 'no'
        addMessage(LOCALIZED_TEXT[appState.language].faqWelcome, 'bot');
    }
    setInputEnabled(true, LOCALIZED_TEXT[appState.language].questionPlaceholder);
    showFaqSuggestions();
};


const showFaqSuggestions = (suggestions) => {
    const defaultSuggestions = suggestions || LOCALIZED_FAQ_SUGGESTIONS[appState.language];
    showSuggestionChips(defaultSuggestions, (choice) => {
        elements.chatInput.value = choice;
        handleUserInput();
    });
};

const handleSurveyResponse = (response) => {
    const question = SURVEY_QUESTIONS[appState.surveyStep];
    appState.surveyData[question.id] = response;
    appState.surveyStep++;
    askNextSurveyQuestion();
};

const renderSurveySummary = () => {
    const summaryLines = [
        LOCALIZED_TEXT[appState.language].summaryIntro,
        `• ${translateLabel('pincode')}: ${appState.surveyData.pincode || '—'}`,
        `• ${translateLabel('mla_opinion')}: ${appState.surveyData.mla_opinion || '—'}`,
        `• ${translateLabel('mp_opinion')}: ${appState.surveyData.mp_opinion || '—'}`,
        `• ${translateLabel('satisfaction_score')}: ${appState.surveyData.satisfaction_score || '—'}`
    ];
    addMessage(summaryLines.join('\n'), 'bot');
};

const handleFaqQuery = async (query) => {
    try {
        const response = await fetch(`${API_BASE_URL}/api/v1/chat/ask`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ question: query, language: appState.language }),
        });
        if (!response.ok) throw new Error(`API Error: ${response.status}`);
        const data = await response.json();
        addMessage(data.response, 'bot');
        if (data.suggestions && data.suggestions.length > 0) {
            showFaqSuggestions(data.suggestions);
        } else {
            elements.suggestionsBar.innerHTML = '';
        }
    } catch (error) {
        console.error('FAQ query failed:', error);
        addMessage('Sorry, I am having trouble connecting to my services. Please try again later.', 'bot');
    }
};

const handleUserInput = () => {
    const userInput = elements.chatInput.value.trim();
    const currentQuestion = SURVEY_QUESTIONS[appState.surveyStep];

    // Only process input if it's not a button question or if there's text
    if (appState.mode === 'survey' && currentQuestion.type === 'buttons') {
        return; // Do nothing, wait for a button click
    }
    
    if (!userInput) return;

    addMessage(userInput, 'user');
    elements.chatInput.value = '';

    if (appState.mode === 'survey') {
        setInputEnabled(false);
        handleSurveyResponse(userInput);
    } else if (appState.mode === 'faq') {
        elements.suggestionsBar.innerHTML = ''; // Clear suggestions while waiting for response
        handleFaqQuery(userInput);
    }
};

// Event Listeners
elements.consentYes.addEventListener('click', startSurvey);
elements.consentNo.addEventListener('click', startFaqMode);
elements.chatForm.addEventListener('submit', (e) => {
    e.preventDefault();
    handleUserInput();
});

elements.languageSelect.addEventListener('change', (event) => {
    const selected = event.target.value;
    appState.language = selected;
    applyLocalizedText();
});

const applyLocalizedText = () => {
    const locale = LOCALIZED_TEXT[appState.language];
    elements.consentTitle.textContent = locale.consentTitle;
    elements.consentDescription.textContent = locale.consentDescription;
    elements.consentYesButton.textContent = locale.consentYes;
    elements.consentNoButton.textContent = locale.consentNo;
    addLocalizedConsentMessage();
};

const addLocalizedConsentMessage = () => {
    const intro = LOCALIZED_TEXT[appState.language].introMessage;
    const lastMessage = elements.chatLog.lastElementChild;
    if (!lastMessage || lastMessage.textContent !== intro) {
        addMessage(intro, 'bot');
    }
};

const translateLabel = (key) => {
    const labels = {
        english: {
            pincode: 'Pincode',
            mla_opinion: 'MLA opinion',
            mp_opinion: 'MP opinion',
            satisfaction_score: 'Overall rating'
        },
        hindi: {
            pincode: 'पिन कोड',
            mla_opinion: 'विधायक पर राय',
            mp_opinion: 'सांसद पर राय',
            satisfaction_score: 'कुल संतुष्टि'
        },
        telugu: {
            pincode: 'పిన్ కోడ్',
            mla_opinion: 'MLA అభిప్రాయం',
            mp_opinion: 'MP అభిప్రాయం',
            satisfaction_score: 'మొత్తం రేటింగ్'
        }
    };
    return labels[appState.language][key];
};

// Initial state
applyLocalizedText();
setInputEnabled(false, LOCALIZED_TEXT[appState.language].textPlaceholder);

