export const initialUserState = {
    theme: 'dark',
    completedExams: {}, // examId: completedCount
    solvedQuestions: {}, // questionId: { solved: true, correct: boolean, selectedOption: string, timeSpent: number }
    starredQuestions: {}, // questionId: boolean
    geminiApiKey: '' // default Gemini API Key
};

const STORAGE_KEY = "antigravity_study_state";

export function loadState() {
    const saved = localStorage.getItem(STORAGE_KEY);
    if (saved) {
        try {
            return { ...initialUserState, ...JSON.parse(saved) };
        } catch (e) {
            console.error("Error loading state:", e);
        }
    }
    return initialUserState;
}

export function saveState(state) {
    try {
        localStorage.setItem(STORAGE_KEY, JSON.stringify(state));
    } catch (e) {
        console.error("Error saving state:", e);
    }
}
