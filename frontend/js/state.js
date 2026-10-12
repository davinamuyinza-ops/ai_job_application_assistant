export const state = {
    session: null,
    resumeJson: null,
    pendingParsedResume: null,
    jobDescription: "",
    jobAnalysis: null,
    tailoredResume: null,
    personalMotivation: "",
    coverLetter: null,
    currentApplicationId: null,
    applications: [],
    promisingJobs: [],
    jobSectors: [],
    selectedJobSectors: [],
};

export function resetPipelineState() {
    state.pendingParsedResume = null;
    state.jobDescription = "";
    state.jobAnalysis = null;
    state.tailoredResume = null;
    state.personalMotivation = "";
    state.coverLetter = null;
    state.currentApplicationId = null;
    state.applications = [];
    state.promisingJobs = [];
    state.jobSectors = [];
    state.selectedJobSectors = [];
}
